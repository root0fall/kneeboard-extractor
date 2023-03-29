'''extract BMS kneeboard images'''

# Kneeboard Extractor
# Copyright (C) 2023 root0fall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import re
import time
import winreg
import argparse
from PIL import Image

VERSION = "1.3.0b"

INIT_DDS = 7982
DDS_COUNT = 16

DEBUG = False
INFO = True
FORCE = False

BMS_VERSION = "4.37"
WIN_REG_KEY = rf"SOFTWARE\WOW6432Node\Benchmark Sims\Falcon BMS {BMS_VERSION}"
DDS_DIR = os.path.join("Data","TerrData","Objects","KoreaObj")
EXT = ".dds"
OUT_EXT = "png"

DIM_RE = re.compile(r'\d+%?')

EXIT_BAD_RESTRICT = 1
EXIT_BAD_DIR = 2

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

def write_cropped(img, indims, dims, target):
    '''write the cropped image to file with supplied dimensions'''

    debug(f'writing cropped {img}, {dims}, {target}')

    cropped = img.crop(dims)

    width = indims[0]
    height = indims[1]
    if width != 0:
        if isinstance(width, float):
            width = int(cropped.width * width)

    if height != 0:
        if isinstance(height, float):
            height = int(cropped.height * height)

    if height != 0 or width != 0:
        debug(f'resizing: {width}x{height}')
        cropped = cropped.resize((width or cropped.width, height or cropped.height),
                            Image.Resampling.BICUBIC)

    info(f"writing knee {cropped.width}x{cropped.height}: {target}")
    if not os.path.isdir(os.path.dirname(target)):
        if not FORCE:
            print(f'invalid output directory: {os.path.dirname(target)}')
            print('use --force argument to create missing directory')
            sys.exit(EXIT_BAD_DIR)
        else:
            os.mkdir(os.path.dirname(target))
    cropped.save(target, format=OUT_EXT)

def write_new_files(base_dir, indims, leftdir, rightdir, restrictions=None):
    '''write new kneeboard images to output directory'''

    for i in range(INIT_DDS, INIT_DDS + DDS_COUNT):
        original = os.path.join(get_dds_dir(base_dir), str(i) + EXT)
        debug(f'processing original: {original}')
        debug(f'values: {base_dir}, {indims}, {leftdir}, {rightdir}, {restrictions}')
        with Image.open(original) as img:

            left_dims = (0,0,int(img.size[0]/2),img.size[1])
            lfname = os.path.join(leftdir, f"L_{str(i)}.{OUT_EXT}")
            if restrictions is None or str(i + 1 - INIT_DDS) in restrictions[0]:
                write_cropped(img, indims, left_dims, lfname)

            right_dims = int(img.size[0]/2),0,img.size[0],img.size[1]
            rfname = os.path.join(rightdir or leftdir, f"R_{str(i)}.{OUT_EXT}")
            if restrictions is None or str(i + 1 - INIT_DDS) in restrictions[1]:
                write_cropped(img, indims, right_dims, rfname)

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

def monitor(base_dir, indims, *dirs, **restrictions):
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
            write_new_files(base_dir, indims, *dirs, **restrictions)
            prev_time = new_time
            prevl_time = get_time(check_file_last)
            info("fresh files written")
        time.sleep(0.2)

def parse_dim(dim):
    '''parse individual dimension value, int or %%'''

    if dim is None:
        return 0

    dmatch = DIM_RE.match(dim)
    if dmatch is None:
        debug('dimension unmatched {dim}')
        return 0
    if dim[-1] == "%":
        return float(dim[:-1])/100
    return int(dim)

def parse_res(width, height):
    '''parse supplied width and height'''
    return parse_dim(width), parse_dim(height)

def parse_restrictions(vals):
    '''parse command-line restricted pages'''

    valid_left = re.compile(r'[l0-9]{2,3}')
    valid_right = re.compile(r'[r0-9]{2,3}')
    left = []
    right = []

    try:
        opts = vals.split(',')
        for opt in opts:
            if valid_left.match(opt.lower()):
                left.append(opt[1:])
            elif valid_right.match(opt.lower()):
                right.append(opt[1:])
            else:
                return None
        if not left and not right:
            return None

    # pylint: disable=bare-except
    except:
        print(f'error parsing restrictions: {vals}')
        return None

    return left, right


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Kneeboard Extractor",
                                    description="Extract Kneeboard images from BMS files")
    parser.add_argument("--monitor", action="store_true", help="automatically detect changes to " +\
                        "BMS kneeboard files, and write to output directory")
    parser.add_argument("--basedir", metavar='<BASEDIR>',
                        help="BMS base directory for locating kneeboard files")
    parser.add_argument("--left", required=True, metavar='<LEFTDIR>',
                        help="directory to output left kneeboard images")
    parser.add_argument("--right", required=False, metavar='<RIGHTDIR>',
                        help="directory to output right kneeboard images (optional)")
    parser.add_argument("--debug", action="store_true", help="enable debug messages")
    parser.add_argument("--silent", action="store_false", help="disable messages")
    parser.add_argument('--version', action='version', version=f'{parser.prog} {VERSION}')
    parser.add_argument('--force', action='store_true',
                        help='force creation of target directory if it doesn\'t exist')
    parser.add_argument('--restrict', help='''restrict output to a comma-delimited set of pages
                                        e.g. L1,R4,R8''', metavar='<L1,L2,R5...>')
    parser.add_argument('--width', help='''set width of output as absolute pixel dimension,
                        or as percentage of original, e.g. 768 or 140%%''',
                        metavar='<RES_VAL | VAL%>')
    parser.add_argument('--height', help='''set width of output as absolute pixel dimension,
                        or as percentage of original, e.g. 768 or 140%%''',
                        metavar='<RES_VAL | VAL%>')
    parser.add_argument('--custom', help='''specifiy a custom path for theatres other than KTO
                        e.g. \'Data\\Add-On Balkans\\Terrdata\\objects\\KoreaObj\'''',
                        metavar='<DDSDIR>')

    args = parser.parse_args()

    DEBUG = args.debug if args.debug is not None else DEBUG
    INFO = args.silent if args.silent is not None else INFO
    FORCE = args.force if args.force is not None else FORCE
    DDS_DIR = args.custom if args.custom is not None else DDS_DIR

    if args.restrict is not None:
        page_restrictions = parse_restrictions(args.restrict)
        if page_restrictions is None:
            print(f'invalid restrictions in {args.restrict}')
            sys.exit(EXIT_BAD_RESTRICT)

    basedir = get_base_dir(args.basedir)
    try:
        if args.monitor:
            monitor(basedir, parse_res(args.width, args.height), args.left.strip("\\"),
                    args.right.strip("\\") if args.right else None,
                    restrictions=page_restrictions if args.restrict else None)
        else:
            write_new_files(basedir, parse_res(args.width, args.height), args.left.strip("\\"),
                            args.right.strip("\\") if args.right else None,
                            restrictions=page_restrictions if args.restrict else None)
    except KeyboardInterrupt:
        sys.stderr.write("\rExiting...\n")
        sys.exit(0)
