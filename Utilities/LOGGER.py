#lstResolution = Utilities.utils.lstResolution
#lstDots = Utilities.utils.lstDots
#lstVersion = Utilities.utils.lstVersion
#lstLanguage = Utilities.utils.lstLanguage
#lstTags = Utilities.utils.lstTags

#lstDirectories = ["Documentary", "Family"]
#lstDirectories = ["Documentary", "Family"]
#lstDirectories = ["Documentary", "Family"]
#lstDoc = Utilities.utils.lstGenres
#lstAnime = ["Anime", "Animation"]
#lstFamily = ["Family", "Children"]
#lstAsian = ["ja", "tl", "id", "vi", "zh", "hi", "cn", "my", "th", "tl", "lo", "ko", "ta"]
#lstForeign = ["en"]
#lstStaging =["TV Movie", "Music"]



#        lstGenres = list()
#        lstLang = list()
 #       if (tmdb_movies is not None):
#            get_value_from_tag_as_list(tmdb_movies['series'], 'genres', lstGenres)
#            print(f"{strBaseName} - genres{lstGenres}")#
#
#            get_value_from_tag_as_list(tmdb_movies['series'], 'original_language', lstLang)
#            nLen = len(lstLang)
#
#            list_spoken_lang =  get_value_from_tag(tmdb_movies['series'], 'spoken_languages')
#
#            for languages in list_spoken_lang:
#                if( nLen < get_value_from_tag_as_list(languages, 'english_name', lstLang) ):
#                    #one was at least added
#                    break

#            print(f"{strBaseName} - language {lstLang}")



#        strLanguage = get_jsonvalue(json_object, 'original_language')
#        if (strLanguage != "en"):
#            print_ex(WARNING, self.strTitle + " - (tmdb) " + strLanguage)


        #    if (response['original_language'] != "usa"):
        #        print(strTitle + " = " + response['original_language'])

#        strGenres = ""
#        for j in get_jsonvalue(json_object, 'genres'):
#            strGenres = strGenres + "(" + get_jsonvalue(j, 'name') + ")"
#            if (get_jsonvalue(j, 'name') in lstGenres):
#                print_ex(WARNING, self.strTitle + " - (tmdb) " + strGenres)
#                break

"""
        strPattern = r"\b(S\d\dE\d\d)\b"
        objMatch = re.search(strPattern, file_name)
        if( objMatch ):
            index = objMatch.start() - 1
            if (index > 0 ):
                file_name = file_name[:index]
        else:
            strPattern = r"\b - \d\d\b"
            objMatch = re.search(strPattern, file_name)
            if (objMatch):
                index = objMatch.start() - 1
                if (index > 0):
                    file_name = file_name[:index]
            else:
                strPattern = r"\b S\d - \b"
                objMatch = re.search(strPattern, file_name)
                if (objMatch):
                    index = objMatch.start() - 1
                    if (index > 0):
                        file_name = file_name[:index]
        """



def writeConfig():
    config = configparser.ConfigParser()

    config['Utilities'] = {}
    UtilConf = config['Utilities']

    set_config_list('Resolution', lstResolution, UtilConf)
    set_config_list('Dots', lstDots, UtilConf)
    set_config_list('Version', lstVersion, UtilConf)
    set_config_list('Language', lstLanguage, UtilConf)
    set_config_list('Tags', lstTags, UtilConf)

#    config['Utilities']['Resolution'] = str(lstResolution)
#    config['Utilities']['Dots'] = str(lstDots)
#    config['Utilities']['Version'] = str(lstVersion)
#    config['Utilities']['Language'] = str(lstLanguage)
#    config['Utilities']['Tags'] = str(lstTags)

    config['Genres'] = {}
    GenresConf = config['Genres']


    set_config_list('Animation', lstAnime, GenresConf)
    set_config_list('Family', lstFamily, GenresConf)
    set_config_list('Asian', lstAsian, GenresConf)
    set_config_list('Staging', lstStaging, GenresConf)

    config['Path'] = {}
    PathConf = config['Path']
    PathConf['Documentary'] = strDocPath
    PathConf['Animation'] = strAnimePath
    PathConf['Family'] = strFamilyPath
    PathConf['Asian'] = strAsianPath
    PathConf['Foreign'] = strForeignPath
    PathConf['Staging'] = strStagingPath

    with open('example.cfg', 'w') as configfile:
        config.write(configfile)


def set_config_list(tag: str, value: list, config):
    return set_config_string(tag, str(value), config)

def set_config_string(tag: str, value: str, config):
    config[tag] = value
    return config[tag]

def get_config_list(tag: str, config):
    return ast.literal_eval(get_config_string(tag, config))

def get_config_string(tag: str, config):
    return config[tag]


def readConfig():
    config = configparser.ConfigParser()
    config.sections()
    config.read('example.cfg')
    config.sections()

    UtilConf = config['Utilities']
    lstResolution1 = get_config_list('Resolution', UtilConf)
    lstDots1 = get_config_list('Dots', UtilConf)
    lstVersion1 = get_config_list('Version', UtilConf)
    lstLanguage1 = get_config_list('Language', UtilConf)
    lstTags1 = get_config_list('Tags', UtilConf)

    GenresConf = config['Genres']
    lstAnime1 = get_config_list('Animation', GenresConf)
    lstFamily1 = get_config_list('Family', GenresConf)
    lstAsian1 = get_config_list('Asian', GenresConf)
    lstStaging1 = get_config_list('Staging', GenresConf)

    lstResolution = Utilities.utils.lstResolution
    lstDots = Utilities.utils.lstDots
    lstVersion = Utilities.utils.lstVersion
    lstLanguage = Utilities.utils.lstLanguage
    lstTags = Utilities.utils.lstTags

    # lstDirectories = ["Documentary", "Family"]
    # lstDirectories = ["Documentary", "Family"]
    # lstDirectories = ["Documentary", "Family"]
    lstDoc = Utilities.utils.lstGenres
    lstAnime = ["Anime", "Animation"]
    lstFamily = ["Family", "Children"]
    lstAsian = ["ja", "tl", "id", "vi", "zh", "hi", "cn", "my", "th", "tl", "lo", "ko", "ta"]
    lstForeign = ["en"]
    lstStaging = ["TV Movie", "Music"]
    lstScore = ["\n", "%"]


    for key in config['Utilities']:
        print(key)

    for key in config['Genres']:
        print(key)

    print(lstResolution1)
    print(lstDots1)
    print(lstVersion1)
    print(lstLanguage1)
    print(lstTags1)
    print(lstAnime1)
    print(lstFamily1)
    print(lstAsian1)
    print(lstStaging1)



def sort(strParent: str):
    lstParent = os.listdir(strParent)
    lstParent.sort()
    init(True)

    for strChild in lstParent:
        strChildPath = os.path.join(strParent, strChild)

        # check to see if not directory and create a new directory and move file to it
        if (os.path.isdir(strChildPath) is False):
            strChildPath = makeDir(strParent, strChildPath, strChild)

        strDirectory = strChildPath
        print_ex(INFO, strDirectory)
        strDirectory = replace_patternsinList(strDirectory, lstDots)
        strYear = getYear(strDirectory)
        strResolution = getResolution(strDirectory)
        strTitle = getTitle(strDirectory, strYear, strResolution)

        strTitle = formatTitle(strTitle)
        strBaseName = os.path.basename(strTitle)
        tmdb_movies = get_tmdb_json(strBaseName, strYear)
        strYear = formatYear(strTitle, strYear, tmdb_movies)

        strResolution = formatResolution(strResolution)
        strDirectory = strTitle + strYear + strResolution

        lstValues = list()
        if (tmdb_movies is not None):
            get_value_from_tag_as_list(tmdb_movies, 'genres', lstValues)
            print(f"{strBaseName} - {lstValues}")

        #make sure the directory does not exist before renaming
        if (strDirectory != strChildPath and os.path.isdir(strDirectory) is False ):
            os.rename(strChildPath, strDirectory)
    #        print_ex(INFO, "rename " + strDirectory)

        #check for for genres
