import json
import os

from lib.myLogging import log

class BotData:
    def __init__(self):
        self.filename = "./data/botdata.json"
        self.data = self.__populate_data__()

    def __populate_data__(self):
        starter_data = {
            "TaskHour": 8,
            "DailyWordIndex": 0,
            "DailyGrammarIndex": 0,
            "DailyWordChannelID": 0,
            "DailyGrammarChannelID": 0
        }
        
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                _data = json.load(file)
                log("Bot data successfully loaded.")
                return _data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            if isinstance(e, FileNotFoundError):
                os.makedirs(os.path.dirname(self.filename), exist_ok=True)
                with open(self.filename, "w", encoding="utf-8") as file:
                    json.dump(starter_data, file, indent=4, ensure_ascii=False)
                log("No bot data found. New data file created with starter values.")
                return starter_data
            elif isinstance(e, json.JSONDecodeError):
                log("Critical error reading bot data. Creating backup of damaged data.")
                with open(self.filename, "r", encoding="utf-8") as file:
                    _data = file.read()
                with open("./data/damagedBotData.json", "w", encoding="utf-8") as backup:
                    backup.write(_data)
                with open(self.filename, "w", encoding="utf-8") as file:
                    json.dump(starter_data, file, indent=4, ensure_ascii=False)
                return starter_data
    
    def _save_bot_data(self):
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)
            log("Dumped data to botdata.")
    
    @property
    def taskHour(self):
        return self.data["TaskHour"]

    @taskHour.setter
    def taskHour(self, value):
        self.data["TaskHour"] = value

    @property
    def dailyWordIndex(self):
        return self.data["DailyWordIndex"]
    
    @dailyWordIndex.setter
    def dailyWordIndex(self, value):
        self.data["DailyWordIndex"] = value
    
    @property
    def dailyGrammarIndex(self):
        return self.data["DailyGrammarIndex"]
    
    @dailyGrammarIndex.setter
    def dailyGrammarIndex(self, value):
        self.data["DailyGrammarIndex"] = value

    @property
    def dailyGrammarChannelID(self):
        return self.data["DailyGrammarChannelID"]
    
    @property
    def dailyWordChannelID(self):
        return self.data["DailyWordChannelID"]
    
    def incrementWordIndex(self):
        self.dailyWordIndex += 1
        log(f"Daily word count was incremented to {self.dailyGrammarIndex}.")
        self._save_bot_data()

    def incrementGrammarIndex(self):
        self.dailyGrammarIndex += 1
        log(f"Daily grammar count was incremented to {self.dailyGrammarIndex}.")
        self._save_bot_data()