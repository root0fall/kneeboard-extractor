# kneeboard-extractor

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
