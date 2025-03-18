import time
import os
import json
import urllib3
import sys
from pathlib import Path
from threading import Thread
from datetime import datetime
from subprocess import run, check_output, Popen, PIPE, STDOUT
from io import StringIO
import timeit
import argparse
import platform
import re
import json

import psutil

def get_file_info(file_path, verbose=False, require_local_path=False):
    '''Get exhaustive information about a SAR source file'''

    # make sure its the absolute path
    abspath = os.path.abspath(file_path)

    # get drive info of path
    p = run("df %s" % abspath, shell=True, capture_output=True)
    if (p.returncode!=0):
        raise Exception("Could not retrieve hard drive info for file %s" % abspath)
    drvinfo = p.stdout.decode().split("\n")[1].split()
    if verbose: print("%s: Drive info for %s" % (sys.argv[0], abspath), "=", drvinfo)
    if require_local_path and not drvinfo[0].startswith("/dev"):
        raise Exception("Source file %s is not a local file" % abspath )

    # prepare the dict return obj
    return_dct = {'abspath':abspath, 'hdd': drvinfo[0]}

    # locate partition information for file
    partitions = psutil.disk_partitions()
    found_partition = False
    for partition in partitions:
        if partition.device==drvinfo[0]:
            found_partition=True
            break
    if not found_partition:
        if require_find_partition:
            raise Exception("Could not location partition for %s" % abspath)
        else:
            print("%s: WARNING: Could not find partition info for %s" % (sys.argv[0],abspath))

    # get summary drives
    cmd = "hwinfo --short --disk"
    if verbose: print("%s: Running cmd-" % sys.argv[0],cmd)
    p = run(cmd, shell=True, capture_output=True)
    if p.returncode!=0:
        if verbose: print("%s: hwinfo stdout=" % sys.argv[0], p.stdout.decode())
        raise Exception("Could not run 'hwinfo' - Are you sure its installed?")
    drives_lines = p.stdout.decode().split("\n")
    if verbose: print("%s: Drive lines=" % sys.argv[0], drives_lines)
    drives = [ ln.strip().split()[0] for ln in drives_lines[1:] if ln.strip()!="" ]
    drives_dct = {}
    for drv in drives:
        drives_dct[drv] = drv
    if verbose: print("%s: Got hwinfo drives" % sys.argv[0], drives_dct)

    # get drive manufacturer info
    if found_partition:
        primdrv_part = partition.device
        if verbose: print("%s: Primary drive partition = " % sys.argv[0], primdrv_part)
        primdrv = None
        for drv in drives_dct.keys():
            if verbose: print("%s: drv compare =" % sys.argv[0],drv,primdrv_part)
            if primdrv_part.find(drv)==0:
                primdrv = drv
                if verbose: print("%s: found!" % sys.argv[0], drv, primdrv)
                break
        if primdrv == None:
            raise Exception("Could not get primary drive info for " + partition.device +" " + primdrv_part)

        p = run("hwinfo --disk --only %s" % primdrv, shell=True, capture_output=True)
        if p.returncode!=0:
            raise Exception("Could not run 'hwinfo' - Are you sure its installed?")
        hwinfos = [ el.strip() for el in p.stdout.decode().split("\n") ]
    return_dct['model'] = None
    return_dct['device'] = None
    if found_partition:
        for hwinfo in hwinfos:
            if hwinfo.startswith("Model:"): return_dct['model'] = hwinfo.split(":")[1].strip()
            if hwinfo.startswith("Device:"): return_dct['device'] = hwinfo.split(":")[1].strip()

    # enumerate 'source' files and get additional per file information
    files_info = {}
    files = os.listdir(abspath)
    for f in files:
        file_info = {}
        fpath = os.path.join(abspath,f)
        sz = os.stat(fpath).st_size
        file_info['size']=sz
        # h5 files get special treatment
        if f.endswith(".h5"):
            with h5py.File(fpath, 'r') as fd:
                keys= fd.keys()
                file_info["h5keys"] = [str(k) for k in keys]
                for k in keys:
                    try:
                        file_info[str(k)] = (fd[k].shape,fd[k].dtype)
                    except:
                        print("%s: WARNING: h5 dataset with k=%s is not a numpy array" % sys.argv[0])
        files_info[f]=file_info
    return_dct['files_info'] = files_info

    # get machine name
    machine_name = platform.node()
    return_dct['machine_name'] = machine_name

    # get cpu info
    processor_all = check_output("lscpu", shell=True).strip().decode()
    processor = "".join( [ ln.split(":")[1].strip() for ln in processor_all.split("\n") if ln.startswith("Model name:") ] )
    return_dct["processor"] = processor
    cpu_count = psutil.cpu_count(logical=True)
    return_dct["cpu_count"] = cpu_count
    cpu_freq = psutil.cpu_freq()
    return_dct["cpu_freq"] = str(cpu_freq)

    # get memory info
    mem_info = psutil.virtual_memory()
    return_dct['mem'] = str(mem_info)

    if verbose: print("returning source info=", return_dct)
    return return_dct


if __name__ == "__main__":

    info = get_file_info("/", verbose=True, require_local_path=True)
    print(info)
