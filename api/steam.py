import functions as f
import requests
import configparser
from datetime import datetime

class SteamAPI:
    def __init__(self, steam_key):
        self.steam_key = steam_key

    def getAppList(self):
        # This takes literally years to run
        return None
        try:
            response = requests.request(method="GET",
                                        url="https://api.steampowered.com/ISteamApps/GetAppList/v2/")
            data = response.json()
            if response.status_code == 200:
                return data
            else:
                raise Exception

        except Exception as e:
            print(e)
            return False

    def appDetails(self, appid):
        try:
            response = requests.request(method="GET",
                                        url=f" http://store.steampowered.com/api/appdetails?appids={appid}")
            data = response.json()

            if response.status_code == 200 and data[str(appid)]['success'] == True:
                return data
            else:
                raise Exception

        except Exception as e:
            print(e)
            return False

    def getOwnedGames(self,steam_id):
            try:
                response = requests.request(method="GET",
                                            url=f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={self.steam_key}&steamid={steam_id}&format=json",)
                data = f.getData(response)
                return data
            except Exception as e:
                return False

    def getUserAchievements(self,steam_id,app_id):
        try:
            response = requests.request(method="GET",
                                        url=f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={app_id}&key={self.steam_key}&steamid={steam_id}")
            data = f.getData(response)
            return data
        except Exception as e:
            return False

    def getAchievements(self,app_id):
        try:
            response = requests.request(method="GET",
                url=f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v0002/?key={self.steam_key}&appid={app_id}&l=english&format=json")
            data = f.getData(response)

            try:
                if data['game']['availableGameStats']['achievements']:
                    return data
                else:
                    return False
            except KeyError as e:
                    print("-- Key Error: ", e)
                    return False

        except Exception as e:
            return False
