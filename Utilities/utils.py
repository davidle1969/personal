import re
import os
from pathlib import Path

from thefuzz import fuzz
from colorama import Fore
from enum import Enum


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

class LOG_LEVEL(Enum):
    INFO = 1
    WARNING = 2
    CRITICAL = 3


def print_ex(log_type: int, statement: str):
    if( statement.isascii() is False ):
        statement = "{0}".format( str(statement.encode()) )

    match log_type:
        case 1:
            print(Fore.CYAN + "INFO: " + statement)
        case 2:
            print(Fore.LIGHTGREEN_EX + "WARNING: " + statement)
        case 3:
            print(Fore.RED + "ERROR: " + statement)
        case _:
            print(Fore.WHITE + statement)


def get_jsonvalue(json_object, strTag):
    try:
        if strTag in json_object:
            return json_object[strTag]
        else:
            return ""
    except:
        print_ex(3, "get_jsonvalue: Exception error " + str(strTag))
        return ""



def makeDir(strParent, strPath, strChild):
    strNewDir = os.path.join(strParent, Path(strPath).stem)
    #   strNewDir = os.path.join(strParent, strFilename)
    if (os.path.isdir(strNewDir) is False):
        os.mkdir(strNewDir)
    # src_path = os.path.join(source, f)
    dst_path = os.path.join(strNewDir, strChild)
    os.rename(strPath, dst_path)
    return strNewDir


def createDir(strRoot, strBasename):
    strPath = os.path.join(strRoot, strBasename)

    if (os.path.isdir(strPath) is False):
        os.mkdir(strPath)

    return strPath


def isDir(strPath: str, bCreate: bool = False):
    if (os.path.isdir(strPath) is False and bCreate):
        os.mkdir(strPath)

    return strPath
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
    if (strTitle is None):
        return strTitle

#    strTitle = remove_patternsinList(strTitle, lstTags)
#    strTitle = remove_patternsinList(strTitle, lstVersion)
    strTitle = remove_patterns(strTitle, "  ")
    return strTitle

def format_year(strYear):
    if (strYear != ""):
        strYear = " (" + strYear + ")"
    return strYear

def getYear(strFilename):
    strPattern = r"\b(19\d\d|20\d\d)\b"
    objMatch = re.search(strPattern, strFilename)

    if (objMatch is None):
        return ""

    return objMatch.group(0)


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
    partial_ratio = fuzz.partial_ratio(str1, str2)
    token_sort_ratio = fuzz.token_sort_ratio(str1, str2)
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
        return ""

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