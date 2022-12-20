#!/usr/bin/env python3

import os
import sys
import calendar
import time
import argparse
from datetime import datetime
from pathlib import Path

###############################################################################
# GPhotos Backup Albums Tool using RClone
#
# To execute: 
# ./backup_photos.py gphotos ./backupDir '2021' \
#   -sm -smFrom 'me@gmail.com' \ 
#   -smTo 'logviewer@gmail.com' \ 
#   -clean
#
###############################################################################

CURRENT_TIMESTAMP = calendar.timegm(time.gmtime())
CURRENT_DIR = Path(os.getcwd())
LOG_FILE = f'backup-{CURRENT_TIMESTAMP}.txt'
LOG_FILE_PATH = str(CURRENT_DIR / LOG_FILE)


# dprint - print util to print both stdout and to log file
def dprint(lineToPrint):
    print(lineToPrint)
    original_stdout = sys.stdout # Save a reference to the original standard output
    with open(LOG_FILE_PATH, 'a') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print(lineToPrint)
        sys.stdout = original_stdout # Reset the standard output to its original value

def getGphotosCopyCmd(rcloneRemote, year, dest):
    destPath = Path(dest) / year
    return f'rclone copy "{rcloneRemote}:media/by-year/{year}" "{destPath}"'

def executeRcloneCopy(rcloneCopyCmd):
    try:
        retVal = os.system(rcloneCopyCmd)
        return (0 == retVal)        
    except:
        return False

def backupPhotosByYear(rcloneRemote, year, dest):
    dprint("Getting gPhotos data...")
    copyCmd = getGphotosCopyCmd(rcloneRemote, year, dest)
    dprint(f'Starting backup year {year}...')
    dprint("  Exec command: " + copyCmd)
    status = executeRcloneCopy(copyCmd)
    dprint("  Status: " + str(status))

def cleanupLogAndFiles():
    print("# Cleaning up files")
    os.remove(LOG_FILE_PATH)

def sendLogViaEmail(sender, to, rcloneRemote, albumType, dest, dateFrom, dateTo):
    import sendmail
    print(f'# Send Log Via Email ({to})')
    dateFromStr = dateFrom.strftime("%Y-%m-%d")
    dateToStr = dateTo.strftime("%Y-%m-%d")
    subject = f'GPhotos Backup Status ({albumType}): {dateFromStr} - {dateToStr}'
    htmlMsg = f'''<h2>Backup Status:</h2>
        <span style="font-size: 130%;"><b>From: </b></span><span style="font-size: 120%;">{rcloneRemote}:{albumType},</span>
        <span style="font-size: 130%;"><b>To: </b></span><span style="font-size: 120%;">{dest},</span> 
        <span style="font-size: 130%;"><b>Period: </b></span><span style="font-size: 120%;">{dateFromStr} - {dateToStr}</span>
        '''
    sendmail.sendMail(sender, to, subject, htmlMsg, None, [LOG_FILE_PATH], False)


def getCmdlineArgs():
    parser = argparse.ArgumentParser(description='GPhotos Backup Photos Tool via RClone')
    parser.add_argument('remote', help="RClone remote")
    parser.add_argument('dest', help="Destination: dir or RClone remote")
    parser.add_argument('year', type=lambda s: datetime.strptime(s, '%Y'), help="Year YYYY")    
    parser.add_argument('-sm', default=False, action='store_true', help="Send log via Email?")
    parser.add_argument('-smFrom', help="If -sm is set, sender email addr is needed")
    parser.add_argument('-smTo', help="If -sm is set, recipient email addr is needed")
    parser.add_argument('-clean', default=False, action='store_true', help="Clean up log and other temp files downloaded")
    args = parser.parse_args()

    if (args.sm) and ((args.smFrom is None) or (args.smTo is None)):
       parser.error('-sm flag requires -smFrom (sender email) and -smTo (recipient email)')

    return args

if __name__ == "__main__":
    args = getCmdlineArgs()
    backupPhotosByYear(args.remote, args.year.strftime("%Y"), args.dest)
    if (args.sm):
       sendLogViaEmail(args.smFrom, args.smTo, args.remote, args.albumType, args.dest, args.dateFrom, args.dateTo)
    if (args.clean):
       cleanupLogAndFiles()
