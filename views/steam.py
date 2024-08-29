import streamlit as st
from api import steam

steam_id = "76561198050437739"

def steamView():

    if st.button("Update Steam Library"):
        with st.spinner("Getting Library"):
            steam.getSteamUserGames(steam_id=steam_id)