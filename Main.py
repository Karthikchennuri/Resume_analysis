# main.py
import streamlit as st
from streamlit_option_menu import option_menu
from pages import about_project, test

pages = {
    
    "About Project": about_project,
    "Resume Analysis": test
}

st.sidebar.title("Navigation")
selection = option_menu(
    menu_title=None,
    options=list(pages.keys()),
    icons=["file-earmark-text", "info-circle"],
    default_index=0,
    orientation="horizontal",
)

pages[selection].app()