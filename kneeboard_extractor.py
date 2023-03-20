'''extract BMS kneeboard images'''

import sys
import os
import time
import winreg
import argparse
from wand.image import Image

INIT_DDS = 7982
DDS_COUNT = 16

DEBUG = False
BMS_VERSION = '4.37'
WIN_REG_KEY = rf'SOFTWARE\WOW6432Node\Benchmark Sims\Falcon BMS {BMS_VERSION}'
DDS_DIR = os.path.join("Data","TerrData","Objects","KoreaObj")
EXT = ".dds"
OUT_EXT = "png"

get_time = lambda cfile: os.stat(cfile).st_ctime

def debug(message):
    '''debug message wrapper'''
    if DEBUG:
        sys.stderr.write(f"\n{message}\n")

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
                    if vals[0] == 'baseDir':
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
        with Image(filename=os.path.join(get_dds_dir(base_dir), str(i) + EXT)) as img:
            with img[0:int(img.size[0]/2), 0:img.size[1]] as cropped:
                cropped.format = OUT_EXT
                lfname = os.path.join(leftdir, f"L_{str(i)}.{OUT_EXT}")
                print(f"writing left knee: {lfname}")
                cropped.save(filename=lfname)
            with img[int(img.size[0]/2):img.size[0], 0:img.size[1]] as cropped2:
                cropped2.format = OUT_EXT
                rfname = os.path.join(rightdir or leftdir, f"R_{str(i)}.{OUT_EXT}")
                print(f"writing right knee: {rfname}")
                cropped2.save(filename=rfname)

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
    prev_time = get_time(check_file)
    for msg in monitor_sequence():
        sys.stdout.write('\r' + msg)
        new_time = get_time(check_file)
        if prev_time != new_time:
            print("change detected writing fresh files")
            time.sleep(10)
            write_new_files(base_dir, *dirs)
            prev_time = new_time
            print("fresh files written")
        time.sleep(0.2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Kneeboard Extractor",
                                    description="Extract Kneeboard images from BMS files")
    parser.add_argument("--monitor", action='store_true', help="automatically detect changes to " +\
                        "BMS kneeboard files, and write to output directory")
    parser.add_argument("--basedir", help="BMS base directory for locating kneeboard files")
    parser.add_argument("--left", required=True, help="directory to output left kneeboard images")
    parser.add_argument("--right", required=False,
                        help="directory to output right kneeboard images")
    parser.add_argument("--debug", action='store_true', help="enable debug messages")

    args = parser.parse_args()

    DEBUG = args.debug if args.debug is not None else DEBUG

    basedir = get_base_dir(args.basedir)
    try:
        if args.monitor:
            monitor(basedir, args.left, args.right)
        else:
            write_new_files(basedir, args.left, args.right)
    except KeyboardInterrupt:
        sys.stderr.write("Exiting...\n")
        sys.exit(0)
