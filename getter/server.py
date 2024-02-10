import os
import subprocess
import socket
import argparse

def get_data(script_path) -> tuple[list[str], list[str]]:
    """
    Run getter bash script and parse the data.
    Returns lists of disks and partition data respectively.
    """
    output = subprocess.check_output([script_path]).decode()
    disk_data, part_data = output.split("\nDISK DATA END\n", 1) 

    # parse disk_data
    disks = []
    for row in disk_data.split('\n'):
        disks.append(row.split(','))

    # parse partition_data
    parts = []
    for row in part_data.split('\n'):
        parts.append(row.split(','))
        # find & add partition disk (serial number)
        for disk in disks:
            if disk[0] in parts[-1][0]:
                parts[-1].append(disk[1])

    # cleanup
    for disk in disks:
        disk.pop(0)

    parts.pop()

    return disks, parts

# serve unix socket

parser = argparse.ArgumentParser()
parser.add_argument(
        "--socket-path", 
        default="/tmp/prometheus-disk-exporter.sock",
        help="Asbolute path of the UNIX socket to serve to"
        )

parser.add_argument(
        "--socket-owner", "-o", 
        default=None,
        help="User and group (should have same name) to set as owner \
              of socket file through chown. If not set, socket will have \
              read and write permissions for all users."
        )

args = parser.parse_args()

socket_path = args.socket_path
script_path = os.path.join(os.path.dirname(__file__), "getter.sh")

if os.path.exists(socket_path):
    # should always work as this program runs with privileges
    os.remove(socket_path) 

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.bind(socket_path)

    if args.socket_owner is None:
        os.chmod(socket_path, 0o666)
    else:
        import shutil
        shutil.chown(socket_path, args.socket_owner, args.socket_owner)
        os.chmod(socket_path, 0o600)

    s.listen(1)

    while True:
        conn, addr = s.accept()
        conn.shutdown(socket.SHUT_RD)
        with conn:
            print("new connection")

            disks, parts = get_data(script_path)

            disks_packet = repr(disks).encode('utf-8')
            parts_packet = repr(parts).encode('utf-8')

            disks_packet_size = len(disks_packet).to_bytes(4)
            parts_packet_size = len(parts_packet).to_bytes(4)

            conn.sendall(disks_packet_size)
            conn.sendall(parts_packet_size)
            conn.sendall(disks_packet)
            conn.sendall(parts_packet)

        print("data sent")
