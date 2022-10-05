#!/usr/bin/python

import sys
import os
import shutil
from optparse import OptionParser
import subprocess
import time

ENV = "KDE"  # Can be 'KDE' or 'GNOME'
DEVICEADDR = "9C:5A:81:F7:8C:5B" # bluetooth device address
CHECKINTERVAL = 1  # device pinged at this interval (seconds) when screen is unlocked
CHECKREPEAT = 2  # device must be unreachable this many times to lock
mode = 'unlocked'
minrssivalue = -1
# sudo btmgmt conn-info 9C:5A:81:F7:8C:5B alternatif method
if __name__ == "__main__":
    while True:
        tries = 0
        while tries < CHECKREPEAT:
            process = subprocess.Popen(['sudo', '/usr/bin/btmgmt','conn-info', DEVICEADDR], shell=False, stdout=subprocess.PIPE)
            process.wait()
            result = process.communicate()[0]
            rssiexists = 'RSSI' in result
            if rssiexists:
            	rssiindex = result.index('RSSI')
            	rssiresult = result[rssiindex+4:rssiindex+7].strip()
            	intrssiresult = int(rssiresult)
            else:
            	intrssiresult = minrssivalue - 1
            #print(rssiresult)
            #process = subprocess.Popen(['sudo', '/usr/bin/l2ping', DEVICEADDR, '-t', '1', '-c', '1'], shell=False, stdout=subprocess.PIPE)
            #process.wait()
            #if process.returncode == 0:
            if intrssiresult >= minrssivalue:
                #print("ping OK")
                break
            #print("ping response code: %d" % (process.returncode))
            time.sleep(1)
            tries = tries + 1

        if intrssiresult >= minrssivalue and mode == 'locked':
            mode = 'unlocked'
            if ENV == "KDE":
                subprocess.Popen(['loginctl', 'unlock-session'], shell=False, stdout=subprocess.PIPE)
            elif ENV == "GNOME":
                subprocess.Popen(['gnome-screensaver-command', '--deactivate'], shell=False, stdout=subprocess.PIPE)

        if intrssiresult < minrssivalue and mode == 'unlocked':
            mode = 'locked'
            if ENV == "KDE":
                subprocess.Popen(['loginctl', 'lock-session'], shell=False, stdout=subprocess.PIPE)
            elif ENV == "GNOME":
                subprocess.Popen(['gnome-screensaver-command', '--lock'], shell=False, stdout=subprocess.PIPE)
            
        if mode == 'locked':
            time.sleep(1)
        else:
            time.sleep(CHECKINTERVAL)
