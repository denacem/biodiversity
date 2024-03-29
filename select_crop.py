import streamlit as st
import pandas as pd
import os

# Read the crops.csv file to get available crop options
crops_file_path = "./data/crops.csv"
crops_data = pd.read_csv(crops_file_path, dtype={"code": str})

def crop_selector(crops_data):
    # Create a dropdown menu for selecting the crop
    selected_crop_title = st.selectbox("Select a Crop:", crops_data["title"])
    selected_crop_code = crops_data.loc[crops_data["title"] == selected_crop_title, "code"].iloc[0]

    return selected_crop_title, selected_crop_code

def select_crop(selected_crop_code):
    # Create a dropdown menu for selecting the crop
    selected_crop_emoji = crops_data.loc[crops_data["code"] == selected_crop_code, "emoji"].iloc[0]

    # Display the crop type
    crop_type = crops_data.loc[crops_data["code"] == selected_crop_code, "occupation"].iloc[0]

    # Generate paths for impex and yield files based on the selected crop
    impex_world_file_path = os.path.join("./data/impex", f"{selected_crop_code}_world.csv")
    impex_swiss_file_path = os.path.join("./data/impex", f"{selected_crop_code}_swiss.txt")
    yield_file_path = os.path.join("./data/yield", f"{selected_crop_code}.csv")

    # Read the data from the selected impex and yield files
    impex_world_data = pd.read_csv(impex_world_file_path)
    impex_swiss_data = read_swiss_impex(impex_swiss_file_path)
    yield_data = pd.read_csv(yield_file_path)

    return selected_crop_emoji, crop_type, impex_world_data, impex_swiss_data, yield_data

def read_swiss_impex(file_path):
    # Read the Swiss impex file, skip lines until a line starts with "Period"
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("Period"):
                break

        # Now read the remaining lines into a DataFrame
        impex_data = pd.read_csv(file, delimiter='\t', usecols=[1, 2, 3, 4, 5, 6, 7])

    # Rename columns
    impex_data.columns = [
        "Trade Partner", "Import Quantity (kg)", "Import Value (CHF)", "Import Value +/- %",
        "Export Quantity (kg)", "Export Value (CHF)", "Export Value +/- %"
    ]


    # Remove commas and convert to numeric, handling '*' with errors='coerce'
    impex_data.iloc[:, 1:] = impex_data.iloc[:, 1:].replace({',': ''}, regex=True).apply(pd.to_numeric, errors='coerce')

    # Handle NaN values as needed (replace with 0, drop rows, etc.)
    impex_data = impex_data.fillna(0)

    return impex_data
