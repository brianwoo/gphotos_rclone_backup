#!/usr/bin/env python3

import os
import sys
import json
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
GPHOTOS_ALBUM_JSON_FILE = f'gphotos-{CURRENT_TIMESTAMP}.json'
GPHOTOS_ALBUM_JSON_FILE_PATH = str(CURRENT_DIR / GPHOTOS_ALBUM_JSON_FILE)
ALBUM_TYPES = ['album', 'shared-album']



# dprint - print util to print both stdout and to log file
def dprint(lineToPrint):
    print(lineToPrint)
    original_stdout = sys.stdout # Save a reference to the original standard output
    with open(LOG_FILE_PATH, 'a') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print(lineToPrint)
        sys.stdout = original_stdout # Reset the standard output to its original value

def getGphotosAlbumListCmd(rcloneRemote, albumType):
    return f'rclone lsjson --files-only -R {rcloneRemote}:{albumType} > {GPHOTOS_ALBUM_JSON_FILE_PATH}' 

def getGphotosAlbumCopyCmd(rcloneRemote, albumType, albumName, dest):
    srcAlbumName = escapeCharsInSrcAlbumName(albumName)
    destAlbumName = escapeCharsInDestAlbumName(albumName)
    destPath = Path(dest) / destAlbumName
    return f'rclone copy "{rcloneRemote}:{albumType}/{srcAlbumName}" "{destPath}"'

def escapeCharsInSrcAlbumName(albumName):
    return albumName.replace('"', '\\"')

def escapeCharsInDestAlbumName(albumName):
    albumName = albumName.replace('"', '')
    albumName = albumName.replace('/', '')
    return albumName

def readJsonFile(jsonFilePath):
    with open(jsonFilePath, encoding="utf8") as f:
        jsonData = json.load(f)

    return jsonData

def executeRcloneCopy(rcloneCopyCmd):
    try:
        retVal = os.system(rcloneCopyCmd)
        return (0 == retVal)        
    except:
        return False

def executeRcloneToJson(rcloneRemote, albumType):
    # build the rclone command with the album type
    cmdGetGphotosAlbumJson = getGphotosAlbumListCmd(rcloneRemote, albumType)
    retVal = os.system(cmdGetGphotosAlbumJson)  # returns the exit code in unix
    if 0 != retVal:
        raise RuntimeError("Cannot get gPhotos JSON")


def getGphotosAlbumJson(rcloneRemote, albumType):
    # execute the rclone command and parse json file
    executeRcloneToJson(rcloneRemote, albumType)
    jsonData = readJsonFile(GPHOTOS_ALBUM_JSON_FILE_PATH)
    return jsonData


def isFileModifiedBetweenPeriods(jsonRecord, fromDate, toDate):
    modDatetime = getDatetimeFromISO8601(jsonRecord['ModTime'])
    return (fromDate <= modDatetime) and (toDate >= modDatetime)


def getDatetimeFromISO8601(iso8601Str):
    modTime = datetime.strptime(iso8601Str, "%Y-%m-%dT%H:%M:%S%fZ")
    # Zero out the time because we only want to compare the dates
    newModTime = modTime.replace(hour=0, minute=0, second=0)
    return newModTime

def getDatetimeFromDateStr(dateStr):
    return datetime.strptime(dateStr, "%Y-%m-%d")

def getAlbumName(jsonRecord):
    # We are going to split by the /fileName. This is to avoid a directory
    # name that contains a '/'
    fileName = jsonRecord['Name']
    path = jsonRecord['Path'].split("/" + fileName)
    if len(path) != 2:
        raise RuntimeError("Cannot get the album name correctly")
    
    return path[0]


def findAlbumsUpdatedBetween(jsonData, rcloneRemote, albumType, dest, fromDate, toDate):
    albumsFound = {}
    for eachRecord in jsonData:
        if isFileModifiedBetweenPeriods(eachRecord, fromDate, toDate):
            album = getAlbumName(eachRecord)
            copyCmd = getGphotosAlbumCopyCmd(rcloneRemote, albumType, album, dest)
            albumsFound[album] = copyCmd

    return albumsFound


def backupAlbums(rcloneRemote, albumType, dest, fromDate, toDate):
    dprint("Getting gPhotos album data...")
    jsonData = getGphotosAlbumJson(rcloneRemote, albumType)
    albumsFound = findAlbumsUpdatedBetween(jsonData, rcloneRemote, albumType, dest, fromDate, toDate)
    dprint("Starting backup...")
    for dirName, eachCmd in albumsFound.items():
        dprint("# Backing up album: " + dirName)
        dprint("  Exec command: " + eachCmd)
        status = executeRcloneCopy(eachCmd)
        dprint("  Status: " + str(status))


def cleanupLogAndFiles():
    print("# Cleaning up files")
    os.remove(LOG_FILE_PATH)
    os.remove(GPHOTOS_ALBUM_JSON_FILE_PATH)

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
    # backupAlbums(args.remote, args.albumType, args.dest, args.dateFrom, args.dateTo)
    if (args.sm):
       sendLogViaEmail(args.smFrom, args.smTo, args.remote, args.albumType, args.dest, args.dateFrom, args.dateTo)
    if (args.clean):
       cleanupLogAndFiles()
