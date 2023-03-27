# kneeboard-extractor

## Description

Kneeboard Extractor is a command-line utility that converts kneeboard DDS files into PNG files. It splits the left/right kneeboard pages from the DDS images and outputs them to the directory specfied by the *--left* command-line argument. If the preference is to have left and right pages go to different directories, use the *--right* command-line argument to specify where the righthand pages will go.

The user is able to set the utility to monitor for changes (e.g. when updating kneeboards from Weapons Delivery Planner) by using the *--monitor* argument.

The utility can also be used to simply output PNG files for other uses, but it was primarily created to use with Open Kneeboard, by setting 2 tabs, 1 each for left and right page outputs.

The BMS base directory should be located automatically, but if not, supply it with *--basedir*

It is written in python under GPL 3.0 licensing.

The executable in Releases has been tested on Windows 10 x86_64.


## CLI Usage

```shell
usage: Kneeboard Extractor [-h] [--monitor] [--basedir <BASEDIR>] --left
                           <LEFTDIR> [--right <RIGHTDIR>] [--debug] [--silent]
                           [--version] [--force] [--restrict <L1,L2,R5...>]


options:
  -h, --help            show this help message and exit

  --monitor             automatically detect changes to BMS kneeboard files,
                        and write to output directory

  --basedir <BASEDIR>   BMS base directory for locating kneeboard files

  --left <LEFTDIR>      directory to output left kneeboard images

  --right <RIGHTDIR>    directory to output right kneeboard images (optional)

  --debug               enable debug messages

  --silent              disable messages

  --version             show program's version number and exit

  --force               force creation of target directory if it doesn't exist

  --restrict <L1,L2,R5...>
                        restrict output to a comma-delimited set of pages e.g.
                        L1,R4,R8
```

## Example

### launch in monitor mode (waiting for changes to kneeboard DDS files) and output all files to "E:\LEFT DIR" 

`kneeboard_extractor.exe --left 'E:\LEFT KBD' --monitor`

## Executable

v1.2.0b

SHA256 - AA11758DEA5ECC11B8AF2E2199B07AE7F7587E8AF2816E5430205D4B609CBC75
