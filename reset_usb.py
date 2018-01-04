#!/usr/bin/env python
import os
import sys
from subprocess import Popen, PIPE
import fcntl

instructions = '''
Usage: python reset_usb.py help : Show this help
       sudo python reset_usb.py list : List all devices
       sudo python reset_usb.py path /dev/bus/usb/XXX/YYY : Reset device using path /dev/bus/usb/XXX/YYY
       sudo python reset_usb.py search "search terms" : Search for device using the search terms within the search string returned by list and reset matching device'''

if len(sys.argv) < 2:
    print(instructions)
    sys.exit(0)

option = sys.argv[1].lower()
if 'help' in option:
    print(instructions)
    sys.exit(0)


def create_device_list():
    device_list = list()
    try:
        lsusb_out = Popen('lsusb -v', shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True).stdout.read().strip().decode('utf-8')
        devices = lsusb_out.split('%s%s' % (os.linesep, os.linesep))
        for device_categories in devices:
            if not device_categories:
                continue
            categories = device_categories.split(os.linesep)
            device_stuff = categories[0].strip().split()
            bus = device_stuff[1]
            device = device_stuff[3][:-1]
            device_dict = {'bus': bus, 'device': device}
            device_info = ' '.join(device_stuff[6:])
            device_dict['description'] = device_info
            for category in categories:
                if not category:
                    continue
                categoryinfo = category.strip().split()
                if categoryinfo[0] == 'iManufacturer':
                    manufacturer_info = ' '.join(categoryinfo[2:])
                    device_dict['manufacturer'] = manufacturer_info
                if categoryinfo[0] == 'iProduct':
                    product_info = ' '.join(categoryinfo[2:])
                    device_dict['product'] = product_info
            device_list.append(device_dict)
    except Exception as ex:
        print('Failed to list devices! Error: %s' % ex)
        sys.exit(-1)
    return device_list


if 'list' in option:
    device_list = create_device_list()
    for device in device_list:
        path = '/dev/bus/usb/%s/%s' % (device['bus'], device['device'])
        print('path=%s' % path)
        print('    description=%s' % device['description'])
        print('    manufacturer=%s' % device['manufacturer'])
        print('    product=%s' % device['product'])
        print('    search string=%s %s %s' % (device['description'], device['manufacturer'], device['product']))
    sys.exit(0)

if len(sys.argv) < 3:
    print(instructions)
    sys.exit(0)

option2 = sys.argv[2]

print('Resetting device: %s' % option2)
USBDEVFS_RESET = 21780


def reset_usb(dev_path):
    try:
        f = open(dev_path, 'w', os.O_WRONLY)
        fcntl.ioctl(f, USBDEVFS_RESET, 0)
        print('Successfully reset %s' % dev_path)
        sys.exit(0)
    except Exception as ex:
        print('Failed to reset device! Error: %s' % ex)
        sys.exit(-1)


if 'path' in option:
    reset_usb(option2)


if 'search' in option:
    device_list = create_device_list()
    for device in device_list:
        text = '%s %s %s' % (device['description'], device['manufacturer'], device['product'])
        if option2 in text:
            path = '/dev/bus/usb/%s/%s' % (device['bus'], device['device'])
            reset_usb(path)
    print('Failed to find device!')
    sys.exit(-1)
