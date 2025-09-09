#import tvdb_v4_official
#import json
#import requests
import re
import os
#import re
#from thefuzz import fuzz
#from colorama import init
from pathlib import Path

import Utilities
from Utilities import *
from Connectors import *

from colorama import init
from datetime import datetime

STATUS = Utilities.utilitiesHelper.LOG_LEVEL.STATUS
INFO = Utilities.utilitiesHelper.LOG_LEVEL.INFO
WARNING = Utilities.utilitiesHelper.LOG_LEVEL.WARNING
ERROR = Utilities.utilitiesHelper.LOG_LEVEL.ERROR
CRITICAL = Utilities.utilitiesHelper.LOG_LEVEL.CRITICAL

class CTVSort():
    m_dictSettings: dict = {}

    def __init__(self):
        init(True)


    def load_config(self, strFile: str):
        config = CConfiguration()
        config.read(strFile)

        self.m_dictSettings['working'] = is_dir(config.get_value("Path", "path"))
        self.m_dictSettings['debug'] = True if int(config.get_value("Options", "debug")) == 1 else False
        self.m_dictSettings['completed'] = True if int(config.get_value("Options", "completed_series")) == 1 else False
        self.m_dictSettings['create_directory_from_file'] = True if int(config.get_value("Options", "create_directory_from_file")) == 1 else False

        """
        self.m_dictSettings['documentary'] = is_dir(config.get_value("Path", "documentary"))
        self.m_dictSettings['animation'] = is_dir(config.get_value("Path", "animation"))
        self.m_dictSettings['asian'] = is_dir(config.get_value("Path", "asian"))
        self.m_dictSettings['foreign'] = is_dir(config.get_value("Path", "foreign"))
        """

        self.m_dictSettings['documentary.current'] = self.create_subdirectories(config.get_value("Path", "documentary"), "current")
        self.m_dictSettings['documentary.complete'] = self.create_subdirectories(config.get_value("Path", "documentary"), "complete")
        self.m_dictSettings['animation.current'] = self.create_subdirectories(config.get_value("Path", "animation"), "current")
        self.m_dictSettings['animation.complete'] = self.create_subdirectories(config.get_value("Path", "animation"), "complete")
        self.m_dictSettings['asian.current'] = self.create_subdirectories(config.get_value("Path", "asian"), "current")
        self.m_dictSettings['asian.complete'] = self.create_subdirectories(config.get_value("Path", "asian"), "complete")
        self.m_dictSettings['foreign.current'] = self.create_subdirectories(config.get_value("Path", "foreign"), "current")
        self.m_dictSettings['foreign.complete'] = self.create_subdirectories(config.get_value("Path", "foreign"), "complete")

        self.m_dictSettings['staging.current'] = self.create_subdirectories(config.get_value("Path", "staging"), "current")
        self.m_dictSettings['staging.complete'] = self.create_subdirectories(config.get_value("Path", "staging"), "complete")
        self.m_dictSettings['staging.ongoing'] = self.create_subdirectories(config.get_value("Path", "staging"), "ongoing")

        #self.m_dictSettings['staging'] = is_dir(config.get_value("Path", "staging"))
        self.m_dictSettings['dots_list'] = config.get_value("Utilities.list", "dots")

    #    self.m_dictSettings['complete_staging'] = is_dir(config.get_value("Path", "complete_staging"))
    #    self.m_dictSettings['current_staging'] = is_dir(config.get_value("Path", "current_staging"))



        self.m_dictSettings['documentary_list'] = config.get_value("Genres.list", "documentary")
        self.m_dictSettings['animation_list'] = config.get_value("Genres.list", "animation")
        self.m_dictSettings['asian_list'] = config.get_value("Genres.list", "asian")
        self.m_dictSettings['not_foreign_list'] = config.get_value("Genres.list", "not_foreign")
        self.m_dictSettings['series_title'] = config.get_value("Series.list", "series_title")
        self.m_dictSettings['seasons'] = config.get_value("Series.list", "seasons")




        self.m_dictSettings['tvdb_api'] = config.get_value("keys", "tvdb")
        self.m_dictSettings['tmdb_api'] = config.get_value("keys", "tmdb")

        self.m_dictSettings['extension_list'] = config.get_value("Extension.list", "extension")

        self.m_dictSettings['log_level'] = config.get_value("logging", "level")
        set_log_level(int(self.m_dictSettings['log_level']))

    def create_subdirectories(self, strPath: str, strSubdirectory):
        if (os.path.isdir(strPath)):
            strPath = os.path.join(strPath, strSubdirectory)
            return is_dir(strPath, True, self.m_dictSettings['debug'])
        else:
            return is_dir(strPath, False, self.m_dictSettings['debug'])



    def tvdb_search(self, strTitle, strYear):
#        tvdb_obj = tvdb_connector("680296cd-b9ff-445f-bdcf-dd9325e424bc", completed)
        tvdb_obj = tvdb_connector(self.get_value('tvdb_api'), self.get_value('completed'))

        json_obj = tvdb_obj.connect(os.path.basename(strTitle), strYear)
        return tvdb_obj.process(json_obj)

    def tmdb_search(self, strTitle, strYear):
#        tmdb_obj = tmdb_connector("7044f4a4f633505d060dc089aa6c1d9d", True, completed)
        tmdb_obj = tmdb_connector(self.get_value('tmdb_api'), True, self.get_value('completed'))
        json_obj =  tmdb_obj.connect(os.path.basename(strTitle), strYear)
        return tmdb_obj.process(json_obj)

    def get_value(self, tag: str):
        if tag in self.m_dictSettings:
            return self.m_dictSettings[tag]
        return ""

    def get_value_tmdb(self, tmdb_movies, strTag ):
        if (tmdb_movies is not None):
            if strTag in tmdb_movies:
                return tmdb_movies[strTag]
        return ""

    def get_value_from_series(self, series_obj, strTag ):
        if (series_obj is not None):
            if 'series' in series_obj:
                if strTag in series_obj['series']:
                    return series_obj['series'][strTag]
        return ""



    def get_series_title(self, strPath: str):
        file_name = Path(strPath).stem
        file_name = replace_patternsinList(file_name, self.m_dictSettings['dots_list'])
        for pattern in self.m_dictSettings['series_title']:
            objMatch = re.search(pattern, file_name, re.IGNORECASE)
            if (objMatch):
                index = objMatch.start()
                if (index > 0):
                    file_name = file_name[:index]
                    break
        return file_name

    def get_series_season(self, strPath: str):
        file_name = Path(strPath).stem
        file_name = replace_patternsinList(file_name, self.m_dictSettings['dots_list'])
        for pattern in self.m_dictSettings['seasons']:
            objMatch = re.search(pattern, file_name, re.IGNORECASE)
            if (objMatch is not None):
                return objMatch.group(0)
        return ""

    def get_series_season_as_int(self, strPath: str):
        series_season: str = self.get_series_season(strPath)

        if (series_season != ""):
            season = re.findall(r"\d+", series_season)[0]
            return int(season)
        return 0



    def move_file(self, strPath: str, strChild: str):
        file_name = self.get_series_title(strPath)

        file_name = replace_patternsinList(file_name, self.m_dictSettings['dots_list'])
        file_name = file_name.strip()

        strYear = getYear(strPath)
        if( strYear != "" ):
            file_name = getTitle(file_name, strYear, "strResolution")
            file_name = f"{file_name} ({strYear})"

        season = format_season_string(self.get_series_season(strPath))
#        season = season.strip()
        dest = os.path.join(self.get_value('working'), file_name)

        if( season != "" ):
            dest = os.path.join(dest, season)

        #   strNewDir = os.path.join(strParent, strFilename)
        if (os.path.isdir(dest) is False):
            if (self.get_value('debug') is False):
                os.makedirs(dest)
        # src_path = os.path.join(source, f)
        dst_path = os.path.join(dest, strChild)
        if (self.get_value('debug') is False):
            if( os.path.isfile(dst_path) is False):
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


    def process_path(self, strTitle: str, strYear: str, strChildPath: str, dict_obj: dict):
        debug = True if int(self.get_value('debug')) == 1 else False
        if( strYear == "" and dict_obj is not None):
            strYear = get_year(dict_obj)
            if( strYear != "" ):
                print_ex(INFO, f"{strTitle} ({strYear}) new year found in TMDB")
                file_name = f"{strTitle} ({strYear})"
            else:
                print_ex(INFO, f"{strTitle} new year NOT found in TMDB")
                file_name = strTitle

            #destPath = os.path.join(self.get_value('working'), file_name)
            destPath = file_name
            try:
                if (strChildPath != destPath):
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
                strChildPath = self.move_file(strChildPath, strChild)



    def process_genres(self, strDirectory, tvdb_series):
        debug = True if int(self.get_value('debug')) == 1 else False
        lstGenres: list = self.get_value_tmdb(tvdb_series, 'genres')

        # lets move it to the proper directories base on genres
        if (len(lstGenres) > 0):
            staging = self.get_status_string('documentary', tvdb_series)
            if (self.move_genres(strDirectory, self.get_value(staging), self.get_value('documentary_list'),
                                 lstGenres, True, debug) is True):
                print_ex(CRITICAL, f"MOVE {strDirectory} to {self.get_value(staging)}")
                return True
            staging = self.get_status_string('animation', tvdb_series)
            if (self.move_genres(strDirectory, self.get_value(staging), self.get_value('animation_list'), lstGenres,
                                 True, debug) is True):
                print_ex(CRITICAL, f"MOVE {strDirectory} to {self.get_value(staging)}")
                return True

        return False

    def process_languages(self, strDirectory, tvdb_series):
        debug = True if int(self.get_value('debug')) == 1 else False
        lstLanguages: list = self.get_value_tmdb(tvdb_series, 'languages')

        if (len(lstLanguages) > 0):
            staging = self.get_status_string('asian', tvdb_series)
            if (self.move_genres(strDirectory, self.get_value(staging), self.get_value('asian_list'), lstLanguages,
                                 True, debug) is True):
                print_ex(CRITICAL, f"MOVE {strDirectory} to {self.get_value(staging)}")
                return True
            staging = self.get_status_string('foreign', tvdb_series)
            if (self.move_genres(strDirectory, self.get_value(staging), self.get_value('not_foreign_list'),
                                 lstLanguages, False, debug) is True):
                print_ex(CRITICAL, f"MOVE {strDirectory} to {self.get_value(staging)}")
                return True
        return False

    def get_status_string(self, tag, tvdb_series):
        if (get_value_from_tag(tvdb_series, 'status') == "Ended"):
            return f"{tag}.complete"
        else:
            return f"{tag}.current"


    def process_staging(self, strDirectory, tvdb_series):
        strStatus = get_value_from_tag(tvdb_series, 'status')

        if (strStatus == ""):
            print_ex(INFO, f"{strDirectory} Status not found")
            return False

        debug = True if int(self.get_value('debug')) == 1 else False
        staging = self.get_status_string('staging', tvdb_series)

        episode_aired = self.get_value_tmdb(tvdb_series, 'episode_aired' )
        if(episode_aired != "" and episode_aired is not None ):
            date1 = datetime.strptime(episode_aired, '%Y-%m-%d')
            date2 = datetime.now()

            if( date1 > date2): #some episodes have not aired
                staging = 'staging.ongoing'



        if (self.get_value(staging) != ""):
            try:
                move_dir(strDirectory, self.get_value(staging), debug)
                print_ex(CRITICAL, f"MOVE {strDirectory} to {self.get_value(staging)}")
                return True
            except:
                print_ex(CRITICAL, f"Unable to MOVE {strDirectory} to {self.get_value(staging)}")
        return False


    def check_completeness(self, strDirectory: str, tvdb_series: dict):
        lstParent = os.listdir(strDirectory)
        lstParent.sort()
        count = 0

        season_number = self.get_value_tmdb(tvdb_series, 'season_number')
        #season = format_season_string(season_number)
        episode_number = self.get_value_tmdb(tvdb_series, 'episode_number')

        for strChild in lstParent:
            strChildPath = os.path.join(strDirectory, strChild)
            if (os.path.isdir(strChildPath) is False):
                count = count + 1
            else:
                series_season = self.get_series_season(strChildPath)
                if(series_season != ""):
                    series_season = series_season[1:]

                    if(int(series_season) == season_number):
                        return self.check_completeness(strChildPath, tvdb_series)

        if( count != episode_number ):
            print_ex(ERROR, f"{strDirectory} Season {season_number} episodes {episode_number} has {count} files, ")

    def check_season_for_completeness(self, strDirectory: str, seasons_dict: dict):
        count: int = get_file_count(strDirectory, self.m_dictSettings['extension_list'])
        if(count == 0):
            return

        season: int = self.get_series_season_as_int(strDirectory)
        if( season == 0 ):
            season = 1

        if season in seasons_dict:
            season_dict: dict = seasons_dict[season]
            season_number = season_dict['season_number']
            episode_number = season_dict['episode_number']
            #episode_aired = season_dict['episode_aired']

            if (count > 0 and count != episode_number):
                print_ex(ERROR, f"{strDirectory} INCOMPLETE Season {season_number} - episodes {episode_number} has {count} files, ")


    def check_seasons_completeness(self, strDirectory: str, tvdb_series: dict):
        seasons_dict: dict = self.get_value_tmdb(tvdb_series, 'seasons')
        if( seasons_dict is None or seasons_dict == ""):
            return

        self.check_season_for_completeness(strDirectory, seasons_dict)
        lstParent = os.listdir(strDirectory)
        lstParent.sort()

        for strChild in lstParent:

            if(strChild.casefold() == str('Specials').casefold() or strChild.casefold() == str('Special').casefold()):
                continue

            strChildPath = os.path.join(strDirectory, strChild)
            if (os.path.isdir(strChildPath)):
                self.check_season_for_completeness(strChildPath, seasons_dict)


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
            strTitle = getTitle(strDirectory, strYear, "")

            strTitle = formatTitle(strTitle)
            strBaseName = os.path.basename(strTitle)

            #strStatus = ""
            tvdb_series = self.tvdb_search(strBaseName, strYear)

            if( tvdb_series is None ):
                tvdb_series = self.tmdb_search(strBaseName, strYear)

            if (tvdb_series is not None):

                (strDirectory, strYear) = self.process_path(strTitle, strYear, strChildPath, tvdb_series)
                self.check_seasons_completeness(strDirectory, tvdb_series)

                if (self.process_genres(strDirectory, tvdb_series)):
                    continue

                if (self.process_languages(strDirectory, tvdb_series)):
                    continue

                if (self.process_staging(strDirectory, tvdb_series)):
                    continue



