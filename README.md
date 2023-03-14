# kneeboard-extractor

## Description

Kneeboard Extractor is a command-line utility that converts kneeboard DDS files into PNG files. It splits the left/right kneeboard pages from the DDS images and outputs them to the directory specfied by the *--left* command-line argument. If the preference is to have left and right pages go to different directories, use the *--right* command-line argument to specify where the righthand pages will go.

The user is able to set the utility to monitor for changes (e.g. when updating kneeboards from Weapons Delivery Planner) by using the *--monitor* argument.

The utility can also be used to simply output PNG files for other uses, but it was primarily created to use with Open Kneeboard, by setting 2 tabs, 1 each for left and right page outputs.

It is written in python under GPL 3.0 licensing.

The executable in Releases has been tested on Windows 10 x86_64.


## CLI Usage

usage: Kneeboard Extractor [-h] [--monitor] [--basedir BASEDIR] --left LEFT
                           [--right RIGHT] [--debug] [--silent]

Extract Kneeboard images from BMS files

options:

  -h, --help         show this help message and exit

  --monitor          automatically detect changes to BMS kneeboard files, and
                     write to output directory

  --basedir BASEDIR  BMS base directory for locating kneeboard files

  --left LEFT        directory to output left kneeboard images

  --right RIGHT      directory to output right kneeboard images (optional)

  --debug            enable debug messages

  --silent           disable messages

## Executable

v1.0.0b

SHA256 - 42A410401D479356B3D47135193745907C3A0E4D1D8B72C71D01CD778B831EE8
