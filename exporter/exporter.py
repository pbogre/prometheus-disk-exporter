import time
import socket
import prometheus_client
from prometheus_client import start_http_server, Info, Gauge

def connect_socket(socket_path) -> socket.socket:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    print("connecting to UNIX socket at " + socket_path)
    s.connect(socket_path)

    return s

def receive_packets(s: socket.socket):
    disks_packet_size = int.from_bytes(s.recv(4))
    parts_packet_size = int.from_bytes(s.recv(4))

    disks = eval(s.recv(disks_packet_size))
    parts = eval(s.recv(parts_packet_size))

    return disks, parts

class Collector:
    def __init__(self):
        disk_labels = ['block']
        self.disk_model = Info('disk_model', 'Disk Model Family', disk_labels)
        self.disk_power_on_hours = Gauge('disk_power_on_hours', 'Hours spent with disk powered', disk_labels)
        self.disk_power_cycle_count = Gauge('disk_power_cycle_count', 'Disk power cycle count', disk_labels)
        self.disk_raw_read_error_rate = Gauge('disk_raw_read_error_rate', 'Disk raw read error rate', disk_labels)
        self.disk_temperature = Gauge('disk_temperature', 'Disk temperature in Celsius', disk_labels)

        part_labels = ['block', 'disk']
        self.part_info = Info('partition', 'Partition metadata information', part_labels)
        self.part_usage_bytes = Gauge('partition_usage_bytes', 'Partition used size in bytes', part_labels)
        self.part_size_bytes = Gauge('partition_size_bytes', 'Partition total size in bytes', part_labels)

    def collect(self, disks, parts):    
        # Disk metrics
        for disk in disks:
            self.disk_model.labels(block=disk[0]).info({
                'model_family': disk[1],
                'serial': disk[2],
                'rpm': disk[3]
            })
            self.disk_power_on_hours.labels(block=disk[0]).set(disk[4])
            self.disk_power_cycle_count.labels(block=disk[0]).set(disk[5])
            self.disk_raw_read_error_rate.labels(block=disk[0]).set(disk[6])
            self.disk_temperature.labels(block=disk[0]).set(disk[7])

        # Partition metrics
        for part in parts:
            self.part_info.labels(block=part[0], disk=part[5]).info({
                'mountpoint': part[1],
                'filesystem': part[2]
            })
            self.part_usage_bytes.labels(block=part[0], disk=part[5]).set(part[3])
            self.part_size_bytes.labels(block=part[0], disk=part[5]).set(part[4])

if __name__ == '__main__':
    s = connect_socket("/tmp/prometheus-disk-exporter.sock")
    disks, parts = receive_packets(s)

    print(disks)
    print(parts)

    exit(0)

    collector = Collector()

    # disable default metrics
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

    #start_http_server(3112)
    # instead of a timed loop this should happen on each get request
    #while True:
    #    time.sleep(5)
    #    collector.collect(disks, parts)
