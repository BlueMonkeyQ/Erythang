import streamlit as st
from api import steam

st.set_page_config(page_title="Steam", page_icon=":video_game:")

steam_id = "76561198050437739"

def steamView():

    if st.button("Update Steam Library"):
        with st.spinner("Getting Library"):
            steam.getSteamUserGames(steam_id=steam_id)