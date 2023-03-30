# kneeboard-extractor

## Description

Kneeboard Extractor is a command-line utility that converts kneeboard DDS files into PNG files. It splits the left/right kneeboard pages from the DDS images and outputs them to the directory specfied by the `--left` command-line argument. If the preference is to have left and right pages go to different directories, use the `--right` command-line argument to specify where the righthand pages will go.

The user is able to set the utility to monitor for changes (e.g. when updating kneeboards from Weapons Delivery Planner) by using the `--monitor` argument.

The utility can also be used to simply output PNG files for other uses, but it was primarily created to use with Open Kneeboard, by setting 2 tabs, 1 each for left and right page outputs.

The BMS base directory should be located automatically, but if not, supply it with `--basedir`

It is written in python under GPL 3.0 licensing.

#### The executable in Releases has been tested on Windows 10 x86_64.


## CLI Usage

```

usage: Kneeboard Extractor [-h] [--monitor] [--basedir <BASEDIR>] --left
                           <LEFTDIR> [--right <RIGHTDIR>] [--debug] [--silent]
                           [--version] [--force] [--restrict <L1,L2,R5...>]
                           [--width <RES_VAL | VAL%>]
                           [--height <RES_VAL | VAL%>] [--custom <DDSDIR>]

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

  --width <RES_VAL | VAL%>
                        set width of output as absolute pixel dimension, or as
                        percentage of original, e.g. 768 or 140%

  --height <RES_VAL | VAL%>
                        set width of output as absolute pixel dimension, or as
                        percentage of original, e.g. 768 or 140%

  --custom <DDSDIR>     specifiy a custom path for theatres other than KTO
                        e.g. 'Data\Add-On Balkans\Terrdata\objects\KoreaObj'
```

## Example

### launch in monitor mode (waiting for changes to kneeboard DDS files) and output all files to "E:\LEFT KBD"


`kneeboard_extractor.exe --left 'E:\LEFT KBD' --monitor`

## Notes

 - users wishing to use a batch script to run the utility will need to use a double percent symbol (`%%`) when using the `--width` or `--height` arguments with percentages, to prevent them being consumed as a variable special character

## Executable

v1.3.0b

SHA256 - E26F0622C953789E67C423DD1CE1486AE45FFDAD12136BCAFAB6EF9091F1BDFF

## Building from source

`pyinstaller kneeboard_extractor.py --onefile`

## Dependencies

 - PIL
