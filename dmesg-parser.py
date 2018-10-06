#!/usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import argparse
import os
import re

class DmesgFile(object):
    release = None
    memory = None
    cpu = None
    freq = None
    ncpu = None
    drivers = set([])

    RELEASE_RE = re.compile(r'^(FreeBSD \d+.\d+.*) #\d+.*$')
    MEMORY_RE = re.compile(r'^real memory\s+=\s+(\d+).*$')
    CPU_RE = re.compile(r'^CPU: (.*)$')
    # This works only for x86 systems
    # ARM has less defined format for CPU models
    FREQ_RE = re.compile(r'\((\d+\.\d+)-MHz')
    DEVICE_RE = re.compile(r'(\w+)\d+: .* on \w+$')
    NCPU_RE = re.compile('FreeBSD/SMP: Multiprocessor System Detected: (\d+) CPUs')

    def __init__(self, path):
        self.__path = path
        self.__parse()

    def __repr__(self):
        return 'Dmesg({}, {}, {})'.format(self.release, self.cpu, self.memory)

    def __parse(self):
        dmesg_data = None
        with open(self.__path, 'r') as f:
            dmesg_data = f.read()
        lines = dmesg_data.split('\n')
        for line in lines:
            if self.release is None:
                match = self.RELEASE_RE.match(line)
                if match:
                    self.release = match.group(1)
                    continue
            if self.memory is None:
                match = self.MEMORY_RE.match(line)
                if match:
                    self.memory = int(match.group(1))
                    continue
            if self.cpu is None:
                match = self.CPU_RE.match(line)
                if match:
                    self.cpu = match.group(1)
                    freq_match = self.FREQ_RE.search(self.cpu)
                    if freq_match:
                        self.freq = freq_match.group(1)
                    continue
            if self.ncpu is None:
                match = self.NCPU_RE.match(line)
                if match:
                    self.ncpu = match.group(1)
                    continue

            match = self.DEVICE_RE.match(line)
            if match:
                driver = match.group(1)
                self.drivers.add(driver)



parser = argparse.ArgumentParser()
parser.add_argument('datadir', type=str, help='directory with dmesg files')
args = parser.parse_args()

dmesgs = []
for path in os.listdir(args.datadir):

    # Ignore hidden files
    if path.startswith('.'):
        continue

    full_path = os.path.join(args.datadir, path)

    # Ignore everythin taht is not regular file
    if not (os.path.isfile(full_path)):
        continue

    dmesg = DmesgFile(full_path)
    dmesgs.append(dmesg)

print (dmesgs)
