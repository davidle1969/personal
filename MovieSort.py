# $ErrorActionPreference = "SilentlyContinue"
import os
#import sys
#import re
#from pathlib import Path
# importing shutil module

#import rottentomatoes as rottentoes
from bs4 import BeautifulSoup
# Non-local imports
#import json
import requests  # interact with RT website
#from typing import List, Union

# Project modules
from rottentomatoes import search
#from rottentomatoes import utils
#import configparser
#import ast

#from thefuzz import fuzz
from colorama import init

import Utilities
from Utilities import *
from Connectors import *

INFO = Utilities.utilitiesHelper.LOG_LEVEL.INFO.value
WARNING = Utilities.utilitiesHelper.LOG_LEVEL.WARNING.value
CRITICAL = Utilities.utilitiesHelper.LOG_LEVEL.CRITICAL.value

REQUEST_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) "
        "Gecko/20100101 Firefox/12.0"
    ),
    "Accept-Language": "en-US",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html",
    "Referer": "https://www.google.com"}

def get_ar_from_RT(movie_name: str):
    try:
        search_result = search.top_movie_result(movie_name)
        rt_url = search_result.url

        strTitle = rt_url
        strTitle = replace_patterns(strTitle, "https://www.rottentomatoes.com/m/", "")
        strTitle = replace_patterns(strTitle, "_", " ")
        if( fuzzyMatchNoCase(strTitle, movie_name) < 80 ):
            print_ex(CRITICAL, f"Rotten Tomatoes match not found {movie_name}.")
            return ""



        response = requests.get(rt_url, headers=REQUEST_HEADERS)

        if response.status_code == 404:
            print_ex(CRITICAL, f"Unable to find {movie_name} on Rotten Tomatoes.")
            return ""

        soup = BeautifulSoup(response.text, features="html.parser")
        value = soup.find("rt-button", {"slot": "audienceScore"})
        if( len(value) > 0 ):
            score = value.text
            score = replace_patternsinList(score, ['\n', '%'], "")
            return score

    except:
        print_ex(CRITICAL, f"ERROR in ROTTEN TOTAMTOES {movie_name} ")

    return ""


def get_rotten_tomatoes_user_rating(movie_name: str):
    movie_name = replace_patterns(movie_name, " ", "_")
    try:
        url = f"https://www.rottentomatoes.com/m/{movie_name}"
        # Send a GET request to the URL
        response = requests.get(url)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the user rating element

#        user_rating_element = soup.find('span', {'class': 'audience-score'})
        user_rating_element = soup.find("rt-button", {"slot": "audienceScore"})

        # Extract the user rating value
        if user_rating_element:
            user_rating_text = user_rating_element.text.strip()
            user_rating = float(user_rating_text.replace('%', ''))
            return user_rating
        else:
            print_ex(CRITICAL, f"Rotten Tomatoes match not found {movie_name}.")
            return 0
    except (requests.exceptions.RequestException, ValueError):
        return 0



def formatYear(tmdb_movies, strYear ):
    if (strYear == ""):
        strYear = get_value_tmdb(tmdb_movies, 'release_date')
        if (strYear == ""):
            return ""
        strYear = getYear(strYear)

    if (strYear != ""):
        strYear = " (" + strYear + ")"
    return strYear


def get_value_tmdb(tmdb_movies, strTag ):
    if (tmdb_movies is not None):
        return get_value_from_tag(tmdb_movies, strTag)
    return ""

def get_tmdb_json(strTitle, strYear, completed):
    tmdb_obj = tmdb_connector("7044f4a4f633505d060dc089aa6c1d9d", False, completed)
    json_obj =  tmdb_obj.connect(os.path.basename(strTitle), strYear)
    return tmdb_obj.process(json_obj)


def move_genres(strSource: str, strDest:str, lstFilter: list, lstClientTag: list, bCheck = True, debug = True):
    # lets move it to the proper directories base on genres
    if (strDest != ""):
        if (any( j in lstClientTag for j in lstFilter) is bCheck):
            try:
                move_dir(strSource, strDest, debug)
            except:
                print_ex(CRITICAL, f"Unable to MOVE {strSource} to {strDest}")
            return True
    return False


def process(strParent: str, strRoot: str):

    config = CConfiguration()
    config.read("example.cfg")

    debug = True if int(config.get_value("Options", "debug")) == 1 else False
    create_directory_from_file = True if int(config.get_value("Options", "debug")) == 1 else False
    completed = True if int(config.get_value("Options", "completed")) == 1 else False

    strDocPath = is_dir(config.get_value("Path", "documentary"))
    strAnimePath = is_dir(config.get_value("Path", "animation"))
    strFamilyPath = is_dir(config.get_value("Path", "family"))
    strAsianPath = is_dir(config.get_value("Path", "asian"))
    strForeignPath = is_dir(config.get_value("Path", "foreign"))
    #   strStagingPath = is_dir(testConfig.get_value("Path.string", "Staging"), True)
    strGenreStagingPath = create_dir(config.get_value("Path", "genre_staging"), debug)
    strRatingStagingPath = create_dir(config.get_value("Path", "rating_staging"), debug)
    strDurationStagingPath = create_dir(config.get_value("Path", "duration_staging"), debug)

    nRatingScore = int(config.get_value("Staging", "rating_score"))
    nDurationTime = int(config.get_value("Staging", "duration_time"))


    lstDots = config.get_value("Utilities.list", "dots")
    lstResolution = config.get_value("Utilities.list", "resolution")

    lstGenreStaging = config.get_value("Genres.list", "genre_staging_list")
    lstDoc = config.get_value("Genres.list", "documentary")
    lstFamily = config.get_value("Genres.list", "family")
    lstAnime = config.get_value("Genres.list", "animation")
    lstAsian = config.get_value("Genres.list", "asian")
    lstForeign = config.get_value("Genres.list", "not_foreign")


    lstParent = os.listdir(strParent)
    lstParent.sort()
    init(True)

    for strChild in lstParent:
        strChildPath = os.path.join(strParent, strChild)

        # check to see if not directory and create a new directory and move file to it
        if (os.path.isdir(strChildPath) is False):
            if( create_directory_from_file is True ):
                strChildPath = move_file(strParent, strChildPath, strChild, debug)
            else:
                continue

        strDirectory = strChildPath
        print_ex(INFO, strDirectory)
        strDirectory = replace_patternsinList(strDirectory, lstDots)
        strYear = getYear(strDirectory)
        strResolution = getResolution(strDirectory, lstResolution)
        strTitle = getTitle(strDirectory, strYear, strResolution)

        strTitle = formatTitle(strTitle)
        strBaseName = os.path.basename(strTitle)
        tmdb_movies: dict = get_tmdb_json(strBaseName, strYear, completed)
        if( tmdb_movies is not None):
            strYear = formatYear(tmdb_movies['series'], strYear)

        strResolution = formatResolution(strResolution)
        strDirectory = strTitle + strYear + strResolution

        # make sure the directory does not exist before renaming
        try:
            #new name was formated, not try to rename it from old Childpath to new Directory
            if( rename_dir(strChildPath, strDirectory, debug) is True ):
                print_ex(INFO, f"Rename {strChildPath} to {strDirectory}")
            else:
                print_ex(CRITICAL, f"Unable to Rename {strChildPath} to {strDirectory}, Directory already exist")

        except:
            print_ex(CRITICAL, f"Exception ERROR Unable to Rename {strChildPath} to {strDirectory}")

        #check to see if path exist
        if ( os.path.isdir(strDirectory) is False) :
            print_ex(CRITICAL, f"Destination is not a directory {strDirectory}")
            continue

        if( tmdb_movies is not None ):
            # check runtime
            strRunTime = str(get_value_tmdb(tmdb_movies['series'], 'runtime'))
            if( strRunTime != "" and int(strRunTime) < nDurationTime ):
                try:
                    move_dir(strDirectory, strDurationStagingPath, debug)
                    print_ex(CRITICAL, f"Move to DURATION STAGING ({strBaseName}) - RUNTTIME {strDurationStagingPath}")
                except:
                    print_ex(CRITICAL, f"Unable to Move to DURATION STAGING {strBaseName} to {strDurationStagingPath}")
                continue

            # check to see if it's on the genre filter list
            if (len(lstGenreStaging) > 0):
                if( move_genres(strDirectory, strGenreStagingPath, lstGenreStaging, tmdb_movies['genres'], True, debug) ):
                    print_ex(CRITICAL, f"Move to GENRE  STAGING ({strBaseName}) - STAGING_LIST {tmdb_movies['genres']}")
                    continue


            #check user rating from Rotten Tomatoes
#            strUserRating = str(get_rotten_tomatoes_user_rating(f"{strBaseName}{strYear}" if strYear != "" else strBaseName))
            strUserRating = get_ar_from_RT(f"{strBaseName}{strYear}" if strYear != "" else strBaseName)
            if( strUserRating is not None and len(strUserRating) > 0 ):
                nRating = int(strUserRating)
                if (nRating < nRatingScore):
                      try:
                          move_dir(strDirectory, strRatingStagingPath, debug)
                          print_ex(CRITICAL, f"Move to RT SCORE STAGING ({strBaseName}) - ROTTEN_TOMATOES_RATING {nRating}")
                          continue
                      except:
                          print_ex(CRITICAL, f"Unable to Move to SCORE STAGING {strBaseName} to {strRatingStagingPath} {nRating}")
# check user rating from TMDB
            strUserRating = str(get_value_tmdb(tmdb_movies['series'], 'vote_average'))
            if (len(strUserRating) > 0):
                f_rating = float(strUserRating) * 10.0
                if (strUserRating != "" and f_rating < float(nRatingScore)):
                    try:
                        move_dir(strDirectory, strRatingStagingPath, debug)
                        print_ex(CRITICAL, f"Move to TMDB SCORE STAGING ({strBaseName}) - TMDB_RATING {f_rating}")
                    except:
                        print_ex(CRITICAL, f"Unable to Move to SCORE STAGING {strBaseName} to {strRatingStagingPath}  {f_rating}")
                    continue

            #lets move it to the proper directories base on genres
            if( len(tmdb_movies['genres']) > 0 ):
                if(move_genres(strDirectory, strDocPath, lstDoc, tmdb_movies['genres'], True, debug) is True):
                    print_ex(CRITICAL, f"MOVE {strDirectory} to {strDocPath}")
                    continue
                if(move_genres(strDirectory, strFamilyPath, lstFamily, tmdb_movies['genres'], True, debug) is True):
                    print_ex(CRITICAL, f"MOVE {strDirectory} to {strFamilyPath}")
                    continue
                if (move_genres(strDirectory, strAnimePath, lstAnime, tmdb_movies['genres'], True, debug) is True):
                    print_ex(CRITICAL, f"MOVE {strDirectory} to {strAnimePath}")
                    continue

            if(len(tmdb_movies['languages']) > 0 ):
                if (move_genres(strDirectory, strAsianPath, lstAsian, tmdb_movies['languages'], True, debug) is True):
                    print_ex(CRITICAL, f"MOVE {strDirectory} to {strAsianPath}")
                    continue
                if (move_genres(strDirectory, strForeignPath, lstForeign, tmdb_movies['languages'], False, debug) is True):
                    print_ex(CRITICAL, f"MOVE {strDirectory} to {strForeignPath}")
                    continue

        print_ex(INFO, f"{strBaseName} - NOTHING MOVED")


process("Z:\\Temp\\Movies\\Sorted\\", "Z:\\Temp\\Movies\\")
