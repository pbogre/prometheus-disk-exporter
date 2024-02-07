import socket
from http.server import HTTPServer
from prometheus_client import MetricsHandler, REGISTRY, GC_COLLECTOR, PROCESS_COLLECTOR, PLATFORM_COLLECTOR
from prometheus_client.metrics_core import GaugeMetricFamily, InfoMetricFamily
from prometheus_client.registry import Collector

def connect_socket(socket_path) -> socket.socket:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    print("connecting to UNIX socket at " + socket_path)
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
        # define metrics
        disk_labels = ['block']
        disk_model = InfoMetricFamily('disk_model', 'Disk Model Family', labels=disk_labels)
        disk_power_on_hours = GaugeMetricFamily('disk_power_on_hours', 'Hours spent with disk powered', labels=disk_labels)
        disk_power_cycle_count = GaugeMetricFamily('disk_power_cycle_count', 'Disk power cycle count', labels=disk_labels)
        disk_raw_read_error_rate = GaugeMetricFamily('disk_raw_read_error_rate', 'Disk raw read error rate', labels=disk_labels)
        disk_temperature = GaugeMetricFamily('disk_temperature', 'Disk temperature in Celsius', labels=disk_labels)

        part_labels = ['block', 'disk']
        part_info = InfoMetricFamily('partition', 'Partition metadata information', labels=part_labels)
        part_usage_bytes = GaugeMetricFamily('partition_usage_bytes', 'Partition used size in bytes', labels=part_labels)
        part_size_bytes = GaugeMetricFamily('partition_size_bytes', 'Partition total size in bytes', labels=part_labels)

        # we reconnect on each collection because 
        # that's how the server knows when to serve
        sock = connect_socket(self.socket_path)
        disks, parts = receive_packets(sock)

        # Disk metrics
        for disk in disks:
            disk_model.add_metric(labels=[disk[0]], value={
                'model_family': disk[1],
                'serial': disk[2],
                'rpm': disk[3]
            })
            disk_power_on_hours.add_metric(labels=[disk[0]], value=disk[4])
            disk_power_cycle_count.add_metric(labels=[disk[0]], value=disk[5])
            disk_raw_read_error_rate.add_metric(labels=[disk[0]], value=disk[6])
            disk_temperature.add_metric(labels=[disk[0]], value=disk[7])

        yield disk_model
        yield disk_power_on_hours
        yield disk_power_cycle_count
        yield disk_raw_read_error_rate
        yield disk_temperature

        # Partition metrics
        for part in parts:
            part_info.add_metric(labels=[part[0], part[5]], value={
                'mountpoint': part[1],
                'filesystem': part[2]
            })
            part_usage_bytes.add_metric(labels=[part[0], part[5]], value=part[3])
            part_size_bytes.add_metric(labels=[part[0], part[5]], value=part[4])

        yield part_info
        yield part_usage_bytes
        yield part_size_bytes

        sock.close()

if __name__ == '__main__':
    socket_path = "/tmp/prometheus-disk-exporter.sock"
    REGISTRY.register(DiskCollector(socket_path))

    # disable default metrics
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.unregister(PROCESS_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)

    HTTPServer(('127.0.0.1', 9313), MetricsHandler).serve_forever()
