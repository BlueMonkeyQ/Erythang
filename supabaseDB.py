import configparser
from supabase import create_client, Client
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')

supabaseUrl = config['credentials']['supabaseUrl']
supabaseKey = config['credentials']['supabaseKey']

class Supabase:
    def __init__(self):
        self.supabaseUrl = supabaseUrl
        self.supabaseKey = supabaseKey
        self.supabase: Client = create_client(supabaseUrl,supabaseKey)

# STEAM GAMES
    def existSteamGamesDB(self, appid):
        try:
            response = self.supabase.from_("steamgames")\
            .select("*")\
            .eq(column="app_id", value=appid)\
            .execute()
            data = response.data

            if data:
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return False

    def insertSteamGamesDB(self, app_id, data):
        try:
            if steam_appid := data.get('steam_appid'):
                steam_appid = steam_appid
            else:
                steam_appid = ""

            if name := data.get('name'):
                name = name
            else:
                name = ""

            if header_img := data.get('header_image'):
                header_img = header_img
            else:
                header_img = ""

            if capsule_image := data.get('capsule_image'):
                capsule_image = capsule_image
            else:
                capsule_image = ""

            if short_description := data.get('short_description'):
                short_description = short_description
            else:
                short_description = ""

            if developers := data.get('developers'):
                developers = ", ".join([developer for developer in developers])
            else:
                developers = ""

            if publishers := data.get('publishers'):
                publishers = ", ".join([publisher for publisher in publishers])
            else:
                publishers = ""

            if categories := data.get('categories'):
                categories = ", ".join([category['description'] for category in categories])
            else:
                categories = ""

            if genres := data.get('genres'):
                genres = ", ".join([genre['description'] for genre in genres])
            else:
                genres = ""

            if windows := data['platforms'].get('windows'):
                windows = bool(windows)
            else:
                windows = False

            if mac := data['platforms'].get('mac'):
                mac = bool(mac)
            else:
                mac = False

            if linux := data['platforms'].get('linux'):
                linux = bool(linux)
            else:
                linux = False

            if release_date := data['release_date'].get('date'):
                release_date = release_date
                try:
                    release_date = datetime.strptime(release_date, "%b %d, %Y").strftime("%m/%d/%Y")
                except ValueError as ve:
                    print(f"Error parsing release date: {ve}")
                    release_date = ""
            else:
                release_date = ""

            self.supabase.from_("steamgames")\
            .insert({
                "app_id": app_id,
                "steam_appid": steam_appid,
                "name": name,
                "header_img": header_img,
                "capsule_image": capsule_image,
                "short_description": short_description,
                "developers": developers,
                "publishers": publishers,
                "categories": categories,
                "genres": genres,
                "windows": windows,
                "mac": mac,
                "linux": linux,
                "release_date": release_date
            })\
            .execute()

        except Exception as e:
            print(e)
            return False

# STEAM USER GAMES
    def existSteamUserGamesDB(self, appid):
        try:
            response = self.supabase.from_("steamusergames")\
            .select("*")\
            .eq(column="app_id", value=appid)\
            .execute()
            data = response.data

            if data:
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return False


    def insertSteamUserGamesDB(self, data):
        try:
            self.supabase.from_("steamusergames")\
            .insert({
                "app_id": data['appid'],
                "playtime_forever": data['playtime_forever'],
                "playtime_windows_forever": data['playtime_windows_forever'],
                "playtime_mac_forever": data['playtime_mac_forever'],
                "playtime_linux_forever": data['playtime_linux_forever'],
                "playtime_deck_forever": data['playtime_deck_forever'],
                "rtime_last_played": data['rtime_last_played'],
            })\
            .execute()

        except Exception as e:
            print(e)
            return False

    def updateSteamUserGamesDB(self, data):
        try:
            self.supabase.from_("steamusergames")\
            .update({
                "playtime_forever": data['playtime_forever'],
                "playtime_windows_forever": data['playtime_windows_forever'],
                "playtime_mac_forever": data['playtime_mac_forever'],
                "playtime_linux_forever": data['playtime_linux_forever'],
                "playtime_deck_forever": data['playtime_deck_forever'],
                "rtime_last_played": data['rtime_last_played'],
            })\
            .eq(column="app_id", value=data['appid'])\
            .execute()

        except Exception as e:
            print(e)
            return False

    def getSteamUserGames(self):
        try:
            response = self.supabase.from_("steamusergames")\
            .select("*, steamgames(*)")\
            .execute()
            data = response.data

            return data

        except Exception as e:
            print(e)
            return False

# STEAM USER ACHIEVEMENTS
    def existSteamUserAchievementsDB(self, id):
        try:
            response = self.supabase.from_("steamuserachievements")\
            .select("*")\
            .eq(column="id", value=id)\
            .execute()
            data = response.data

            if data:
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return False

    def insertSteamUserAchievementsDB(self, id, data):
        try:
            self.supabase.from_("steamuserachievements")\
            .insert({
                "achievement_id": id,
                "achieved": data['achieved'],
                "unlocktime": data['unlocktime']
            })\
            .execute()

        except Exception as e:
            print(e)
            return False

    def updateSteamUserAchievementsDB(self, id, data):
        try:
            self.supabase.from_("steamuserachievements")\
            .update({
                "achieved": data['achieved'],
                "unlocktime": data['unlocktime']
            })\
            .eq(column='achievement_id',value=id)\
            .execute()

        except Exception as e:
            print(e)
            return False

# STEAM ACHIEVEMENTS
    def existSteamAchievementsDB(self, appid, name):
        try:
            response = self.supabase.from_("steamachievements")\
            .select("*")\
            .eq(column="app_id", value=appid)\
            .eq(column="name", value=name)\
            .execute()
            data = response.data

            if data:
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return False

    def insertSteamAchievementsDB(self, app_id, data):
        try:
            if name := data.get('name'):
                name = name
            else:
                name = ""

            if display_name := data.get('displayName'):
                display_name = display_name
            else:
                display_name = ""

            if hidden := data.get('hidden'):
                hidden = bool(hidden)
            else:
                hidden = False

            if icon := data.get('icon'):
                icon = icon
            else:
                icon = ""

            if icongray := data.get('icongray'):
                icongray = icongray
            else:
                icongray = ""

            self.supabase.from_("steamachievements")\
            .insert({
                "app_id": app_id,
                "name": name,
                "display_name": display_name,
                "hidden": hidden,
                "icon": icon,
                "icongray": icongray
            })\
            .execute()

        except Exception as e:
            print(e)
            return False

    def getSteamAchievements(self,app_id,name):
        try:
            response = self.supabase.from_("steamachievements")\
            .select("*")\
            .eq(column="app_id", value=app_id)\
            .eq(column="name", value=name)\
            .execute()
            data = response.data

            return data

        except Exception as e:
            print(e)
            return False

# GENERAL
    def steamLibraryDetailView(self, appid):
        try:
            response = self.supabase.from_("steamgames")\
            .select("*, steamusergames(*)")\
            .eq(column="app_id", value=appid)\
            .execute()
            data = response.data

            return data[0]

        except Exception as e:
            print(e)
            return False

    def steamLibraryAchivementsView(self,appid):
        try:
            response = self.supabase.from_("steamachievements")\
            .select("*, steamuserachievements(*)")\
            .eq(column="app_id", value=appid)\
            .execute()
            data = response.data

            return data

        except Exception as e:
            print(e)
            return False
