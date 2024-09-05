from typing_extensions import Text
from numpy import imag
import streamlit as st
import configparser
import pandas as pd
from pathlib import Path
from streamlit_card import card
from api.steam import SteamAPI
from supabaseDB import Supabase
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

config = configparser.ConfigParser()
config.read('config.ini')
steam_key = config['steam']['steamKey']
steam_id = "76561198050437739"
steamapi = SteamAPI(steam_key)

supabase = Supabase()
st.set_page_config(page_title="Steam", page_icon=":video_game:")

if 'clicked_id' not in st.session_state:
    st.session_state.clicked_id = None

@st.cache_data
def get_steam_user_library():
    df = pd.DataFrame()
    records = supabase.getSteamUserGames()
    if records is False:
        return False

    for record in records:
        dict = {
            'app_id': record['app_id'],
            'playtime_forever': record['playtime_forever'],
            'playtime_windows_forever': record['playtime_windows_forever'],
            'playtime_mac_forever': record['playtime_mac_forever'],
            'playtime_linux_forever': record['playtime_linux_forever'],
            'playtime_deck_forever': record['playtime_deck_forever'],
            'rtime_last_played': record['rtime_last_played'],
            'name': record['steamgames']['name'],
            'capsule_image': record['steamgames']['capsule_image'],
            'short_description': record['steamgames']['short_description'],
            'developers': record['steamgames']['developers'],
            'publishers': record['steamgames']['publishers'],
            'categories': record['steamgames']['categories'],
            'genres': record['steamgames']['genres'],
            'windows': record['steamgames']['windows'],
            'mac': record['steamgames']['mac'],
            'linux': record['steamgames']['linux'],
            'release_date': record['steamgames']['release_date'],
        }
        new_df = pd.DataFrame([dict])
        df = pd.concat([df,new_df], ignore_index=True)

    df = df.sort_values(by='name', ascending=False)
    return df

def set_clicked_id(id):
    st.session_state.clicked_id = id

def buildCard(data):
    return card(
        title=data['name'],
        text="",
        image=data['capsule_image'],
        key=str(data['app_id']),
        on_click=lambda: set_clicked_id(data['app_id'])
    )

def steamLibrarySearch(df:pd.DataFrame):
    global clicked_id
    titles = df['name'].unique().tolist()
    titles.insert(0, "All")

    if st.session_state.clicked_id != None:
        title = df.loc[df['app_id'] == st.session_state.clicked_id]['name'].values[0]
        index = titles.index(title)

    else:
        index = 0

    search_query = st.selectbox(label="Search for Title", options=titles,index=index)

    if search_query == "All":
        set_clicked_id(None)
        filtered_df = df.copy()

    elif search_query != "All":
        filtered_df = df.loc[df['name'] == search_query]
        app_id = filtered_df['app_id'].values[0]
        set_clicked_id(filtered_df['app_id'].values[0])
        return None

    # elif st.session_state.clicked_id != None:
    #     filtered_df = df.loc[df['name'] == search_query]

    else:
        filtered_df = df.copy()

    return filtered_df

def steamLibraryCards(df:pd.DataFrame,):
    col1, col2, col3, col4 = st.columns(4)
    for i, row in enumerate(df.iterrows()):
        data = row[1]
        if i % 4 == 0:
            with col1:
                card = buildCard(data)

        elif i % 4 == 1:
            with col2:
                card = buildCard(data)

        elif i % 4 == 2:
            with col3:
                card = buildCard(data)
        else:
            with col4:
                card = buildCard(data)

def steamLibraryView():
    df = get_steam_user_library()
    if df is False:
        st.write("Error getting Steam User Games")
        return False

    filterd_df = steamLibrarySearch(df)
    if filterd_df is not None:
        steamLibraryCards(filterd_df)

def steamLibraryDetailView():
    if st.session_state.clicked_id is None:
        return False

    app_id = st.session_state.clicked_id
    data = supabase.steamLibraryDetailView(app_id)
    if data is False:
        st.warning("Error getting Steam Library Detail View")
        return False

    st.title(data['name'])
    st.image(image=data['header_img'], use_column_width=True)

    # Get Achievements
    try:
        achievements = supabase.steamLibraryAchivementsView(app_id)
        if achievements is False:
            st.warning("Error getting Steam Library Achievements")
            return False

        achievements_df = pd.DataFrame()
        for i in achievements:
            unlocktime = int(i['steamuserachievements'][0]['unlocktime'])
            achieved = i['steamuserachievements'][0]['achieved']

            if unlocktime is not None and achieved:
                unlocktime = datetime.fromtimestamp(unlocktime)
                formatted_unlocktime = unlocktime.strftime('%b %d %Y %I:%M%p')
            else:
                unlocktime = None
                formatted_unlocktime = None

            dict = {
                'name': i['name'],
                'Achievement': i['display_name'],
                'hidden': i['hidden'],
                'icon': i['icon'],
                'icongrey': i['icongray'],
                'Achieved': achieved,
                'unlocktime': unlocktime,
                'Unlocked': formatted_unlocktime
            }
            new_df = pd.DataFrame([dict])
            achievements_df = pd.concat([achievements_df,new_df], ignore_index=True)

    except Exception as e:
        st.warning("Error getting Steam Library Achievements")
        achievements_df = None
        pass

    # Tabs
    if achievements_df is not None:
        tab1, tab2, tab3 = st.tabs(tabs=["Info","Table","Graph"])

        with tab1:
            steamLibraryDetailViewInfoTab(data)

        with tab2:
            steamLibraryDetailViewTableTab(achievements_df)

        with tab3:
            steamLibraryDetailViewGraphTab(achievements_df)

    # Update Achievements
    updateSteamUserAchievements(app_id)

def steamLibraryDetailViewInfoTab(data):
    st.write(data['short_description'])
    st.write(f"Developers: {data['developers']}")
    st.write(f"Publishers: {data['publishers']}")
    st.write(f"Genres: {data['genres']}")
    st.write(f"Release Date: {data['release_date']}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.write("Available Systems:")

    with col2:
        if data['windows'] == True:
            filepath = str(Path(r"data/images/windows.png"))
            st.image(image=filepath,width=50)

    with col3:
        if data['mac'] == True:
            filepath = str(Path(r"data/images/mac.png"))
            st.image(image=filepath,width=50)

    with col4:
        if data['linux'] == True:
            filepath = str(Path(r"data/images/linux.png"))
            st.image(image=filepath,width=50)

def steamLibraryDetailViewTableTab(df:pd.DataFrame):
    # Achievements
    try:
        # Progress Bar
        total_achievements = len(df)
        total_achieved = len(df.loc[df['Achieved'] == True])
        progress = total_achieved / total_achievements

        st.subheader(f"{total_achieved}/{total_achievements} Achievements Unlocked")
        st.progress(value=progress)
        df['Logo'] = df.apply(lambda x: x['icon'] if x['Achieved'] else x['icongrey'], axis=1)

        # Achievments Table
        st.data_editor(
            df,
            column_order=['Logo','Achievement','Achieved','Unlocked'],
            column_config={
                'Logo': st.column_config.ImageColumn(),
            },
            use_container_width=True
        )

    except Exception as e:
        st.warning(f"Error getting Steam Library Achievements {e}")
        pass

def steamLibraryDetailViewGraphTab(df:pd.DataFrame):
    # Graphs
    try:
        df['year'] = df['unlocktime'].dt.year
        df['month'] = df['unlocktime'].dt.month

        col1, col2 = st.columns(2)
        with col1:
            filter_year = st.button("Filter By Year", use_container_width=True)

        with col2:
            filter_month = st.button("Filter By Month", use_container_width=True)

    # By Year
        if filter_year:
            achievements_per_year = df.groupby('year')['Achieved'].sum().reset_index()
            fig = go.Figure()

            # Add bar trace
            fig.add_trace(go.Bar(
                x=achievements_per_year['year'],
                y=achievements_per_year['Achieved'],
                name='Achievements Unlocked',
                marker_color='indianred'
            ))

            # Add line trace
            fig.add_trace(go.Scatter(
                x=achievements_per_year['year'],
                y=achievements_per_year['Achieved'],
                name='Achievements Unlocked (Line)',
                mode='lines+markers',
                line=dict(color='royalblue')
            ))

            fig.update_layout(
                title='Achievements Unlocked Per Year',
                xaxis=dict(title='Year'),
                yaxis=dict(title='Achievements Unlocked'),
                barmode='group'
            )

            fig.update_xaxes(tickmode='array', tickvals=achievements_per_year['year'])
            st.plotly_chart(fig)

    # By Month
        if filter_month:
            achievements_per_month = df.groupby(['year', 'month'])['Achieved'].sum().reset_index()
            achievements_per_month_pivot = achievements_per_month.pivot(index='month', columns='year', values='Achieved').fillna(0)

            fig = go.Figure()

            for year in achievements_per_month_pivot.columns:
                fig.add_trace(go.Bar(
                    x=achievements_per_month_pivot.index,
                    y=achievements_per_month_pivot[year],
                    name=str(year)
                ))

            fig.update_layout(
                title='Achievements Unlocked Per Month Grouped by Year',
                xaxis=dict(title='Month', tickmode='array', tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
                yaxis=dict(title='Achievements Unlocked'),
                barmode='stack'
            )

            st.plotly_chart(fig)

    except Exception as e:
        st.warning(f"Error Graphing Steam Library Achievements {e}")
        pass

def updateSteamUserAchievements(app_id):
    if st.button("Update Achievements",use_container_width=True):
        with st.spinner(f'Updating Steam User Achievements...'):
            achievments = steamapi.getUserAchievements(app_id=app_id, steam_id=steam_id)
            if achievments is False:
                st.write("Error getting Steam User Achievements")
                return False

            for i, achievement in enumerate(achievments['playerstats']['achievements']):
                response = supabase.getSteamAchievements(app_id=app_id,name=achievement['apiname'])

                if response is False:
                    print(f"Error getting Steam Achievements {app_id} {achievement['apiname']}")
                    continue

                id = response[0]['id']
                if supabase.existSteamUserAchievementsDB(id=id):
                    if supabase.updateSteamUserAchievementsDB(id=id,data=achievement) is False:
                        print(f"Error updating Steam Achievements {app_id} {achievement['apiname']}")
                        continue

                else:
                    if supabase.insertSteamUserAchievementsDB(id=id,data=achievement)  is False:
                        print(f"Error inserting Steam Achievements {app_id} {achievement['apiname']}")
                        continue

def updateSteamLibrary():
    if st.button("Update Steam Library"):
        games = steamapi.getOwnedGames(steam_id=steam_id)
        if games is False:
            st.write("Error getting Steam Library")
            return False

        with st.spinner(f'Updating Steam Library...'):

            for i, game in enumerate(games['response']['games']):
                app_id = game['appid']
                print(f"{i:<4}/{len(games['response']['games']):<4} app_id ", app_id)

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

def steamView():
    steamLibraryView()
    steamLibraryDetailView()
    # updateSteamLibrary()


steamView()
