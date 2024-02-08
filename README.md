# todo
- ability to pass arguments
    - getter   | socket path
    - exporter | listen address, listen port, (min delay between requests)
- create sample systemd services with appropriate permissions
    - socket   |  prometheus:prometheus, read+write 0 0
    - getter   |  root:root
    - exporter |  prometheus:prometheus
- limit http requests on exporter (or on getter?) (+ argument)
- proper logging
- use a better system to generate metrics; instead of manually declaring each one have a separate file 
  which describes their format like name, labels, help, value col, etc., and iterate through the metrics
  in that file to generate them

# partition data from socket (csv)
|column |value       |example
|-------|------------|-------
|0      |block       |`/dev/sda1`,
|1      |mountpoint  |`/`,
|2      |filesystem  |`ext4`,
|3      |used bytes  |`1231231232`,
|4      |size bytes  |`9999999999`,
|5      |disk serial |`WD-W...........`

# disk data from socket (csv)
|column | value              |example
|-------|--------------------|-----------------
|0      |serial number       |`WD-W................`,
|1      |model family        |`Western Digital Blue`,
|2      |rotation rate       |`7200rpm`
|3      |power on hours      |`11000`,
|4      |power cycles        |`2000`,
|5      |raw read error rate |`0`,
|6      |temperature         |`41`

# socket protocol
|bytes  |type           |description
|-------|---------------|-----------------
|0-3    |unsigned       |disks data length        
|4-7    |unsigned       |parts data length
|8-X    |utf-8          |repr of disk data csv
|X+1-end|utf-8          |repr of part data csv

# links
- https://github.com/cloudandheat/prometheus_smart_exporter
