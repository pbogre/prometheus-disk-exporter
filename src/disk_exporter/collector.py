import socket
import logging
from prometheus_client.metrics_core import GaugeMetricFamily, InfoMetricFamily
from prometheus_client.registry import Collector

def connect_socket(socket_path) -> socket.socket:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)

    return sock

def receive_packets(sock: socket.socket):
    disks_packet_size = int.from_bytes(sock.recv(4))
    parts_packet_size = int.from_bytes(sock.recv(4))

    disks = eval(sock.recv(disks_packet_size))
    parts = eval(sock.recv(parts_packet_size))

    return disks, parts

class DiskCollector(Collector):
    def __init__(self, socket_path):
        self.socket_path = socket_path

    def collect(self):
        logging.info(f"Began data collection")
        # first check if the getter socket works
        disk_getter_error = GaugeMetricFamily(
                'disk_getter_error',
                'Indicates an error with getter socket (connection/retrieving)',
                labels=['type']
                )

        # we reconnect on each collection because 
        # that's how the server knows when to serve
        logging.info(f"Connecting to socket and retrieving data...")
        try:
            self.sock = connect_socket(self.socket_path)
            self.disks, self.parts = receive_packets(self.sock)
        except Exception as e:
            logging.error(f"Exception occured while connecting to or retrieving from socket ({e.__class__.__name__})")
            disk_getter_error.add_metric([e.__class__.__name__], 1)
            yield disk_getter_error
            return

        disk_getter_error.add_metric(['None'], 0)
        yield disk_getter_error

        logging.info(f"Gathering metrics...")

        # if socket works, proceed with metrics
        disk_labels = ['disk_serial']
        disk_model = InfoMetricFamily('disk_model', 'Disk Model Family', labels=disk_labels)
        disk_power_on_hours = GaugeMetricFamily('disk_power_on_hours', 'Hours spent with disk powered', labels=disk_labels)
        disk_power_cycle_count = GaugeMetricFamily('disk_power_cycle_count', 'Disk power cycle count', labels=disk_labels)
        disk_raw_read_error_rate = GaugeMetricFamily('disk_raw_read_error_rate', 'Disk raw read error rate', labels=disk_labels)
        disk_temperature = GaugeMetricFamily('disk_temperature', 'Disk temperature in Celsius', labels=disk_labels)

        part_labels = ['block', 'disk_serial']
        part_info = InfoMetricFamily('partition', 'Partition metadata information', labels=part_labels)
        part_usage_bytes = GaugeMetricFamily('partition_usage_bytes', 'Partition used size in bytes', labels=part_labels)
        part_size_bytes = GaugeMetricFamily('partition_size_bytes', 'Partition total size in bytes', labels=part_labels)

        # Disk metrics
        for disk in self.disks:
            disk_model.add_metric([disk[0]], {
                'model_family': disk[1],
                'rpm': disk[2]
            })
            disk_power_on_hours.add_metric([disk[0]], disk[3])
            disk_power_cycle_count.add_metric([disk[0]], disk[4])
            disk_raw_read_error_rate.add_metric([disk[0]], disk[5])
            disk_temperature.add_metric([disk[0]], disk[6])

        yield disk_model
        yield disk_power_on_hours
        yield disk_power_cycle_count
        yield disk_raw_read_error_rate
        yield disk_temperature

        # Partition metrics
        for part in self.parts:
            part_info.add_metric([part[0], part[5]], {
                'mountpoint': part[1],
                'filesystem': part[2]
            })
            part_usage_bytes.add_metric([part[0], part[5]], part[3])
            part_size_bytes.add_metric([part[0], part[5]], part[4])

        yield part_info
        yield part_usage_bytes
        yield part_size_bytes

        self.sock.close()

        logging.info(f"Collection process ended")
