import aiohttp
import asyncio
import json
import os  
import configparser

config = configparser.ConfigParser()  
config.read(".global_config.ini")

def langs_list(): 
    with open(os.path.join('env','Lib','site-packages', '_yandex_detect','lang_list.json')) as f:
        templates = json.load(f)
        return templates
class Translate_errors(Exception):
    def __init__(self, m):
        self.message = m
    def __str__(self):
        return self.message
    
class Dedector:
    def __init__(self,  
                       langs_to_detect:list = "default", 
                       langs_hints:list = "default", 
                       detector_url:str = config["ya_services"]["url_translator"], 
                       api_key: str = config["ya_services"]["API_key"]):

        self.langs = [] # фильтр языков
        self.langs_hints =[] #Список наиболее вероятных языков для переводчика
        if  langs_to_detect == "default":
            self.langs_to_detect = langs_list()["langs_to_detect"]
        else:
            self.langs_to_detect =  langs_to_detect
        if langs_hints == "default":
            self.langs_hints =  langs_list()["langs_hints"]
        self.detector_url = detector_url
        self.api_key = api_key
        self.headers = {
                        "Content-Type": "application/json",
                        "Authorization":f"Api-Key {self.api_key}"}

             
    
    async def detect(self, text:str, filter=False):
            data ={
                 "text": text,
                 "languageCodeHints": self.langs_hints
            }
            async with aiohttp.ClientSession() as session, session.post(self.detector_url, json=data, headers=self.headers) as response:
                rs = response.status
                #print(rs)
                if rs == 200:
                        if filter == False:
                            return (await response.json())["languageCode"]
                        else:
                             language = (await response.json())["languageCode"]
                             if language == filter:
                                return True
                             elif filter == True:
                                if language in self.langs_to_detect:
                                     return True
                                else:
                                     return False
                             elif language != filter and filter != True:
                                return False 
                else:   
                        raise Translate_errors(f"error_code - {rs} \n {await response.text()}")

