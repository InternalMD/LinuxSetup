#!/bin/sh
for mapped_drive in $(find /dev/mapper/ -mindepth 1 -not -path /dev/mapper/control); do
    echo "Veracrypt \"$(basename "$mapped_drive")\" drive is unlocked"
done
