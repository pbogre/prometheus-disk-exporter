# prometheus-disk-exporter

A prometheus exporter for disk S.M.A.R.T. data and partition usage

## information

For safety reasons (inspired by @cloudandheat 's similar project),
this program is composed of two main parts: the getter and the exporter.
The getter script *gets* the information using `lsblk` and `smartctl`, and
then serves it on a UNIX socket. The exporter receives information from 
this socket, parses it, and *serves* it as prometheus metrics with an http
server (by default on port `9313`).

This is done so that you only have to run the getter script as sudo, as
it requires root privileges to gather the data from the system, while the 
http server is safely ran at a lower permission level. Additionally the 
socket is in read-only mode by default.

This project was heavily inspired by another similar project which you
can have a look at from the credits section of this readme.

## structure

### partition data from socket (csv)
|column |value       |example
|-------|------------|-------
|0      |block       |`/dev/sda1`,
|1      |mountpoint  |`/`,
|2      |filesystem  |`ext4`,
|3      |used bytes  |`1231231232`,
|4      |size bytes  |`9999999999`,
|5      |disk serial |`WD-W...........`

### disk data from socket (csv)
|column | value              |example
|-------|--------------------|-----------------
|0      |serial number       |`WD-W................`,
|1      |model family        |`Western Digital Blue`,
|2      |rotation rate       |`7200rpm`
|3      |power on hours      |`11000`,
|4      |power cycles        |`2000`,
|5      |raw read error rate |`0`,
|6      |temperature         |`41`

### socket protocol
|bytes  |type           |description
|-------|---------------|-----------------
|0-3    |unsigned       |disks data length        
|4-7    |unsigned       |parts data length
|8-X    |utf-8          |repr of disk data csv
|X+1-end|utf-8          |repr of part data csv

# credits
this project is largely inspired from @cloudandheat 's 
[https://github.com/cloudandheat/prometheus_smart_exporter](prometheus_smart_exporter).
if all you are looking for is a SMART data exporter, i highly recommend their 
implementation.
