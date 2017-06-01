#!/usr/bin/python

import os, sys, getopt, shutil, urllib
from pathlib import Path
from datetime import datetime, timedelta
from ffmpy import FFmpeg

BASE_URL = "http://neige.meteociel.fr/satellite/archives"
BASE_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

def format(num):
    return '0%s' % (num) if num < 10 else '%s' % (num)

def mkdirOfNotExists(path):
    d = Path(path)
    if not d.exists():
        os.mkdir(path)

def convertFile(input, output):
    try:
        ff = FFmpeg(inputs={input: '-loglevel error'}, outputs={output: None})
        ff.run()
    except Exception as e:
        print 'Error during conversion of %s into %s --- %s' % (input, output, e)

def getFileIfNotExists(url, filename):
    jfilename = '%s/.img/%s.jpg' % (BASE_DIR, filename)
    gfilename = '%s/.gif/%s.gif' % (BASE_DIR, filename)
    j = Path(jfilename)
    g = Path(gfilename)
    if not j.exists():
        if not g.exists():
            try:
                file = urllib.URLopener()
                file.retrieve(url, gfilename)
            except:
                pass
        if g.exists():
            convertFile(gfilename, jfilename)

def getImagesForPeriod(startDate, endDate, c):
    mkdirOfNotExists('%s/.gif' % (BASE_DIR))
    mkdirOfNotExists('%s/.img' % (BASE_DIR))
    color = ("color" if c else "")
    date = startDate
    duration = endDate - startDate
    while date < endDate:
        date = date + timedelta(minutes=15)
        d = '%s-%s-%s' % (format(date.day), format(date.month), format(date.year))
        h = '%s-%s' % (format(date.hour), format(date.minute))
        url = '%s/%s/satir%s-%s.gif' % (BASE_URL, d, color, h)
        filename = '%s-%s-%s' % (d, h, color)
        getFileIfNotExists(url, filename)
        currentDuration = date - startDate
        sys.stdout.write('\rGet images... %s %%' % (int(round((currentDuration.total_seconds() / duration.total_seconds()) * 100))))
        sys.stdout.flush()
    shutil.rmtree('%s/.gif' % (BASE_DIR))
    print ''

def generateTimelapse(startDate, endDate, c, framerate):
    mkdirOfNotExists('%s/.tl' % (BASE_DIR))
    color = ("color" if c else "")
    i = 1
    date = startDate
    duration = endDate - startDate
    while date < endDate:
        date = date + timedelta(minutes=15)
        d = '%s-%s-%s' % (format(date.day), format(date.month), format(date.year))
        h = '%s-%s' % (format(date.hour), format(date.minute))
        filename = '%s/.img/%s-%s-%s.jpg' % (BASE_DIR, d, h, color)
        f = Path(filename)
        currentDuration = date - startDate
        sys.stdout.write('\rCopy images... %s %%' % (int(round((currentDuration.total_seconds() / duration.total_seconds()) * 100))))
        sys.stdout.flush()
        if f.exists():
            dst = '%s/.tl/img%s.jpg' % (BASE_DIR, i)
            shutil.copyfile(filename, dst)
            i = i + 1

    print ''
    fname = '%s/timelapse%s.mp4' % (BASE_DIR, color)
    f = Path(fname)
    if f.exists():
        f.unlink()
    ff = FFmpeg(
        inputs={'%s/.tl/img%%d.jpg' % (BASE_DIR): '-loglevel info -framerate %s -start_number 1' % (framerate)},
        outputs={fname: '-c:v libx264 -pix_fmt yuv420p'}
    )
    ff.run()
    shutil.rmtree('%s/.tl' % (BASE_DIR))


def main(argv):
    c = False
    days = 1
    framerate = 6
    try:
        opts, args = getopt.getopt(argv, "hcd:f:", ["help","color", "days=", "framerate="])
    except getopt.GetoptError:
        print 'generator.py'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'This script will generate a timelapse from satellite images of clouds above Europe. Those images are generated every 15 minutes.\n' \
                  'The script gets most recent images on a period (ex. : last 24 hours).\n\n' \
                  'Usage : generator.py [OPTIONS]\n\n' \
                  ' -h, --help \t\tPrint this help\n' \
                  ' -c, --color \t\tCreate timelapse with Infra Red colored images\n' \
                  ' -d, --days \t\tPeriod of the timelapse. Default to 1 day.\n' \
                  ' -f, --framerate \tNumber of images per seconds in the timelapse. /!\\ High framerate on short period will generate very short timelapse /!\\. Default to 6 FPS.'
            sys.exit()
        elif opt in ("-c", "--color"):
            c = True
        elif opt in ("-d", "--days"):
            days = int(arg)
        elif opt in ("-f", "--framerate"):
            framerate = int(arg)

    refDate = datetime.now() - timedelta(minutes=30)
    endDate = datetime(refDate.year, refDate.month, refDate.day, refDate.hour, (refDate.minute / 15) * 15)
    startDate = endDate - timedelta(days=days)
    duration = endDate - startDate
    resolution = timedelta(minutes=(framerate * 15))

    print '-----------------------------------------------'
    print 'Generating timelapse from %s to %s at %s FPS' % (startDate, endDate, framerate)
    print 'Resolution : %s hour(s) / s' % (resolution.total_seconds() / 3600)
    print 'Estimated video duration : %ss' % (int(duration.total_seconds() / resolution.total_seconds()))
    print '-----------------------------------------------'

    getImagesForPeriod(startDate, endDate, c)
    generateTimelapse(startDate, endDate, c, framerate)

if __name__ == "__main__":
   main(sys.argv[1:])