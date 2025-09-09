# $ErrorActionPreference = "SilentlyContinue"
import os
from pathlib import Path
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
import imdb
import time

#from rottentomatoes import utils
#import configparser
#import ast

#from thefuzz import fuzz
from colorama import init

import Utilities
from Utilities import *
from Connectors import *

STATUS = Utilities.utilitiesHelper.LOG_LEVEL.STATUS
INFO = Utilities.utilitiesHelper.LOG_LEVEL.INFO
WARNING = Utilities.utilitiesHelper.LOG_LEVEL.WARNING
ERROR = Utilities.utilitiesHelper.LOG_LEVEL.ERROR
CRITICAL = Utilities.utilitiesHelper.LOG_LEVEL.CRITICAL

REQUEST_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) "
        "Gecko/20100101 Firefox/12.0"
    ),
    "Accept-Language": "en-US",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html",
    "Referer": "https://www.google.com"}

class CMovieSort():
    m_dictSettings: dict = {}

    def __init__(self):
        init(True)

    def load_config(self, strFile: str):
        config = CConfiguration()
        config.read(strFile)

        self.m_dictSettings['working'] = is_dir(config.get_value("Path", "path"))
        debug = True if int(config.get_value("Options", "debug")) == 1 else False
        self.m_dictSettings['debug'] = debug
        self.m_dictSettings['create_directory_from_file'] = True if int(config.get_value("Options", "create_directory_from_file")) == 1 else False
        self.m_dictSettings['use_rotten_tomatoes'] = True if int(config.get_value("Options", "use_rotten_tomatoes")) == 1 else False
        self.m_dictSettings['use_imdb'] = True if int(config.get_value("Options", "use_imdb")) == 1 else False

        self.m_dictSettings['staging'] = is_dir(config.get_value("Path", "staging"))
        self.m_dictSettings['dots'] = config.get_value("Utilities.list", "dots")

        self.m_dictSettings['tvdb_api'] = config.get_value("keys", "tvdb")
        self.m_dictSettings['tmdb_api'] = config.get_value("keys", "tmdb")

        self.m_dictSettings['documentary'] = is_dir(config.get_value("Path", "documentary"))
        self.m_dictSettings['animation'] = is_dir(config.get_value("Path", "animation"))
        self.m_dictSettings['family'] = is_dir(config.get_value("Path", "family"))
        self.m_dictSettings['asian'] = is_dir(config.get_value("Path", "asian"))
        self.m_dictSettings['foreign'] = is_dir(config.get_value("Path", "foreign"))
        #   strStagingPath = is_dir(testConfig.get_value("Path.string", "Staging"), True)
        self.m_dictSettings['genre_staging'] = create_dir(config.get_value("Path", "genre_staging"), debug)
        self.m_dictSettings['rating_staging'] = create_dir(config.get_value("Path", "rating_staging"), debug)
        self.m_dictSettings['duration_staging'] = create_dir(config.get_value("Path", "duration_staging"), debug)

        self.m_dictSettings['rating_score'] = int(config.get_value("Staging", "rating_score"))
        self.m_dictSettings['duration_time'] = int(config.get_value("Staging", "duration_time"))

        self.m_dictSettings['dots_list'] = config.get_value("Utilities.list", "dots")
        self.m_dictSettings['resolution_list'] = config.get_value("Utilities.list", "resolution")

        self.m_dictSettings['genre_staging_list'] = config.get_value("Genres.list", "genre_staging_list")
        self.m_dictSettings['documentary_list'] = config.get_value("Genres.list", "documentary")
        self.m_dictSettings['family_list'] = config.get_value("Genres.list", "family")
        self.m_dictSettings['animation_list'] = config.get_value("Genres.list", "animation")
        self.m_dictSettings['asian_list'] = config.get_value("Genres.list", "asian")
        self.m_dictSettings['not_foreign_list'] = config.get_value("Genres.list", "not_foreign")

        self.m_dictSettings['tmdb_api'] = config.get_value("keys", "tmdb")

    def get_rotten_tomatoes_user_rating(self, movie_name: str):
        try:
            search_result = search.top_movie_result(movie_name)
            rt_url = search_result.url
            strTitle = rt_url
            strTitle = replace_patterns(strTitle, "https://www.rottentomatoes.com/m/", "")
            strTitle = replace_patterns(strTitle, "_", " ")
            if (fuzzyMatchNoCase(strTitle, movie_name) < 80):
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

    def get_imdb_user_rating(self, movie_name, year: str):
        try:
            lasttime = time.time()
            imdb_search = imdb.Cinemagoer()
            movies = imdb_search.search_movie(movie_name)
            starttime = time.time()

            print_ex(INFO, f"imdb search_movie = {starttime - lasttime}")

            for movie in movies:
                strTitle = movie['title']
                strYear = movie['year']
                movieID = movie.getID()

                if(strYear != "" ):
                    strTitle = f"{strTitle} ({strYear})"

                if (fuzzyMatchNoCase(strTitle, movie_name) > 80):
                    lasttime = time.time()

                    movie_byID = imdb_search.get_movie(movieID)
                    starttime = time.time()
                    print_ex(INFO, f"imdb get_movie = {starttime - lasttime}")

                    rating = movie_byID.data['rating']
                    return rating * 10.0
        except:
            print_ex(CRITICAL, f"ERROR in IMDB {movie_name} ")
        return 0.0


    def formatYear(self, tmdb_movies, strYear ):
        if (strYear == ""):
            strYear = get_year(tmdb_movies)
        return format_year_string(strYear)


    def get_value_tmdb(self, tmdb_movies, strTag ):
        if (tmdb_movies is not None):
            if strTag in tmdb_movies:
                return tmdb_movies[strTag]
        return ""


    def get_value(self, tag: str):
        if tag in self.m_dictSettings:
            return self.m_dictSettings[tag]
        return ""

    def tmdb_search(self, strTitle, strYear):
#        tmdb_obj = tmdb_connector("7044f4a4f633505d060dc089aa6c1d9d", False, completed)
        tmdb_obj = tmdb_connector(self.get_value('tmdb_api'), False, self.get_value('completed'))

        json_obj =  tmdb_obj.connect(os.path.basename(strTitle), strYear)
        return tmdb_obj.process(json_obj)

    def move_title(self, strPath: str , strChild: str):
        file_name = Path(strPath).stem
        file_name = replace_patternsinList(file_name, self.m_dictSettings['dots'])
        file_name = file_name.strip()

        dest = os.path.join(self.get_value('working'), file_name)
        #   strNewDir = os.path.join(strParent, strFilename)
        if (os.path.isdir(dest) is False):
            if (self.get_value('debug') is False):
                os.makedirs(dest)
        # src_path = os.path.join(source, f)
        dst_path = os.path.join(dest, strChild)
        if (self.get_value('debug') is False):
            os.rename(strPath, dst_path)
        return dest


    def move_genres(self, strSource: str, strDest:str, lstFilter: list, lstClientTag: list, bCheck = True, debug = True):
        # lets move it to the proper directories base on genres
        if (strDest != ""):
            if (any( j in lstClientTag for j in lstFilter) is bCheck):
                try:
                    move_dir(strSource, strDest, debug)
                except:
                    print_ex(CRITICAL, f"Unable to MOVE {strSource} to {strDest}")
                return True
        return False

    def process_path(self, strTitle: str, strYear: str, strResolution: str, strChildPath: str, tmdb_movies):
        debug = True if int(self.get_value('debug')) == 1 else False
        if (tmdb_movies is not None):
            strYear = self.formatYear(self.get_value_tmdb(tmdb_movies, 'series'), strYear)
        else:
            if (strYear != ""):
                strYear = f" ({strYear})"

        strResolution = formatResolution(strResolution)
        destPath = strTitle + strYear + strResolution

        # make sure the directory does not exist before renaming
        # new name was formated, not try to rename it from old Childpath to new Directory
        try:
            if( strChildPath != destPath):
                if (rename_dir(strChildPath, destPath, debug) is True):
                    print_ex(INFO, f"{strChildPath} Renamed to {destPath}")
                    strChildPath = destPath
        except:
            print_ex(CRITICAL, f"{strChildPath} Unable to Rename to {destPath}")

        return (strChildPath, strYear)


    def process_files(self):
        lstParent = os.listdir(self.get_value('working'))
        lstParent.sort()

        for strChild in lstParent:
            strChildPath = os.path.join(self.get_value('working'), strChild)

            # check to see if not directory and create a new directory and move file to it
            if (os.path.isdir(strChildPath) is False):
                strChildPath = self.move_title(strChildPath, strChild)


    def process_ratings(self, strBaseName, strYear, strDirectory, tmdb_movies):
        debug = True if int(self.get_value('debug')) == 1 else False
        use_rotten_tomatoes = True if int(self.get_value('use_rotten_tomatoes')) == 1 else False
        use_imdb = True if int(self.get_value('use_imdb')) == 1 else False
        rating = 0.0

        if (use_rotten_tomatoes is True):
            # check user rating from Rotten Tomatoes
            strUserRating = self.get_rotten_tomatoes_user_rating(f"{strBaseName}{strYear}" if strYear != "" else strBaseName)
            if (len(strUserRating) > 0):
                rating = float(strUserRating)
                if (rating > 0.001 and rating < self.get_value('rating_score')):
                    try:
                        move_dir(strDirectory, self.get_value('rating_staging'), debug)
                        print_ex(CRITICAL,f"Move to RT SCORE STAGING ({strBaseName}) - ROTTEN_TOMATOES_RATING {rating}")
                        return True
                    except:
                        print_ex(CRITICAL,f"Unable to Move to SCORE STAGING {strBaseName} to {self.get_value('rating_staging')} {rating}")
        if (use_imdb is True):
            rating = self.get_imdb_user_rating(f"{strBaseName} {strYear}" if strYear != "" else strBaseName, strYear)
            if (rating > 0.001 and rating < self.get_value('rating_score')):
                try:
                    move_dir(strDirectory, self.get_value('rating_staging'), debug)
                    print_ex(CRITICAL, f"Move to IMDB SCORE STAGING ({strBaseName}) - IMDB {rating}")
                    return True
                except:
                    print_ex(CRITICAL,f"Unable to Move to SCORE STAGING {strBaseName} to {self.get_value('rating_staging')} {rating}")

            # check user rating from TMDB
        strUserRating = str(self.get_value_tmdb(self.get_value_tmdb(tmdb_movies, 'series'), 'vote_average'))
        if (len(strUserRating) > 0):
            rating = float(strUserRating) * 10.0
            if (rating > 0.001 and rating < self.get_value('rating_score')):
                try:
                    move_dir(strDirectory, self.get_value('rating_staging'), debug)
                    print_ex(CRITICAL, f"Move to TMDB SCORE STAGING ({strBaseName}) - TMDB_RATING {rating}")
                    return True
                except:
                    print_ex(CRITICAL,f"Unable to Move to SCORE STAGING {strBaseName} to {self.get_value('rating_staging')}  {rating}")

        return False

    def process_duration (self, strDirectory, tmdb_movies):
        debug = True if int(self.get_value('debug')) == 1 else False
        # check runtime
        strRunTime = str(self.get_value_tmdb(self.get_value_tmdb(tmdb_movies, 'series'), 'runtime'))
        if (strRunTime != "" and int(strRunTime) > 0 and int(strRunTime) < self.get_value('duration_time')):
            try:
                move_dir(strDirectory, self.get_value('duration_staging'), debug)
                print_ex(CRITICAL, f"{strDirectory} {strRunTime} minutes Moved to DURATION STAGING {self.get_value('duration_staging')}")
                return True
            except:
                print_ex(CRITICAL, f"{strDirectory} {strRunTime} minutes Unable to MOVE to DURATION STAGING {self.get_value('duration_staging')}")

        return False

    def process_staging(self, strDirectory, tmdb_movies):
        debug = True if int(self.get_value('debug')) == 1 else False
        genre_staging_list = self.get_value('genre_staging_list')
        series_genre_list = self.get_value_tmdb(tmdb_movies, 'genres')

        if (len(genre_staging_list) > 0):
            if ( self.move_genres(strDirectory, self.get_value('genre_staging'), genre_staging_list, series_genre_list, True, debug)):
                print_ex(CRITICAL,f"{strDirectory} Moved to GENRE STAGING STAGING_LIST {self.get_value_tmdb(tmdb_movies, 'genres')}")
                return True
        return False

    def process_genres(self, strDirectory, tmdb_movies):
        debug = True if int(self.get_value('debug')) == 1 else False
        lstGenres: list = self.get_value_tmdb(tmdb_movies, 'genres')

        if (len(lstGenres) > 0):
            if (self.move_genres(strDirectory, self.get_value('documentary'), self.get_value('documentary_list'),
                                 lstGenres, True, debug) is True):
                print_ex(CRITICAL, f"MOVE {strDirectory} to {self.get_value('documentary')}")
                return True
            if (self.move_genres(strDirectory, self.get_value('family'), self.get_value('family_list'), lstGenres, True,
                                 debug) is True):
                print_ex(CRITICAL, f"MOVE {strDirectory} to {self.get_value('family')}")
                return True
            if (self.move_genres(strDirectory, self.get_value('animation'), self.get_value('animation_list'), lstGenres,
                                 True, debug) is True):
                print_ex(CRITICAL, f"MOVE {strDirectory} to {self.get_value('animation')}")
                return True

        return False

    def process_languages(self, strDirectory, tmdb_movies):
        debug = True if int(self.get_value('debug')) == 1 else False
        lstLanguages: list = self.get_value_tmdb(tmdb_movies, 'languages')

        if (len(lstLanguages) > 0):
            if (self.move_genres(strDirectory, self.get_value('asian'), self.get_value('asian_list'), lstLanguages,
                                 True, debug) is True):
                print_ex(CRITICAL, f"MOVE {strDirectory} to {self.get_value('asian')}")
                return True
            if (self.move_genres(strDirectory, self.get_value('foreign'), self.get_value('not_foreign_list'),
                                 lstLanguages, False, debug) is True):
                print_ex(CRITICAL, f"MOVE {strDirectory} to {self.get_value('foreign')}")
                return True
        return False


    def process(self):

        if (self.m_dictSettings['create_directory_from_file'] is True):
            self.process_files()

        debug = self.get_value('debug')

        print_ex(INFO, f"Processing {self.get_value('working')}")

        lstParent = os.listdir(self.get_value('working'))
        lstParent.sort()

        for strChild in lstParent:
            strChildPath = os.path.join(self.get_value('working'), strChild)

            # check to see if not directory and create a new directory and move file to it
            if (os.path.isdir(strChildPath) is False):
                continue

            strDirectory = strChildPath
            print_ex(INFO, strDirectory)
            strDirectory = replace_patternsinList(strDirectory, self.get_value('dots_list'))
            strYear = getYear(strDirectory)
            strResolution = getResolution(strDirectory, self.get_value('resolution_list'))
            strTitle = getTitle(strDirectory, strYear, strResolution)

            strTitle = formatTitle(strTitle)
            strBaseName = os.path.basename(strTitle)

            tmdb_movies: dict = self.tmdb_search(strBaseName, strYear)

            if (tmdb_movies is not None):
                (strDirectory, strYear) = self.process_path(strTitle, strYear, strResolution, strChildPath, tmdb_movies)

           #check to see if path exist
            if ( os.path.isdir(strDirectory) is False) :
                continue

            if( tmdb_movies is not None ):
                # check runtime
                if(self.process_duration(strDirectory, tmdb_movies)):
                    continue

                # check to see if it's on the genre filter list
                if( self.process_staging(strDirectory, tmdb_movies) ):
                    continue

                if (self.process_genres(strDirectory, tmdb_movies)):
                    continue

                if (self.process_languages(strDirectory, tmdb_movies)):
                    continue

                if (self.process_ratings(strBaseName, strYear, strDirectory, tmdb_movies)):
                    continue

            print_ex(INFO, f"{strBaseName} - NOTHING MOVED")


#process("Z:\\Temp\\Movies\\Sorted\\", "Z:\\Temp\\Movies\\")
