import tvdb_v4_official

#import json
#import requests
import Utilities.utils
from Utilities import *

STATUS = Utilities.utilitiesHelper.LOG_LEVEL.STATUS
INFO = Utilities.utilitiesHelper.LOG_LEVEL.INFO
WARNING = Utilities.utilitiesHelper.LOG_LEVEL.WARNING
ERROR = Utilities.utilitiesHelper.LOG_LEVEL.ERROR
CRITICAL = Utilities.utilitiesHelper.LOG_LEVEL.CRITICAL


class tvdb_connector():

    strAPIKey: str
    str_url: str
    strTitle: str
    str_year: str
    str_id: str
    CLASSNAME = "(tvdb)"
    bConnected: bool
    bCompleted: bool
    nFuzzyMatch: int
    season: int
    episode: int
    episode_aired: str

    def __init__(self, apiKey: str, bCompleted: bool):
        self.strAPIKey = apiKey
        self.strTitle = ""
        self.str_year = ""
        self.str_id = ""

        self.bConnected = False
        self.bCompleted = bCompleted
        self.nFuzzyMatch = 80

        self.season = 0
        self.episode = 0
        self.episode_aired = ""

    def init(self):
        if( self.bConnected is False ):
            try:
                self.tvdb = tvdb_v4_official.TVDB(self.strAPIKey)
                self.bConnected = True
                self.season = 0
                self.episode = 0
            except:
                self.bConnected = False
                print_ex(CRITICAL, "connect: Exception error ")


    def setFuzzy(self, fuzzy: int):
        self.nFuzzyMatch = fuzzy





    def fuzzy_match_series(self, response):
        top_series = ""
        top_score = 0
        top_name: str = ""
        strTitle = self.strTitle
        str_year = self.str_year
        if (str_year != ""):
            str_year = getYear(str_year)
            strTitle = f"{strTitle} ({str_year})"

        for series in response:
            strName = get_jsonvalue(series, 'name')
            strYear = get_year(series)

            if (strYear != ""):
                strYear = getYear(strYear)
                strName = f"{strName} ({strYear})"

            score = fuzzyMatchNoCase(strName, strTitle)
            if ( score > top_score):
                top_score = score
                top_series = series
                top_name = strName
                if( top_score == 100):
                    break


        if (top_series != "" and top_score > self.nFuzzyMatch):
            print_ex(WARNING, f"{top_name} - {self.CLASSNAME} Fuzzy Matching series score {top_score}")
            return top_series
        else:
            print_ex(WARNING, f"{top_name} - {self.CLASSNAME}  Cannot find Match in results score {top_score}")
            return ""

    def fuzzy_match_aliases(self, response):
        top_series = ""
        top_score = 0
        top_name: str = ""

        strTitle = self.strTitle
        str_year = self.str_year
        if (str_year != ""):
            str_year = getYear(str_year)
            strTitle = f"{strTitle} ({str_year})"

        for series in response:
            strName = get_jsonvalue(series, 'name')
            strYear = get_year(series)

            if (strYear != ""):
                strYear = getYear(strYear)

            for aliases in get_jsonvalue(series, 'aliases'):
                if (strYear != ""):
                    aliases = f"{aliases} ({strYear})"

                score = fuzzyMatchNoCase(aliases, strTitle)
                if (score > top_score):
                    top_score = score
                    top_series = series
                    top_name = strName

                    if (top_score == 100 ):
                        print_ex(WARNING, f"{top_name} - {self.CLASSNAME} Fuzzy Matching aliases score {top_score}")
                        return top_series

        if(top_series != "" and top_score > self.nFuzzyMatch):
            print_ex(WARNING, f"{top_name} - {self.CLASSNAME} Fuzzy Matching aliases score {top_score}")
            return top_series
        else:
            return ""

    def fuzzy_match_translations(self, response):
        top_series = ""
        top_score = 0
        top_name: str = ""

        strTitle = self.strTitle
        str_year = self.str_year
        if (str_year != ""):
            str_year = getYear(str_year)
            strTitle = f"{strTitle} ({str_year})"

        for series in response:
            strName = get_jsonvalue(series, 'name')
            strYear = get_year(series)

            if (strYear != ""):
                strYear = getYear(strYear)

            translations = get_jsonvalue(series, 'translations')
            if (translations is not None):
                for key, value in translations.items():
                    if (strYear != ""):
                        value = f"{value} ({strYear})"

                    score = fuzzyMatchNoCase(value, strTitle)
                    if (score > top_score):
                        top_score = score
                        top_series = series
                        top_name = value

                        if (top_score == 100):
                            print_ex(WARNING, f"{top_name} - {self.CLASSNAME} Fuzzy Matching translations score {top_score}")
                            return top_series

        if (top_series != "" and top_score > self.nFuzzyMatch):
            print_ex(WARNING, f"{top_name} - {self.CLASSNAME} Fuzzy Matching translations score {top_score}")
            return top_series
        else:
            return ""


    def fuzzy_match(self, response):
        series = self.fuzzy_match_series(response)
        if(series != ""):
            return series

        series = self.fuzzy_match_aliases(response)
        if (series != ""):
            return series

        series = self.fuzzy_match_translations(response)
        if (series != ""):
            return series

        print_ex(WARNING, f"Cannot find Match in results for {self.CLASSNAME} {self.strTitle}")
        return ""

    def connect(self, strTitle: str, strYear: str):
        json_object = self.connect_title(strTitle, strYear)
        if( json_object is not None):
            return self.connect_id(get_jsonvalue( json_object, 'tvdb_id'))
        return None


    def connect_title(self, strTitle: str, strYear: str):
        self.strTitle = strTitle
        self.str_year = strYear
        self.init()

        try:
            if (strYear != ""):
                nYear = int(strYear)
                response = self.tvdb.search(strTitle, year=nYear, type='series')
                if (len(response) < 1):
                    return self.connect_title(strTitle, "")

            else:
                response = self.tvdb.search(strTitle, type='series')
        except:
            print_ex(CRITICAL, "connect_tvdb: Exception error " + strTitle)
            return None

        if (len(response) < 1):
            print_ex(WARNING, f"{strTitle} + {format_year_string(strYear)} + Connection Error in {self.CLASSNAME}")
            return None

        # let iterate through the list and do a fuzz match on title
        series = self.fuzzy_match(response)

        if( series != ""):
            return series

        print_ex(WARNING, f"Cannot find Match in results for {self.CLASSNAME} {self.strTitle}")

        series = response[0]
        strName = get_jsonvalue(series, 'name')
        print_ex(WARNING, f"Returning first result for {self.CLASSNAME} {strName}")
        return series


    def connect_id(self, ID: str):
        nID = int(ID)
        if (nID < 1 ):
            return None

        self.init()
        self.str_id = ID

        try:
            # fetching the series extended detail data
            # returns a dict
            response = self.tvdb.get_series_extended(nID)
            # check to see if something came back
            # there can only be 1
            if (len(response) < 1):
                print_ex(WARNING, str(nID) + " Connection Error in tvdb")
                return None

            season_ignore_list = []
            seasons = get_jsonvalue(response, 'seasons')
            self.get_season_details(seasons, season_ignore_list)

        except:
            print_ex(CRITICAL, "get_series_extended: Exception error " + str(nID))
            return None

        return response


    def get_season_details(self, seasons, season_ignore_list: list):

        if (len(seasons) > 0):
            top_season = None
            top_num = -1
            for season in seasons:
                type = get_jsonvalue(season, 'type')
                number = get_jsonvalue(season, 'number')
                id: int = get_jsonvalue(type, 'id')
                if (id == 1 and number > top_num and number not in season_ignore_list):
                    top_num = number
                    top_season = season

            if (top_season is not None):
                seasonID = get_jsonvalue(top_season, 'id')
                season_number = get_jsonvalue(top_season, 'number')

                season_response = self.tvdb.get_season_extended(seasonID)
                if (len(season_response) > 0):
                    episodes_list = get_jsonvalue(season_response, 'episodes')
                    episode_index = len(episodes_list) - 1
                    if (episode_index >= 0 and episodes_list is not None):
                        episode_number = get_jsonvalue(episodes_list[episode_index], 'number')
                        episode_aired = get_jsonvalue(episodes_list[episode_index], 'aired')
                        self.season = season_number
                        self.episode = episode_number
                        self.episode_aired = episode_aired

                        print_ex(STATUS, f"{self.strTitle} ({self.str_year}) - {self.CLASSNAME} Season {season_number} Episode {episode_number} Aired {episode_aired}")
                        return True
                    else:
                        season_ignore_list.append(top_num)
                        return self.get_season_details(seasons, season_ignore_list)
        return False

    def get_all_season_details(self, seasons):
        seasons_dict: dict = {}
        if (len(seasons) > 0):
            for season in seasons:
                type = get_jsonvalue(season, 'type')

                id: int = get_jsonvalue(type, 'id')
                if (id == 1 ):
                    seasonID = get_jsonvalue(season, 'id')
                    season_number: int = get_jsonvalue(season, 'number')
                    if(season_number > 0):
                        season_response = self.tvdb.get_season_extended(seasonID)
                        if (len(season_response) > 0):
                            episodes_list = get_jsonvalue(season_response, 'episodes')

                            max_episode: dict  = {}
                            max_number: int  = -1
                            for episode in episodes_list:
                                episode_number = get_jsonvalue(episode, 'number')
                                if( episode_number > max_number):
                                    max_number = episode_number
                                    max_episode = episode

                            if( max_number < 0 ):
                                continue

                            episode_number: int = get_jsonvalue(max_episode, 'number')
                            episode_aired = get_jsonvalue(max_episode, 'aired')
                            season_dict: dict = {}
                            season_dict['season_number'] = season_number
                            season_dict['episode_number'] = episode_number
                            season_dict['episode_aired'] = episode_aired
                            seasons_dict[season_number] = season_dict

        return seasons_dict

    def search(self, strTitle, strYear):
        #do search with year first
        json_object = self.connect_title(strTitle, strYear)
        if( json_object is None):
            #since no result came back, try same search withour year
            if( strYear != ""):
                json_object = self.connect_title(strTitle, "")

            if (json_object is None):
                print_ex(WARNING, strTitle + " NOT Found in tvdb")
                return ""

            print_ex(WARNING, strTitle + " " + get_jsonvalue(json_object, 'year') + " NEW YEAR")

        return self.searchSeries(str(get_jsonvalue( json_object, 'tvdb_id')), strTitle)


    def searchSeries(self, ID: str, strTitle: str):
        json_object = self.connect_id(ID)
        # check to see if something came back
        if (json_object is None):
            print_ex(WARNING,  ID + ":" + strTitle + " NOT Found in tvdb")
            return ""
        return get_jsonvalue( get_jsonvalue( json_object, 'status'), 'name')

    def process (self, json_object):
        if (json_object is None):
            return None

        # dict of list
        dict_container: dict = {}

        dict_container['series'] = json_object

        strStatus = get_jsonvalue(get_jsonvalue(json_object, 'status'), 'name')
        print_ex(WARNING, f"{self.strTitle} ({self.str_year}) - {self.CLASSNAME} status {strStatus}")
        dict_container['status'] = strStatus

        lstLang: list = []
        get_value_from_tag_as_list(json_object, 'originalLanguage', lstLang)
        print_ex(WARNING, f"{self.strTitle} ({self.str_year}) - {self.CLASSNAME} languages {lstLang}")
        dict_container['languages'] = lstLang

        lstGenres: list = []
        get_value_from_tag_as_list(json_object, 'genres', lstGenres)
        print_ex(WARNING, f"{self.strTitle} ({self.str_year}) - {self.CLASSNAME} genres {lstGenres}")
        dict_container['genres'] = lstGenres

        seasons_dict: dict = {}
        seasons = get_jsonvalue(json_object, 'seasons')
        seasons_dict = self.get_all_season_details(seasons)
        dict_container['seasons'] = seasons_dict

        maxCount: int = 0

        for season in seasons_dict.values():
            #season = seasons_dict[keys]
            season_num = season['season_number']
            if( season_num > maxCount ):
                self.episode_aired = season['episode_aired']
                maxCount = self.season = season_num
                self.episode = season['episode_number']

        dict_container['year'] = get_year(json_object)
        dict_container['episode_aired'] = self.episode_aired

        dict_container['season_number'] = self.season
        dict_container['episode_number'] = self.episode


        return dict_container

