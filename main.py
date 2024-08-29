import streamlit as st
from views.bank import bankView
from views.steam import steamView


st.set_page_config()
st.title("Yo")

bankView()
# steamView()