#!/bin/bash

# TODO make smart regex into 2 functions to avoid repetition
# TODO run python script as non-root (otherwise socket will require root)
# TODO use script path to execute socket.py, as currently it won't find it 
#      unless you run this script from the same folder

lsblk=$(lsblk -o TYPE,FSTYPE,FSUSED,FSSIZE,MOUNTPOINT,NAME,NAME -b)

disk_blks=$( echo "$lsblk" | awk '$1=="disk" {print "/dev/"$2}')
for i in $disk_blks;
do
    smart=$(smartctl -iA $i)

    model_family=$(echo "$smart" | grep "Model Family:" | sed 's/^Model Family:\s*\(\S.*\)$/\1/g')
    serial_number=$(echo "$smart" | grep "Serial Number:" | sed 's/^Serial Number:\s*\(\S.*\)$/\1/g')
    rotation_rate=$(echo "$smart" | grep "Rotation Rate:" | sed 's/^Rotation Rate:\s*\(\S.*\)$/\1/g')

    smart_attributes=$(echo "$smart" | awk '/ID#\s*ATTRIBUTE_NAME\s*/{flag=1} /SMART Error Log Version:/{flag=0} flag')

    power_on_hours=$(echo "$smart" | awk '$2=="Power_On_Hours" {print $10}')
    power_cycle_count=$(echo "$smart" | awk '$2=="Power_Cycle_Count" {print $10}')
    raw_read_error_rate=$(echo "$smart" | awk '$2=="Raw_Read_Error_Rate" {print $10}')
    temperature=$(echo "$smart" | awk '$2=="Temperature_Celsius" {print $10}')
   
    echo $i,$model_family,$serial_number,$rotation_rate,$power_on_hours,$power_cycle_count,$raw_read_error_rate,$temperature
done
echo "DISK DATA END"

echo "$lsblk" | awk '$1=="part" {print "/dev/"$7","$5","$2","$3","$4}'
