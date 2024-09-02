import streamlit as st
import configparser
import pandas as pd
from api.steam import SteamAPI
from supabaseDB import Supabase

config = configparser.ConfigParser()
config.read('config.ini')
steam_key = config['steam']['steamKey']
steam_id = "76561198050437739"
steamapi = SteamAPI(steam_key)

supabase = Supabase()

st.set_page_config(page_title="Steam", page_icon=":video_game:")

@st.cache_data
def get_steam_user_library():
    return supabase.getSteamUserGames()

def steamView():
    steamGamesView()
    updateSteamLibrary()

def steamGamesView():
    df = pd.DataFrame()
    records = get_steam_user_library()

    if records is False:
        st.write("Error getting Steam User Games")
        return False

    for record in records:
        row = pd.DataFrame([record])
        df = pd.concat([df,row], ignore_index=True)
    df = df.sort_values(by='playtime_forever', ascending=False)


    st.dataframe(df)

def updateSteamLibrary():
    if st.button("Update Steam Library"):
        games = steamapi.getOwnedGames(steam_id=steam_id)
        if games is False:
            st.write("Error getting Steam Library")
            return False

        with st.spinner(f'Updating Steam Library...'):

            for i, game in enumerate(games['response']['games']):
                app_id = game['appid']
                print(f"{i:>4}/{len(games['response']['games']):<4} app_id ", app_id)

                # DB SteamGames
                print("++ DB SteamGames")
                if supabase.existSteamGamesDB(app_id) is False:
                    app_detail = steamapi.appDetails(app_id)

                    if app_detail is False:
                        print(f"Error appDetails {app_id}")
                        continue
                    else:
                        app_detail = app_detail[str(app_id)]['data']

                    if supabase.insertSteamGamesDB(app_id=app_id,data=app_detail) is False:
                        print(f"Error insertSteamGamesDB {app_id}")
                        continue

                # DB SteamAchievements
                print("++ DB SteamAchievements")
                achievements = steamapi.getAchievements(app_id=app_id)
                if achievements is False:
                    print(f"Error getAchievements {app_id}")
                    pass
                else:
                    achievements = achievements['game']['availableGameStats']['achievements']

                    if achievements is False:
                        print(f"Error No Achievements {app_id}")
                        continue

                    for achievement in achievements:
                        if supabase.existSteamAchievementsDB(app_id,achievement['name']) is False:
                            if supabase.insertSteamAchievementsDB(app_id,achievement) is False:
                                print(f"Error insertSteamAchievementsDB {app_id}")
                                continue

                # DB SteamUserGames
                print("++ DB SteamUserGames")
                if supabase.existSteamUserGamesDB(app_id) is False:

                    if supabase.insertSteamUserGamesDB(game) is False:
                        print(f"Error insertSteamUserGamesDB {app_id}")
                        continue

                    if supabase.updateSteamUserGamesDB(game) is False:
                        print(f"Error insertSteamUserGamesDB {app_id}")
                        continue

steamView()
