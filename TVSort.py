#import tvdb_v4_official
#import json
#import requests
import os
#import re
#from thefuzz import fuzz
from colorama import init

import Utilities
from Utilities import *
from Connectors import *

from colorama import init

INFO = Utilities.utilitiesHelper.LOG_LEVEL.INFO.value
WARNING = Utilities.utilitiesHelper.LOG_LEVEL.WARNING.value
CRITICAL = Utilities.utilitiesHelper.LOG_LEVEL.CRITICAL.value


def get_tvdb_json(strTitle, strYear, completed):
    tvdb_obj = tvdb_connector("680296cd-b9ff-445f-bdcf-dd9325e424bc", completed)
    json_obj = tvdb_obj.connect(os.path.basename(strTitle), strYear)
    return tvdb_obj.process(json_obj)

def get_tmdb_json(strTitle, strYear, completed):
    tmdb_obj = tmdb_connector("7044f4a4f633505d060dc089aa6c1d9d", True, completed)
    json_obj =  tmdb_obj.connect(os.path.basename(strTitle), strYear)
    return tmdb_obj.process(json_obj)


def process(strParent: str):
    config = CConfiguration()
    config.read("tv.cfg")

    debug = True if int(config.get_value("Options", "debug")) == 1 else False
    completed = True if int(config.get_value("Options", "completed_series")) == 1 else False

    strStaging = is_dir(config.get_value("Path", "staging"))
    lstDots = config.get_value("Utilities.list", "dots")
#    lstResolution = config.get_value("Utilities.list", "resolution")


    lstParent = os.listdir(strParent)
    lstParent.sort()
    init(True)

    for strChild in lstParent:
        strChildPath = os.path.join(strParent, strChild)

        # check to see a directory
        if (os.path.isdir(strChildPath) is False):
            continue

        strDirectory = strChild
        print_ex(INFO, strDirectory)
        strDirectory = replace_patternsinList(strDirectory, lstDots)
        strYear = getYear(strDirectory)
        strTitle = getTitle(strDirectory, strYear, "")

        strTitle = formatTitle(strTitle)
        strBaseName = os.path.basename(strTitle)

        if( strYear == "" ):
            print_ex(INFO, strTitle + " MISSING YEAR")
        strStatus = ""
        tvdb_series = get_tvdb_json(strBaseName, strYear, completed)
        if( tvdb_series is not None ):
            strStatus = get_value_from_tag(tvdb_series, 'status')
            if (find_value_from_list("eng", tvdb_series['languages']) is False or len(tvdb_series['languages']) < 1):
                get_tmdb_json(strBaseName, strYear, completed)
        else:
            tmdb_series = get_tmdb_json(strBaseName, strYear, completed)
            strStatus = get_value_from_tag(tmdb_series, 'status')

        if( strStatus == "" )
            continue

        move_genre: bool = False

        if (completed):
            if (strStatus == "Continuing" or strStatus == "Returning Series"):
                move_genre = True
        else:
            if (strStatus != "Continuing" and strStatus != "Returning Series"):
                move_genre = True

        if( move_genre is True):
            if (strStaging != ""):
                try:
                    move_dir(strChildPath, strStaging, debug)
                    print_ex(CRITICAL, f"MOVE {strChildPath} to {strStaging}")
                except:
                    print_ex(CRITICAL, f"Unable to MOVE {strChildPath} to {strStaging}")




#process("Z:\\TV\\Documentary\\Completed\\")
#process("Z:\\TV\\Documentary\\Curtent\\")

#Sort("Z:\\TV\\TV Completed Series\\", True)
process("Z:\\TV\\TV Current Season\\")
#process("Z:\\TV\\TV\\")
#process("Z:\\TV\\Foreign\\Completed")
#Sort("Z:\\TV\\Foreign\\Current", True)
#Sort("Z:\\TV\\Asian\\Completed", True)
#Sort("Z:\\TV\\Asian\\Current", False)

#process("Z:\\Temp\\TV\\TV Completed Series\\")
