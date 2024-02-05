import http.server
import prometheus_client

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

# add parent disk column to partition rows

for part in parts:
    for disk in disks:
        if disk[0] in part[0]:
            part.append(disk[0])

httpd = http.server.HTTPServer(("localhost", 3000), prometheus_client.exposition.MetricsHandler)
