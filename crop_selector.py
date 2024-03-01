import streamlit as st
import pandas as pd
import os

def select_crop():

    # Read the crops.csv file to get available crop options
    crops_file_path = "./data/crops.csv"
    crops_data = pd.read_csv(crops_file_path)

    # Create a dropdown menu for selecting the crop
    selected_crop = st.selectbox("Select a Crop:", crops_data["crop"])
    selected_crop_emoji = crops_data.loc[crops_data["crop"] == selected_crop, "emoji"].iloc[0]

    # Display the selected crop
    st.write(f"Selected: {selected_crop_emoji + ' ' + selected_crop.title()}")

    # Display the crop type
    crop_type = crops_data.loc[crops_data["crop"] == selected_crop, "occupation"].iloc[0]
    st.write(f"Type of Crop: {crop_type.title()}")

    # Generate paths for impex and yield files based on the selected crop
    impex_world_file_path = os.path.join("./data/impex", f"{selected_crop.lower()}_world_2022.csv")
    impex_swiss_file_path = os.path.join("./data/impex", f"{selected_crop.lower()}_swiss_2022.txt")
    yield_file_path = os.path.join("./data/yield", f"{selected_crop.lower()}_2022.csv")

    # Read the data from the selected impex and yield files
    impex_world_data = pd.read_csv(impex_world_file_path)
    impex_swiss_data = read_swiss_impex(impex_swiss_file_path)
    yield_data = pd.read_csv(yield_file_path)

    return selected_crop, crop_type, impex_world_data, impex_swiss_data, yield_data

def read_swiss_impex(file_path):
    # Read the Swiss impex file, skip lines until a line starts with "Period"
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("Period"):
                break

        # Now read the remaining lines into a DataFrame, skip the first line (column names)
        impex_data = pd.read_csv(file, delimiter='\t', usecols=[1, 2, 3, 4, 5, 6, 7])

    # Rename columns
    impex_data.columns = [
        "Commercial partner", "Import Quantity (kg)", "Import Value (CHF)", "Import Value +/- %",
        "Export Quantity (kg)", "Export Value (CHF)", "Export Value +/- %"
    ]

    return impex_data
