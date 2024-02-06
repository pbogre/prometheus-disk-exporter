import os
import socket

# TODO get new data on sock connection

# parse disk data
disk_blks = os.environ["disk_blks"].split('\n')

disks = []
for blk in disk_blks:
    disk_csv = os.environ[blk + "_info"]
    disks.append(disk_csv.split(','))

# parse partition data
parts_csv = os.environ["parts_info"].split('\n')
parts = []

for row in parts_csv:
    parts.append(row.split(','))
    # find & add partition disk
    for disk in disks:
        if disk[0] in parts[-1][0]:
            parts[-1].append(disk[0])

# setup unix socket
socket_path = "/tmp/prometheus-disk-exporter.sock"

try:
    os.unlink(socket_path)
except OSError:
    if os.path.exists(socket_path):
        raise

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.bind(socket_path)
    s.listen(1)

    while True:
        conn, addr = s.accept()
        conn.shutdown(socket.SHUT_RD)
        with conn:
            print("new connection")

            disks_packet = repr(disks).encode('utf-8')
            parts_packet = repr(parts).encode('utf-8')

            disks_packet_size = len(disks_packet).to_bytes(4)
            parts_packet_size = len(parts_packet).to_bytes(4)

            conn.sendall(disks_packet_size)
            conn.sendall(parts_packet_size)
            conn.sendall(disks_packet)
            conn.sendall(parts_packet)

        print("data sent")
