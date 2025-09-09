import re
import os
from pathlib import Path
import shutil
import filecmp

from thefuzz import fuzz
from colorama import Fore
from enum import IntEnum


#lstResolution = ["1080p", "2160p", "720p", "480p"]
#lstDots = [".", " [", "] ", "[", "]", " (", ") ", "(", ")", "  "]
#lstVersion = ["SUBBED", "DUBBED", "REMASTERED", "EXTENDED", "STV", "UNCUT", "UNCENSORED", "IMAX", "PROPER", "AMZN",
#              "UNRATED", "DOCU", "HULU", "DC", "DF", "US", "EN", "INTERNAL", "COLORIZED", "RESTORED", "EXTRAS",
#              "THEATRICAL", "REMASTER", "RERIP", "VERSION", "CRITERION", "SHOUT", "SHORT", "ENSUBBED", "AMZN", "WS",
#              "FS", "OAR"]
#lstLanguage = ["JAPANESE", "GERMAN", "DUTCH", "SWEDISH", "SPANISH", "KOREAN", "CHINESE", "ITALIAN", "FINNISH", "DANISH",
#               "PORTUGUESE", "NORWEGIAN", "BASQUE ", "THAI", "FRENCH", "RUSSIAN", "HEBREW", "VIETNAMESE", "INDONESIAN",
#               "MALAY", "POLISH", "TAGALOG", "HUNGARIAN", "TIBETAN", "ARABIC", "MACEDONIAN", "UKRAINIAN", "ARAMAIC",
#               "PERSIAN", "TURKISH", "ALBANIAN", "ABORIGINAL", "GEORGIAN", "GREEK", "CZECH", "FILIPINO"]
#lstTags = ["x265", "BluRay", "BLURAY", "WEBRip", "WEBRIP", "REPACK", "KINO", "PROPER", "WEB-DL", "THEATRICAL CUT",
#           "LIMITED", "REMASTERED", "REPACK BLURAY REMUX", "BLURAY REMUX", "RERIP", "HEVC", "The Animation"]
#
#lstGenres = ["Documentary", "Home and Garden", "Reality", "Food"]

class LOG_LEVEL(IntEnum):
    STATUS = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


log_global_var: int = 0

def set_log_level (level: int):
    global log_global_var
    log_global_var = level


def return_log_level():
    return log_global_var

def print_ex(log_type: LOG_LEVEL, statement: str):

    if log_type < log_global_var:
        return

    if( statement.isascii() is False ):
        statement = "{0}".format( str(statement.encode()) )

    match log_type:
        case LOG_LEVEL.STATUS:
            print(Fore.LIGHTYELLOW_EX + f"STATUS: {statement}")
        case LOG_LEVEL.INFO:
            print(Fore.CYAN + f"INFO: {statement}")
        case LOG_LEVEL.WARNING:
            print(Fore.LIGHTGREEN_EX + f"WARNING: {statement}")
        case LOG_LEVEL.ERROR:
            print(Fore.LIGHTRED_EX + f"ERROR: {statement}")
        case LOG_LEVEL.CRITICAL:
            print(Fore.MAGENTA + f"CRITICAL: {statement}")
        case _:
            print(Fore.WHITE + statement)


def get_jsonvalue(json_object, strTag):
    try:
        if strTag in json_object:
            return json_object[strTag]
        else:
            return ""
    except:
        print_ex(LOG_LEVEL.ERROR, "get_jsonvalue: Exception error " + str(strTag))
        return ""


# check to see if not directory and create a new directory and move file to it


def create_dir(strPath, debug = True):
#    if (strBasename != ""):
#        strPath = os.path.join(strPath, strBasename)

    if( os.path.isdir(strPath) is False):
        if (debug is False ):
            os.makedirs(strPath)
        return strPath
    return strPath

def is_dir(strPath: str, bCreate: bool = False, debug = True):


    if ( bCreate is True ):
        return create_dir(strPath, debug)

    if (os.path.isdir(strPath) ):
        return strPath
    return ""


"""

def create_dir(strRoot, strBasename):
    strPath = os.path.join(strRoot, strBasename)
    if( os.path.isdir(strPath) is False):
        os.mkdir(strPath)
        return strPath
    return ""
"""

#dest - Z:\Temp\TV\staging\ongoing\9-1-1 Lone Star (2020)
#source - Z:\Temp\TV\working\

#dest - Z:\Temp\TV\staging\ongoing\9-1-1 Lone Star (2020)
#source - Z:\Temp\TV\working\9-1-1 Lone Star (2020)\S05

def _move(source:str, destination: str  ):
    try:
        shutil.move(source, destination)
    except Exception as e:
        print_ex(LOG_LEVEL.CRITICAL, f"Unable to move directory {source} " + str(e))
        if (os.path.exists(source)):
            base_name = os.path.basename(source)
            dst_dir = os.path.join(destination, base_name)
            if (os.path.exists(dst_dir)):
                for src_dir, dirs, files in os.walk(source):
                    for dir_ in dirs:
                        src_ = os.path.join(source, dir_)
                        _move(src_, dst_dir )

                for file_ in files:
                    src_file = os.path.join(source, file_)
                    dst_file = os.path.join(dst_dir, file_)
                    if os.path.exists(dst_file):
                        # in case of the src and dst are the same file
                        #if filecmp.cmp(src_file, dst_file):
                        #    continue
                        os.remove(dst_file)
                    shutil.move(src_file, dst_dir)


    return True

def move(source:str, destination: str  ):
    try:
        shutil.move(source, destination)
    except Exception as e:
        print_ex(LOG_LEVEL.CRITICAL, f"Unable to move directory {source} " + str(e))
        if (os.path.exists(source)):
            base_name = os.path.basename(source)
            dst_dir = os.path.join(destination, base_name)
            if (os.path.exists(dst_dir)):
                for src_dir, dirs, files in os.walk(source):
                    for file_ in files:
                        src_file = os.path.join(source, file_)
                        dst_file = os.path.join(dst_dir, file_)
                        if os.path.exists(dst_file):
                            # in case of the src and dst are the same file
                            if filecmp.cmp(src_file, dst_file):
                                continue
                            os.remove(dst_file)
                        shutil.move(src_file, dst_dir)
                shutil.rmtree(source)


def move_dir(source: str, destination: str, debug = True):
    if (os.path.isdir(source) and os.path.isdir(destination)):
        if (debug is False):
            _move(source, destination)
            shutil.rmtree(source)
        return True
    return False


def rename_dir(source: str, destination: str, debug = True):
    # make sure the directory does not exist before renaming
    if (source != destination ):
        if( os.path.isdir(destination) is False):
            if (debug is False ):
                os.rename(source, destination)
            return True
    return False

def get_file_count(strDirectory: str, lstFileExtension: list ):
    lstParent = os.listdir(strDirectory)
    lstParent.sort()
    count = 0

    for strChild in lstParent:
        strChildPath = os.path.join(strDirectory, strChild)

        if (os.path.isdir(strChildPath) is False):
            _, ext = os.path.splitext(strChildPath)

            if( lstFileExtension.count(ext.lower()) > 0 ):
                count = count + 1


    return count


def replace_patternsinList(strFilename, lstPattern, strReplace=" "):
    for strPattern in lstPattern:
        #print(strPattern)
        strFilename = replace_patterns(strFilename, strPattern, strReplace)
    return strFilename


def replace_patterns(strFilename, strPattern, strReplace=" "):
    #strFilename = str(strFilename)
    if (strFilename.find(strPattern) > -1):
        strFilename = strFilename.replace(strPattern, strReplace)
    return strFilename


def remove_patternsinList(strFilename, lstPattern):
    return replace_patternsinList(strFilename, lstPattern, "")


def remove_patterns(strFilename, strPattern):
    return replace_patterns(strFilename, strPattern, "")

def getTitle(strFilename, strYear, strResolution):
    if (strYear == ""):
        if (strResolution == ""):
            return strFilename
        else:
            return strFilename[0:strFilename.find(strResolution) - 1]
    else:
        nIndex = strFilename.find(strYear)
        nResIndex = strFilename.find(strResolution)

        if (nResIndex > 0 and nResIndex < nIndex):
            nIndex = nResIndex

        return strFilename[0:nIndex - 1]


def formatTitle(strTitle):
    if (strTitle == ""):
        return strTitle

#    strTitle = remove_patternsinList(strTitle, lstTags)
#    strTitle = remove_patternsinList(strTitle, lstVersion)
    strTitle = remove_patterns(strTitle, "  ")
    return strTitle

def format_year_string(strYear):
    if (strYear != ""):
        strYear = " (" + strYear + ")"
    return strYear

def getYear(strFilename):
    if( strFilename == "" ):
        return ""

    strPattern = r"\b(19\d\d|20\d\d)\b"
    objMatch = re.search(strPattern, strFilename)

    if (objMatch is None):
        return ""

    return objMatch.group(0)

def format_season_string(season):
    season = season.strip()
    if( season == "" ):
        return ""

    pattern_list = [r"\d{1,4}\b", r"\d\d\b", r"\d\b", r"\d\d\d\b"]
    for pattern in pattern_list:
        objMatch = re.search(pattern, season)

        if (objMatch is not None):
            strSeason = objMatch.group(0)
           # strSeason = format(int(strSeason), '02d')
            strSeason = f"S{int(strSeason):02d}"

            return strSeason

    return ""


def get_year(series):
    if(series is None):
        return ""
    strYear = get_jsonvalue(series, 'release_date')
    if (strYear == ""):
        strYear = get_jsonvalue(series, 'year')

    return getYear(strYear)

def formatResolution(strResolution):
    if (strResolution != ""):
        strResolution = " [" + strResolution + "]"
    return strResolution


def getResolution(strFilename: str, lstResolution: list):
    for strPattern in lstResolution:
        if (strFilename.find(strPattern) > -1):
            return strPattern

    return ""

def fuzzyMatchNoCase(str1, str2):
    str1 = str1.casefold()
    str2 = str2.casefold()
    ratio = fuzz.ratio(str1, str2)
    partial_ratio = 0#fuzz.partial_ratio(str1, str2)
    token_sort_ratio = 0#fuzz.token_sort_ratio(str1, str2)
    token_set_ratio = fuzz.token_set_ratio(str1, str2)
    return max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)

def get_value_from_tag(json_object: dict, strTag: str):
    if (json_object is None):
        return ""

    strValue = ""
    if(strTag == "genres"):
        for j in get_jsonvalue(json_object, 'genres'):
            strValue = strValue + "(" + get_jsonvalue(j, 'name') + ")"
        return strValue

    return get_jsonvalue(json_object, strTag)

def get_value_from_tag_as_list(json_object: dict, strTag: str, lstValues: list):
    if (json_object is None):
        return 0

    if (strTag == "genres"):
        for j in get_jsonvalue(json_object, 'genres'):
            strValue = get_jsonvalue(j, 'name')
            if (strValue != ""):
                lstValues.append(strValue)
            # strGenres = strGenres + "(" + get_jsonvalue(j, 'name') + ")"
        return len(lstValues)

    strValue = get_jsonvalue(json_object, strTag)
    if (strValue != ""):
        lstValues.append(strValue)

    return len(lstValues)

def find_value_from_list(strTag: str, lstValues: list):
    if (len(lstValues) < 1):
        return False

    return strTag in lstValues

