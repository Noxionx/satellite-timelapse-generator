# Satellite TimeLapse Generator

This python script will generate a timelapse from satellite images of clouds above Europe (generated every 15 minutes).
It gets most recent images on a period (ex. : last 24 hours) and uses [FFmpeg](https://ffmpeg.org/) to generate the video.

## Installation
This script requires [Python 2.7](https://www.python.org/downloads/release/python-2713/), [PiP](https://pip.pypa.io/en/stable/installing/) and [FFmpeg](https://ffmpeg.org/download.html) to be installed.
You'll need some additional libraries :
```
pip install pathlib
pip install ffmpy
```

## Usage
### Basic
```
python generator.py
```
The command will generate a timelapse of the last 24 hours.

### Options
**-c, --color**
Create timelapse with Infra Red colored images
**-d, --days**
Period of the timelapse. Default to 1 day.
**-f, --framerate**
Number of images per seconds in the timelapse. /!\ High framerate on short period will generate very short timelapse /!\\. Default to 6 FPS.
**-h, --help**
Show help.

### Example
To generate a colored timelapse of the last week at 24 frames per seconds :
```
python generator.py -c -d 7 -f 24
``` 

### Notes
This script caches images into `.img` directory. 
It is recommended to have enough disk space to generate on a long period.
At least 60 MB / day
