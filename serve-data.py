import time
import prometheus_client
from prometheus_client import start_http_server, Info, Gauge

# TODO clean data when parsing (remove \n) and convert to proper type

def parse_csv():
    # parse partition data
    parts_csv = open("data/parts", "r").readlines()
    parts = []

    for row in parts_csv:
        parts.append(row.split(','))

    # parse disk data
    disks_csv = open("data/disks", "r").readlines()
    disks = []

    for row in disks_csv:
        disks.append(row.split(','))

    yield disks

    # add parent disk column to partition rows
    for part in parts:
        for disk in disks:
            if disk[0] in part[0]:
                part.append(disk[0])

    yield parts

def collect(disks, parts):
    disk_labels = ['block']
    disk_model = Info('disk_model', 'Disk Model Family', disk_labels)
    disk_power_on_hours = Gauge('disk_power_on_hours', 'Hours spent with disk powered', disk_labels)
    disk_power_cycle_count = Gauge('disk_power_cycle_count', 'Disk power cycle count', disk_labels)
    disk_raw_read_error_rate = Gauge('disk_raw_read_error_rate', 'Disk raw read error rate', disk_labels)
    disk_temperature = Gauge('disk_temperature', 'Disk temperature in Celsius', disk_labels)

    part_labels = ['block', 'disk']
    part_info = Info('partition', 'Partition metadata information', part_labels)
    part_usage_bytes = Gauge('partition_usage_bytes', 'Partition used size in bytes', part_labels)
    part_size_bytes = Gauge('partition_size_bytes', 'Partition total size in bytes', part_labels)

    # Disk metrics
    for disk in disks:
        disk_model.labels(block=disk[0]).info({
            'model_family': disk[1],
            'serial': disk[2],
            'rpm': disk[3]
        })
        disk_power_on_hours.labels(block=disk[0]).set(disk[4])
        disk_power_cycle_count.labels(block=disk[0]).set(disk[5])
        disk_raw_read_error_rate.labels(block=disk[0]).set(disk[6])
        disk_temperature.labels(block=disk[0]).set(disk[7])

    # Partition metrics
    for part in parts:
        part_info.labels(block=part[0], disk=part[5]).info({
            'mountpoint': part[1],
            'filesystem': part[2]
        })
        part_usage_bytes.labels(block=part[0], disk=part[5]).set(part[3])
        part_size_bytes.labels(block=part[0], disk=part[5]).set(part[4])

if __name__ == '__main__':
    disks, parts = parse_csv()
    collect(disks, parts)

    # disable default metrics
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

    start_http_server(3112)
    while True:
        time.sleep(1)
