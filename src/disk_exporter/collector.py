import logging
import subprocess
import os
from prometheus_client.metrics_core import GaugeMetricFamily, InfoMetricFamily
from prometheus_client.registry import Collector

class DiskCollector(Collector):
    def __init__(self):
        self.script_path = os.path.join(os.path.dirname(__file__), "getter.sh")

    def get_data(self):
        output = subprocess.check_output([self.script_path]).decode()
        disk_csv, part_csv = output.split("\nDISK DATA END\n")

        # parse disk data
        disks = []
        for row in disk_csv.split('\n'):
            disks.append(row.split(','))

        # parse partition data
        parts = []
        for row in part_csv.split('\n'):
            if not row:
                continue

            parts.append(row.split(','))
            # remove index 1 ("part")
            parts[-1].pop(1)
            # find & add partition disk serial number
            for disk in disks:
                if disk[0] in parts[-1][0]:
                    parts[-1].append(disk[1])

        # remove block column from disks
        for disk in disks:
            disk.pop(0)

        return disks, parts

    def collect(self):
        logging.info(f"Began data collection")

        # first check if running shell script 
        # gives no errors
        disk_getter_error = GaugeMetricFamily(
                'disk_getter_error',
                'Indicates an internal error while getting data from shell script',
                labels=['type']
                )

        logging.info(f"Running shell script to get data...")
        try:
            self.disks, self.parts = self.get_data()
        except Exception as e:
            logging.error(f"Exception occured while running shell script ({e.__class__.__name__})")
            disk_getter_error.add_metric([e.__class__.__name__], 1)
            yield disk_getter_error
            return

        disk_getter_error.add_metric(['None'], 0)
        yield disk_getter_error

        # if there are no errors, proceed
        # with the rest of the metrics
        logging.info(f"Gathering metrics...")

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
            if disk[3]:
                disk_power_on_hours.add_metric([disk[0]], disk[3])
            if disk[4]:
                disk_power_cycle_count.add_metric([disk[0]], disk[4])
            if disk[5]:
                disk_raw_read_error_rate.add_metric([disk[0]], disk[5])
            if disk[6]:
                disk_temperature.add_metric([disk[0]], disk[6])

        yield disk_model
        yield disk_power_on_hours
        yield disk_power_cycle_count
        yield disk_raw_read_error_rate
        yield disk_temperature

        # Partition metrics
        for part in self.parts:
            part_info.add_metric([part[0], part[5]], {
                'mountpoint': part[4],
                'filesystem': part[1]
            })
            if part[2]:
                part_usage_bytes.add_metric([part[0], part[5]], part[2])
            if part[3]:
                part_size_bytes.add_metric([part[0], part[5]], part[3])

        yield part_info
        yield part_usage_bytes
        yield part_size_bytes

        logging.info(f"Collection process ended")
