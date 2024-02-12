import streamlit as st

from crop_selector import select_crop

st.set_page_config(layout="wide")

st.title("🌿 Biodiversity!")

selected_crop, crop_type, impex_data, yield_data = select_crop()

