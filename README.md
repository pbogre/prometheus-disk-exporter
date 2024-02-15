# prometheus-disk-exporter

A prometheus exporter for disk S.M.A.R.T. data and partition usage

## information

For security reasons, this script is *not* supposed to be ran with root
privileges. Instead, the only command which requires these privileges
(`smartctl`) is ran using `sudo` within `getter.sh`. For this reason
the installation step includes adding a sudoers configuration to run
this command without the need of a password for the specified user.

## installation

1. TODO
2. Add sudoers configuration to run `smartctl` without password. 
   Make sure to change `prometheus` to whatever user is set to run
   the service with systemd
```sh
echo 'prometheus ALL=(ALL:ALL) NOPASSWD: /usr/bin/smartctl' | sudo tee -a /etc/sudoers.d/99-prometheus-disk-exporter
```
3. TODO

## arguments

TODO

## data structure

### partition data (csv)
|column |value       |example
|-------|------------|-------
|0      |block       |`/dev/sda1`,
|1      |mountpoint  |`/`,
|2      |filesystem  |`ext4`,
|3      |used bytes  |`1231231232`,
|4      |size bytes  |`9999999999`,
|5      |disk serial |`WD-W...........`

### disk data (csv)
|column | value              |example
|-------|--------------------|-----------------
|0      |block               |`/dev/sda`,
|1      |serial number       |`WD-W................`,
|2      |model family        |`Western Digital Blue`,
|3      |rotation rate       |`7200rpm`
|4      |power on hours      |`11000`,
|5      |power cycles        |`2000`,
|6      |raw read error rate |`0`,
|7      |temperature         |`41`

# credits
- [https://github.com/cloudandheat/prometheus_smart_exporter](prometheus_smart_exporter). 
  (if all you are looking for is a SMART data exporter, i highly recommend their 
  implementation)
