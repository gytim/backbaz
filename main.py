# -*- coding: UTF-8 -*-

from pathlib import Path
from datetime import datetime, timedelta
import sys
import os
import shutil

import GlobalParams as GP
 
def systemSlash(oS):
    if oS == 'win':
        GP.CURR_OS = oS
        GP.ROOT_DIR = GP.ROOT_DIR.replace(GP.SLASH_OS, '\\')
        GP.SLASH_OS = '\\'
    elif oS == 'lin':
        GP.CURR_OS = oS
        GP.SLASH_OS = '/'
        GP.ROOT_DIR = GP.ROOT_DIR.replace(GP.SLASH_OS, '/')


# создание бекапа
def createBackup(backupdir, base):
    currDate = datetime.now()

    dateDIC = {"year": currDate.year,
               "month": currDate.month if currDate.month > 9 else "0" + str(currDate.month),
               "day": currDate.day if currDate.day > 9 else "0" + str(currDate.day),
               "hour": currDate.hour if currDate.hour > 9 else "0" + str(currDate.hour),
               "minute": currDate.minute if currDate.minute > 9 else "0" + str(currDate.minute)}

    nameFolder = GP.FORMAT_NAME.format(**dateDIC)
    pathToBackup = backupdir + GP.SLASH_OS + nameFolder
	
    os.putenv('PGPASSWORD', GP.PASSWORD_PSQL)

    if not os.path.exists(str(pathToBackup)):
        os.makedirs(str(pathToBackup))

    if GP.CURR_OS == 'win':
        command_dump = '"C:\\Program Files (x86)\\PostgreSQL\\9.5\\bin\\pg_dump.exe"'
    elif GP.CURR_OS == 'lin':
        command_dump = "pg_dump"
		
    print(command_dump)
		
    os.system(command_dump + " -Fp -h {host} -U {user} %(name)s > %(pathbackup)s"
              .format(**settingsPostgres(base, backupdir))
              % {"name": base,
                 "pathbackup": pathToBackup + GP.SLASH_OS + "_backup_in_progress.sql"}
              )

    shutil.move(pathToBackup + GP.SLASH_OS + "_backup_in_progress.sql", pathToBackup + GP.SLASH_OS + "backup.sql")


# удаление папки (путь, дни, дельта)
def removeFolder(path, DAY, olddays):
    if not os.path.exists(path): print("path not found"); return

    dirs = Path(path)
    # т.к. день у нас всегда в одном месте находим обрезкой
    for dir in dirs.iterdir():
        if dir.is_dir():
            dirname = str(dir).replace(str(path) + GP.SLASH_OS, "")

            if len(dirname) == 13:  
                if not dirname[6:8] in DAY:
                    fileDate = datetime.strptime(dirname[:8], "%Y%m%d").date()

                    if (datetime.now().date() - fileDate).days > olddays:
                        shutil.rmtree(str(dir))
                        print("Удалено:" + str(dir))


# сборка настроек для команды postgres в словарь
def settingsPostgres(base, backupdir):
    settings = {"host": GP.HOST_PSQL,
                "user": GP.USERNAME_PSQL,
                "base": base,
                "dir": backupdir}

    return settings


if __name__ == '__main__':
    systemSlash('win')
	
    # первая база
    base = 'base'
    DAYS = ['07', '17', '27']
    oldDay = 20
    backupDir = GP.ROOT_DIR + GP.SLASH_OS + base

    removeFolder(backupDir, DAYS, oldDay)
    createBackup(backupDir, base)

    sys.exit(0)
