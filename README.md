# todo
- custom http request handler so that script is called on get request (not timer)
- use systemd socket instead of generating one (which is created with root permissions)
- create sample systemd services with appropriate permissions

# partition data (csv)
block       (/dev/sda1),
mountpoint  (/),
filesystem  (ext4),
used bytes  (1231231232),
size bytes  (9999999999),
disk block  (/dev/sda)

# disk data (csv)
block           (/dev/sda),
model family    (Western Digital Blue),
serial number   (WD-W................),
rotation rate   (7200rpm)
power on hours  (11000),
power cycles    (2000),
raw read err r  (0),
temperature     (41)

# socket protocol
bytes   type            description
0-3     unsigned        disks data length        
4-7     unsigned        parts data length
8-X     utf-8           repr of disks data list
X+1-end utf-8           repr of parts data list

# links
https://stackoverflow.com/questions/38972736/how-to-print-lines-between-two-patterns-inclusive-or-exclusive-in-sed-awk-or
https://github.com/cloudandheat/prometheus_smart_exporter
