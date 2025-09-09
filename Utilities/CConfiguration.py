import json
import requests
import Utilities.utils
from Utilities import *
import configparser
import ast


#two tiers
#1st tier section
#examples - config['Genres'] = {}
#2nd tier is the list or string of the values
#set_config_list('Animation', lstAnime, GenresConf)
#config['Path'] = {}
#PathConf = config['Path']
#PathConf['Documentary'] = strDocPath

class CConfiguration():
    #dict of dict
    type key_value_pair = tuple[int, str]
    type dict_value = tuple[str, tuple[int, str]]

    #first key = section header, example 'Genres'
    #first_value = dict {key, pair(int, value)} = {'Animation': lstAnimation, 'Family': lstFamily}
    #[Genres]
    #animation = ['Anime', 'Animation']
    #family = ['Family', 'Children']
    #first key = 'Genres'
    #first_value = dict {'animation', pair(1"for list", list ['Anime', 'Animation'])}
    #first key = 'Genres'
    #first_value = dict {'family', pair(1"for list", list ['Family', 'Children'])}
    #[Path]
    #documentary = Z:\Temp\Movies\Documentary
    #animation = Z:\Temp\Movies\Animation
    # first key = 'Path'
    # first_value = dict {'documentary', pair(0"for STRING", str"Z:\Temp\Movies\Documentary)}
    # first key = 'Path'
    # first_value = dict {'animation', pair(0"for STRING", str"Z:\Temp\Movies\Animation)}
    #m_dictConfig['Path']['documentary'] = (0"for STRING", str"Z:\Temp\Movies\Documentary)
    m_dictData: dict = {}
    #config: configparser = {}



    def __init__(self):
        self.m_dictData = {}

    def write(self, strFilename: str):

        config = configparser.ConfigParser()

        for section_key, section_value in self.m_dictData.items():
            #section
            config[section_key] = {}
            section_config = config[section_key]
            for tag_key, tag_value in section_value.items():
                #if(tag_value[0] == 0 ):
                tag_value = str(tag_value)
                config[section_key][tag_key] = tag_value


        with open(strFilename, 'w') as configfile:
            config.write(configfile)


    def read(self, strFilename: str):
        config = configparser.ConfigParser()
        config.read(strFilename)
        config.sections()

        for section in config.sections():
            section_config = config[section]
            self.m_dictData[section] = {}
            for tag_key, tag_value in section_config.items():
                if(section.find('list') != -1):
                    tag_value = ast.literal_eval(tag_value)
                self.m_dictData[section][tag_key] = tag_value

        #print(self.m_dictData)



    def get_value(self, section: str, tag: str):
        if section in self.m_dictData:
            if tag in self.m_dictData[section]:
                return self.m_dictData[section][tag]
        return ""



