# Google Photos Albums Backup using RClone

This tool is to backup your **Albums** and **Shared Albums** based on a specified date range.

For example, when a day range is set between 2020-01-01 and 2020-12-31, any albums with images / videos that were created / modified between this range will be copied.

This tool uses RClone to get from Google Photos and to a local directory (or other cloud storage providers).

## Tested on
* Ubuntu Linux (Python 3.6.9)
* Microsoft Windows 10 (Python 3.7)
* Raspberry Pi OS (Python 3.7)


## Requirements

**Install RClone package:**

Click [here](https://rclone.org/downloads/) to download 

**Setup Google Photos with RClone**

Note: Make sure the rclone command is in PATH!

rclone config

## Checkout the Project and Setup Directory Structure

1. Checkout the project
```bash
demo$ git clone https://github.com/brianwoo/gphotos_rclone_backup.git
Cloning into 'gphotos_rclone_backup'...
remote: Enumerating objects: 55, done.
remote: Counting objects: 100% (55/55), done.
remote: Compressing objects: 100% (42/42), done.
remote: Total 55 (delta 15), reused 51 (delta 11), pack-reused 0
Unpacking objects: 100% (55/55), done.
```

2. Create a backup directory
```bash
mkdir backup
```

We have directory tree structure as the following:
```bash
demo$ tree -d -L 1 .
.
├── backup
└── gphotos_rclone_backup

2 directories
```

## To enable Gmail Support (Optional)

To enable Gmail support, you will need to install a Python package: **simplegmail**:
```bash
pip3 install simplegmail
```

You will also need to setup Gmail API access and authentication, please refer to this guide [here](SETUP_GMAIL.md).


## Backup Google Photos (Examples)

To start a backup, proceed from the backup directory we created earlier (if you need Gmail support).

```bash
backup$ python3 ../gphotos_rclone_backup/backup.py -h
usage: backup.py [-h] [-sm] [-smFrom SMFROM] [-smTo SMTO] [-clean]
                 remote {album,shared-album} dest dateFrom dateTo

GPhotos Backup Tool via RClone

positional arguments:
  remote                RClone remote
  {album,shared-album}  Supported album types
  dest                  Destination: dir or RClone remote
  dateFrom              From date YYYY-MM-DD
  dateTo                To date YYYY-MM-DD

optional arguments:
  -h, --help            show this help message and exit
  -sm                   Send log via Email?
  -smFrom SMFROM        If -sm is set, sender email addr is needed
  -smTo SMTO            If -sm is set, recipient email addr is needed
  -clean                Clean up log and other temp files downloaded

```

To backup any **Shared Albums** that have pictures created/modified between **2021-01-01** to **2021-01-31** (without clean-up and without email of backup status): 

Note: you can also backup albums by specifying **album** instead of **shared-album**.

```
backup$ python3 ../gphotos_rclone_backup/backup.py gphotos shared-album ./ \
          "2021-01-01" "2021-01-31"
Getting gPhotos album data...
Starting backup...
# Backing up album: 20201231 New Years Eve
  Exec command: rclone copy "gphotos:shared-album/20201231 New Years Eve" "20201231 New Years Eve"
  Status: True
```

The Shared Album has been backed up:
```bash
backup$ ls 
'20201231 New Years Eve'   backup-1610912365.txt   client_secret.json   
gmail_token.json           gphotos-1610912365.json

```

To backup any **Shared Albums** that have pictures created/modified between **2021-01-01** to **2021-01-31** (with **clean-up** and without email of backup status): 
```
backup$ python3 ../gphotos_rclone_backup/backup.py gphotos shared-album ./ \
          "2021-01-01" "2021-01-31" -clean
Getting gPhotos album data...
Starting backup...
# Backing up album: 20201231 New Years Eve
  Exec command: rclone copy "gphotos:shared-album/20201231 New Years Eve" "20201231 New Years Eve"
  Status: True
# Cleaning up files
```

The Shared Album has been backed up (log and meta files cleaned up):
```bash
backup$ ls 
'20201231 New Years Eve'   client_secret.json   gmail_token.json

```

To backup any **Shared Albums** that have pictures created/modified between **2021-01-01** to **2021-01-31** (with **clean-up** and **email support**): 
```
backup$ python3 ../gphotos_rclone_backup/backup.py gphotos shared-album ./ \
          "2021-01-01" "2021-01-31" -clean \
          -sm -smFrom "me@gmail.com" -smTo "my.recipient@gmail.com"

Getting gPhotos album data...
Starting backup...
# Backing up album: 20201231 New Years Eve
  Exec command: rclone copy "gphotos:shared-album/20201231 New Years Eve" "20201231 New Years Eve"
  Status: True
# Send Log Via Email (my.recipient@gmail.com)
# Cleaning up files
```

You should receive an email:

![email_sample](/assets/email_sample.png)


Since we are using RClone to manage different cloud providers, we can also use a RClone remote as a destination:
```
backup$ python3 ../gphotos_rclone_backup/backup.py gphotos shared-album dropbox:backup \
          "2021-01-01" "2021-01-31" 
```
