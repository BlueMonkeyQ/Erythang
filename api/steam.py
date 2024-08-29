import functions as f
import requests
from datetime import datetime
from db import supabase
steam_key = "14EB214CEC3F1701FD192885D330990F"


def getOwnedGames(steam_id):
    try:
        response = requests.request(method="GET", 
                                    url=f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_key}&steamid={steam_id}&format=json",)
        data = f.getData(response)
        return data
    except Exception as e:
        raise e

def getSteamGame(appid):
    try:
        response = requests.request(method="GET",
                                    url=f"http://store.steampowered.com/api/appdetails?appids={appid}")
        data = f.getData(response)
        return data
    except Exception as e:
        raise e

def insertSteamGame(app_id):
    game_data = getSteamGame(app_id)
    if game_data is None or game_data[str(app_id)]['success'] is False:
        return False
    game_data = game_data[str(app_id)]['data']

    # Work
    release_date = game_data.get('release_date', {}).get('date', None),
    if release_date is None or release_date[0] == '':
        release_date = None
    else:
        try:
            release_date = release_date[0].replace(',', "")
            release_date = datetime.strptime(release_date, "%b %d %Y")
            release_date = release_date.strftime("%m/%d/%Y")
        except ValueError:
            release_date = None

    supabase.from_("steamgames")\
    .insert({
        "app_id": app_id,
        "name": game_data.get('name',None),
        "type": game_data.get('type',None),
        "developers": game_data.get('developers',None),
        "publishers": game_data.get('publishers',None),
        "header_image": game_data.get('header_image',None),
        "url": f"https://store.steampowered.com/agecheck/app/{app_id}/",
        "price": game_data.get('price_overview', {}).get('final', None),
        "required_age": 0,
        "categories": [i.get('description', None) for i in game_data.get('categories', [])],
        "genres": [i.get('description', None) for i in game_data.get('genres', [])],
        "windows": game_data.get('platforms', {}).get('windows', None),
        "mac": game_data.get('platforms', {}).get('mac', None),
        "linux": game_data.get('platforms', {}).get('linux', None),
        "release_date": release_date,
        "recommendations": game_data.get('recommendations', {}).get('total', None)
    })\
    .execute()
    return

def getSteamUserGames(steam_id):
    data = getOwnedGames(steam_id)
    for i in data['response']['games']:
        app_id = i['appid']
        playtime_forever = i['playtime_forever']
        playtime_windows_forever = i['playtime_windows_forever']
        playtime_mac_forever = i['playtime_mac_forever']
        playtime_linux_forever = i['playtime_linux_forever']
        playtime_deck_forever = i['playtime_deck_forever']
        rtime_last_played = i['rtime_last_played']

        # Check if game exist in SteamGames db
        exist = supabase.from_("steamgames")\
        .select("id")\
        .eq(column="app_id", value=app_id)\
        .limit(size=1)\
        .execute().data

        if not exist:
            if insertSteamGame(app_id=app_id) is False:
                continue

        # Check if app_id exist in database for steam_id
        exist = supabase.from_("steamusergames")\
        .select("app_id")\
        .eq(column="steam_id", value=steam_id)\
        .eq(column="app_id", value=app_id)\
        .limit(size=1)\
        .execute().data

        if exist:
            supabase.from_("steamusergames")\
            .update({
                "playtime_forever": playtime_forever,
                "playtime_windows_forever": playtime_windows_forever,
                "playtime_mac_forever": playtime_mac_forever,
                "playtime_linux_forever": playtime_linux_forever,
                "playtime_deck_forever": playtime_deck_forever,
                "rtime_last_played": rtime_last_played
            })\
            .eq(column="steam_id", value=steam_id)\
            .eq(column="app_id", value=app_id)\
            .execute()
            
        else:
            supabase.from_("steamusergames")\
            .insert({
                "steam_id": steam_id,
                "app_id": app_id,
                "playtime_forever": playtime_forever,
                "playtime_windows_forever": playtime_windows_forever,
                "playtime_mac_forever": playtime_mac_forever,
                "playtime_linux_forever": playtime_linux_forever,
                "playtime_deck_forever": playtime_deck_forever,
                "rtime_last_played": rtime_last_played
            })\
            .execute()