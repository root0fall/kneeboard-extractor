'''extract BMS kneeboard images'''

import sys
import os
import time
import winreg
import argparse
from PIL import Image

VERSION = "0.9.0"

INIT_DDS = 7982
DDS_COUNT = 16

DEBUG = False
INFO = True
BMS_VERSION = "4.37"
WIN_REG_KEY = rf"SOFTWARE\WOW6432Node\Benchmark Sims\Falcon BMS {BMS_VERSION}"
DDS_DIR = os.path.join("Data","TerrData","Objects","KoreaObj")
EXT = ".dds"
OUT_EXT = "png"

get_time = lambda cfile: os.stat(cfile).st_ctime

def debug(message):
    '''debug message wrapper'''
    if DEBUG:
        sys.stderr.write(f"\n{message}\n")

def info(message):
    '''print message'''
    if INFO:
        print(message)

def get_dds_dir(base_dir):
    '''path to the BMS DDS files'''

    return os.path.join(base_dir, DDS_DIR)

def get_base_dir(base_dir):
    '''get the BMS base directory'''
    # pylint: disable=broad-except,too-many-nested-blocks

    if base_dir is None:
        try:
            con = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(con, WIN_REG_KEY)
            for element in range(8):
                try:
                    vals = winreg.EnumValue(key, element)
                    if vals[0] == "baseDir":
                        ret_base = os.path.normpath(vals[1])
                        if os.path.isdir(ret_base):
                            return ret_base
                except Exception as regerr:
                    debug(regerr)
            sys.stderr.write("\nUnable to determine BMS base directory from Registry\n")
            sys.stderr.write("Supply base directory directly with --basedir arguement\n\n")
        except Exception as err:
            sys.stderr.write("\nError detecting BMS base path from registry - " +
                                "pass --base_dir argument instead\n")
            debug(err)
    return base_dir

def write_new_files(base_dir, leftdir, rightdir):
    '''write new kneeboard images to output directory'''

    for i in range(INIT_DDS, INIT_DDS + DDS_COUNT):
        original = os.path.join(get_dds_dir(base_dir), str(i) + EXT)
        with Image.open(original) as img:

            left_dims = (0,0,int(img.size[0]/2),img.size[1])
            cropped = img.crop(left_dims)
            lfname = os.path.join(leftdir, f"L_{str(i)}.{OUT_EXT}")
            info(f"writing left knee: {lfname}")
            cropped.save(lfname, format=OUT_EXT)

            right_dims = int(img.size[0]/2),0,img.size[0],img.size[1]
            cropped2 = img.crop(right_dims)
            rfname = os.path.join(rightdir or leftdir, f"R_{str(i)}.{OUT_EXT}")
            info(f"writing right knee: {rfname}")
            cropped2.save(rfname, format=OUT_EXT)

def monitor_sequence():
    '''generator for monitor message'''

    message = "..monitoring.."
    count = 0
    while True:
        if count == len(message):
            yield " "*len(message)
            count = 0
        else:
            yield message[:count % len(message) + 1] + " "*(len(message) - count - 1)
            count += 1

def monitor(base_dir, *dirs):
    '''monitor for changes to kneebaord files'''

    check_file = os.path.join(get_dds_dir(base_dir), str(INIT_DDS) + EXT)
    check_file_last = os.path.join(get_dds_dir(base_dir), str(INIT_DDS + DDS_COUNT - 1) + EXT)
    prev_time = get_time(check_file)
    prevl_time = get_time(check_file_last)
    for msg in monitor_sequence():
        if INFO:
            sys.stdout.write("\r" + msg)
        new_time = get_time(check_file)
        if prev_time != new_time:
            info("\rchange detected waiting for modification completion")
            newl_time = get_time(check_file_last)
            while newl_time == prevl_time:
                newl_time = get_time(check_file_last)
                time.sleep(1)
            write_new_files(base_dir, *dirs)
            prev_time = new_time
            info("fresh files written")
        time.sleep(0.2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Kneeboard Extractor",
                                    description="Extract Kneeboard images from BMS files")
    parser.add_argument("--monitor", action="store_true", help="automatically detect changes to " +\
                        "BMS kneeboard files, and write to output directory")
    parser.add_argument("--basedir", help="BMS base directory for locating kneeboard files")
    parser.add_argument("--left", required=True, help="directory to output left kneeboard images")
    parser.add_argument("--right", required=False,
                        help="directory to output right kneeboard images (optional)")
    parser.add_argument("--debug", action="store_true", help="enable debug messages")
    parser.add_argument("--silent", action="store_false", help="disable messages")

    args = parser.parse_args()

    DEBUG = args.debug if args.debug is not None else DEBUG
    INFO = args.silent if args.silent is not None else INFO

    basedir = get_base_dir(args.basedir)
    try:
        if args.monitor:
            monitor(basedir, args.left.strip("\\"),
                    args.right.strip("\\") if args.right else None)
        else:
            write_new_files(basedir, args.left.strip("\\"),
                            args.right.strip("\\") if args.right else None)
    except KeyboardInterrupt:
        sys.stderr.write("\rExiting...\n")
        sys.exit(0)
