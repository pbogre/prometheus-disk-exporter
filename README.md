# prometheus-disk-exporter

A prometheus exporter for disk S.M.A.R.T. data and partition usage

## information

For security reasons, this script is *not* supposed to be ran with root
privileges. Instead, the only command which requires these privileges
(`smartctl`) is ran using `sudo` within `getter.sh`. For this reason
the installation step includes adding a sudoers configuration to run
this command without the need of a password for the specified user.

## installing

These steps assume that you are running with root privileges.

### Setup prometheus user

> Note: this step can be skipped if you already have a linux user 
> for exporting prometheus metrics, such as for prometheus-pve-exporter

1. Create linux user with no login
```
# useradd -s /bin/false prometheus
```

### Install package in virtual environment

1. Install the `venv` python module
```
# apt install python3-venv
```
2. Create the virtual environment in `/opt`
```
# python3 -m venv /opt/prometheus-disk-exporter
```
3. Activate the virtual environment
```
# source /opt/prometheus-disk-exporter/bin/activate
```
4. Install the pip package for prometheus-disk-exporter
```
(prometheus-disk-exporter) # pip install prometheus-disk-exporter
```
5. Disable the virtual environment
```
(prometheus-disk-exporter) # deactivate
```

### Setup sudoers and systemd configuration

1. Add sudoers configuration to run `smartctl` without password.
```
# echo "prometheus ALL=(ALL:ALL) NOPASSWD: $(which smartctl)" | tee -a /etc/sudoers.d/99-prometheus-disk-exporter
```
2. Create a systemd service `/etc/systemd/system/prometheus-disk-exporter.service` for this script.
   A sample can be found in the `systemd` folder of the repository.
3. Start and enable the systemd service.
```
# systemctl daemon-reload
# systemctl enable prometheus-disk-exporter.service
# systemctl start prometheus-disk-exporter.service
```
4. Verify that the installation was successful by visiting `0.0.0.0:9313`,
   or whatever address and port you specified in the command arguments

## arguments
```
usage: prometheus_disk_exporter [-h] [--listen-address LISTEN_ADDRESS]
                                [--listen-port LISTEN_PORT]

options:
  -h, --help            show this help message and exit
  --listen-address LISTEN_ADDRESS, -l LISTEN_ADDRESS
                        Address for HTTP server to listen on
  --listen-port LISTEN_PORT, -p LISTEN_PORT
                        Port for HTTP server to listen on
```

* **listen-address:** Address for HTTP server to listen on (string) (Default: '0.0.0.0')
* **listen-port:** Port for HTTP server to listen on (int) (Default: 9313)


## metrics sample

```
# HELP disk_getter_error Indicates an internal error while getting data from shell script
# TYPE disk_getter_error gauge
disk_getter_error{type="None"} 0.0
# HELP disk_model_info Disk Model Family
# TYPE disk_model_info gauge
disk_model_info{disk_serial="WD-WCC6Y3TVHSKJ",model_family="Western Digital Blue",rpm="7200 rpm"} 1.0
disk_model_info{disk_serial="50026B76821954FF",model_family="Kingston SSDNow UV400/500",rpm="Solid State Device"} 1.0
# HELP disk_power_on_hours Hours spent with disk powered
# TYPE disk_power_on_hours gauge
disk_power_on_hours{disk_serial="WD-WCC6Y3TVHSKJ"} 11583.0
disk_power_on_hours{disk_serial="50026B76821954FF"} 11583.0
# HELP disk_power_cycle_count Disk power cycle count
# TYPE disk_power_cycle_count gauge
disk_power_cycle_count{disk_serial="WD-WCC6Y3TVHSKJ"} 2055.0
disk_power_cycle_count{disk_serial="50026B76821954FF"} 2032.0
# HELP disk_raw_read_error_rate Disk raw read error rate
# TYPE disk_raw_read_error_rate gauge
disk_raw_read_error_rate{disk_serial="WD-WCC6Y3TVHSKJ"} 0.0
disk_raw_read_error_rate{disk_serial="50026B76821954FF"} 2.476152e+06
# HELP disk_temperature Disk temperature in Celsius
# TYPE disk_temperature gauge
disk_temperature{disk_serial="WD-WCC6Y3TVHSKJ"} 41.0
disk_temperature{disk_serial="50026B76821954FF"} 42.0
# HELP partition_info Partition metadata information
# TYPE partition_info gauge
partition_info{block="/dev/sda1",disk_serial="WD-WCC6Y3TVHSKJ",filesystem="ext4",mountpoint="/media"} 1.0
partition_info{block="/dev/sdb1",disk_serial="50026B76821954FF",filesystem="vfat",mountpoint="/boot/efi"} 1.0
partition_info{block="/dev/sdb2",disk_serial="50026B76821954FF",filesystem="ext4",mountpoint="/"} 1.0
# HELP partition_usage_bytes Partition used size in bytes
# TYPE partition_usage_bytes gauge
partition_usage_bytes{block="/dev/sda1",disk_serial="WD-WCC6Y3TVHSKJ"} 1.33785550848e+011
partition_usage_bytes{block="/dev/sdb1",disk_serial="50026B76821954FF"} 303104.0
partition_usage_bytes{block="/dev/sdb2",disk_serial="50026B76821954FF"} 2.4086495232e+010
# HELP partition_size_bytes Partition total size in bytes
# TYPE partition_size_bytes gauge
partition_size_bytes{block="/dev/sda1",disk_serial="WD-WCC6Y3TVHSKJ"} 9.83349346304e+011
partition_size_bytes{block="/dev/sdb1",disk_serial="50026B76821954FF"} 3.13929728e+08
partition_size_bytes{block="/dev/sdb2",disk_serial="50026B76821954FF"} 1.17236166656e+011
```

## credits
- [prometheus_smart_exporter](https://github.com/cloudandheat/prometheus_smart_exporter).
  if all you are looking for is a SMART data exporter, i highly recommend their
  implementation
- [proxmox prometheus metrics](https://community.hetzner.com/tutorials/proxmox-prometheus-metrics),
  for helping me figure out how to properly install the package
