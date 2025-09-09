import json
import requests
import Utilities.utils
from Utilities import *

STATUS = Utilities.utilitiesHelper.LOG_LEVEL.STATUS
INFO = Utilities.utilitiesHelper.LOG_LEVEL.INFO
WARNING = Utilities.utilitiesHelper.LOG_LEVEL.WARNING
ERROR = Utilities.utilitiesHelper.LOG_LEVEL.ERROR
CRITICAL = Utilities.utilitiesHelper.LOG_LEVEL.CRITICAL


class tmdb_connector:
    strAPIKey: str
    str_url: str
    strTitle: str
    str_year: str
    str_id: str
    CLASSNAME = "(tmdb)"
    bConnected: bool
    bCompleted: bool
    bIsTV: bool
    nFuzzyMatch: int

    def __init__(self, apiKey, bTV, bCompleted):
        self.strAPIKey = apiKey
        self.bConnected = False
        self.bCompleted = bCompleted
        self.str_id = ""
        self.bIsTV = bTV
        if( bTV ):
            self.str_type = "tv"
        else:
            self.str_type = "movie"
        self.nFuzzyMatch = 80

    def setFuzzy(self, fuzzy: int):
        self.nFuzzyMatch = fuzzy

    def get_search_url(self):
        title = replace_patterns(self.strTitle, " ", "+")
        strYear = self.str_year
        if (strYear != ""):
            strYear = f"&y:{strYear}"
        strType = 'tv' if self.bIsTV else 'movie'

#        return "https://api.themoviedb.org/3/search/" + 'tv' if self.bIsTV else 'movie' + "?query=" + title + strYear + "&api_key=" + self.strAPIKey
        return f"https://api.themoviedb.org/3/search/{strType}?query={title}{strYear}&api_key={self.strAPIKey}"

    def get_id_url(self):
        strType = 'tv' if self.bIsTV else 'movie'
#        return "https://api.themoviedb.org/3/" + 'tv' if self.bIsTV else 'movie' + "/" + self.str_id + "?api_key=" + self.strAPIKey
        return f"https://api.themoviedb.org/3/{strType}/{self.str_id}?api_key={self.strAPIKey}"

    def connect(self, strTitle: str, strYear: str):
        json_object = self.connect_title(strTitle, strYear)
        if (json_object is not None):
            return self.connect_id(str(get_jsonvalue(json_object, 'id')))
        return None

    def fuzzy_match_series(self, json_object):
        top_series = ""
        top_score = 0
        top_name: str = ""
        strTitle = self.strTitle
        str_year = self.str_year
        if (str_year != ""):
            str_year = getYear(str_year)
            strTitle = f"{strTitle} ({str_year})"

        for series in get_jsonvalue(json_object, 'results'):
            strName = get_jsonvalue(series, 'name' if self.bIsTV else 'title')
            strYear = get_year(series)
            if( strYear != ""):
                strYear = getYear(strYear)
                strName = f"{strName} ({strYear})"

            score = fuzzyMatchNoCase(strName, strTitle)
            if (score > top_score):
                top_score = score
                top_series = series
                top_name = strName
                if (top_score == 100):
                    break

        if (top_series != "" and top_score > self.nFuzzyMatch):
            strYear = get_year(top_series)
            if (strYear != ""):
                strYear = getYear(strYear)
                top_name = f"{top_name} ({strYear})"

            print_ex(WARNING, f"{top_name} - {self.CLASSNAME} Fuzzy Matching series score {top_score} ")
            return top_series
        else:
            print_ex(WARNING, f"{top_name} - {self.CLASSNAME}  Cannot find Match in results score {top_score}")
        return ""

    def fuzzy_match(self, json_object):
        return self.fuzzy_match_series(json_object)

    def connect_title(self, strTitle: str, strYear: str):
        self.strTitle = strTitle
        self.str_year = strYear
        url = self.get_search_url()

        try:
            response = requests.get(url)
        except:
            print_ex(CRITICAL, "requests.get: Exception error " + strTitle)
            return None

        if (response.status_code != 200):
            if (strYear != ""):
                return self.connect_title(strTitle, "")
            print_ex(WARNING, f"{strTitle} + {format_year_string(strYear)} + Connection Error in {self.CLASSNAME} {response.status_code}")
            return None

        json_object = json.loads(response.content)
        if (json_object is None):
            print_ex(WARNING, self.strTitle + format_year_string(self.str_year) +  " NOT Found in tmdb")
            return None

        if (get_jsonvalue(json_object, 'total_results') < 1):
            print_ex(WARNING, self.strTitle + format_year_string(self.str_year) + " No Results in tmdb")
            return None

        # let iterate through the list and do a fuzz match on title, return top match
        top_series = self.fuzzy_match(json_object)
        if (top_series != ""):
            return top_series

        #    for j in get_jsonvalue(json_object, 'results'):
        #        return tmdbSearchSeriesByID(get_jsonvalue(j, 'id'), strTitle, bCompleted)

        series = get_jsonvalue(json_object, 'results')[0]
        strName = get_jsonvalue(series, 'name' if self.bIsTV else 'title')
        print_ex(WARNING, f"{strName} - {self.CLASSNAME} Returning first result")

        return series

    def connect_id(self, strID: str):
        nID = int(strID)
        if (nID < 1 ):
            return None

        self.str_id = strID
        url = self.get_id_url()
        try:
            # fetching the series extended detail data
            # returns a dict
            response = requests.get(url)
        except:
            print_ex(CRITICAL, "get_series_extended: Exception error " + str(nID))
            return None

        if (response.status_code != 200):
            print_ex(WARNING, self.str_id + " Connection Error in tmdb " + str(response.status_code))
            return None

        json_object = json.loads(response.content)
        return json_object


    def search(self, strTitle, strYear):
        json_object = self.connect_title(strTitle, strYear)
        if (json_object is None):
            print_ex(WARNING, strTitle + " NOT Found in tmdb")
            return ""
        return self.searchSeries(get_jsonvalue(json_object, 'id'), strTitle)

    def searchSeries(self, ID: str, strTitle: str):
        json_object = self.connect_id(ID)
        if (json_object is None):
            print_ex(WARNING, ID + ": " + strTitle + " NOT Found in tmdb")
            return ""
        return get_jsonvalue(json_object, 'status')

    def process(self, json_object):
        if (json_object is None):
            return None

        #dict of list
        dict_container: dict = {}
        dict_container['series'] = json_object

        strStatus = get_jsonvalue( json_object, 'status')
        print_ex(WARNING, f"{self.strTitle} ({self.str_year}) - {self.CLASSNAME} status {strStatus}")


        """if (self.bCompleted is True):
            if (strStatus == "Returning Series"):
                print_ex(WARNING, f"{self.strTitle} ({self.str_year}) - {self.CLASSNAME} status {strStatus}")
        else:
            if (strStatus != "Returning Series"):
                print_ex(WARNING, f"{self.strTitle} ({self.str_year}) - {self.CLASSNAME} status {strStatus}")"""


        dict_container['status'] = strStatus

        lstLang: list = []
        get_value_from_tag_as_list(json_object, 'original_language', lstLang)
        lstSpokenLang: list = []
        list_spoken_lang = get_value_from_tag(json_object, 'spoken_languages')
        for languages in list_spoken_lang:
            get_value_from_tag_as_list(languages, 'english_name', lstLang)
        print_ex(WARNING, f"{self.strTitle} ({self.str_year}) - {self.CLASSNAME} languages {lstLang}")
        dict_container['languages'] = lstLang

        lstGenres: list = []
        get_value_from_tag_as_list(json_object, 'genres', lstGenres)
        print_ex(WARNING, f"{self.strTitle} ({self.str_year}) - {self.CLASSNAME} - genres {lstGenres}")
        dict_container['genres'] = lstGenres

        dict_container['year'] = get_year(json_object)

        return dict_container

    """
    def get_value_from_tag(self, json_object, strTag: str):
        if (json_object is None):
            return ""

        strValue = ""
        if(strTag == "genres"):
            for j in get_jsonvalue(json_object, 'genres'):
                strValue = strValue + "(" + get_jsonvalue(j, 'name') + ")"
            return strValue

        return get_jsonvalue(json_object, strTag)

    def get_value(self, dict_container:dict, strTag: str):

        if 'Series' in dict_container:
            json_object = dict_container['series']
            if (json_object is None):
                return ""

            strValue = ""
            if(strTag == "genres"):
                for j in get_jsonvalue(json_object, 'genres'):
                    strValue = strValue + "(" + get_jsonvalue(j, 'name') + ")"
                return strValue

            return get_jsonvalue(json_object, strTag)
        return ""

    def get_value_from_tag_as_list(self, json_object, strTag: str, lstValues: list):
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
    """
