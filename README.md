# todo
- make `server.py` be able to find `getter.sh` regardless of directory it is executed from
- use systemd socket instead of generating one (which is created with root permissions)
    - or manually set permissions from within the script (chmod 664 socket\_path)
- ability to pass arguments such as socket path, exporter ip/port, ...
- use a better system to generate metrics; instead of manually declaring each one have a separate file 
  which describes their format like name, labels, help, value col, etc., and iterate through the metrics
  in that file to generate them
- create sample systemd services with appropriate permissions
- proper logging

# partition data (csv)
|column |value       |example
|-------|------------|-------
|0      |block       |`/dev/sda1`,
|1      |mountpoint  |`/`,
|2      |filesystem  |`ext4`,
|3      |used bytes  |`1231231232`,
|4      |size bytes  |`9999999999`,
|5      |disk block  |`/dev/sda`

# disk data (csv)
|column | value              |example
|-------|--------------------|-----------------
|0      |block               |`/dev/sda`,
|1      |model family        |`Western Digital Blue`,
|2      |serial number       |`WD-W................`,
|3      |rotation rate       |`7200rpm`
|4      |power on hours      |`11000`,
|5      |power cycles        |`2000`,
|6      |raw read error rate |`0`,
|7      |temperature         |`41`

# socket protocol
|bytes  |type           |description
|-------|---------------|-----------------
|0-3    |unsigned       |disks data length        
|4-7    |unsigned       |parts data length
|8-X    |utf-8          |repr of disks data list
|X+1-end|utf-8          |repr of parts data list

# links
- https://github.com/cloudandheat/prometheus_smart_exporter
