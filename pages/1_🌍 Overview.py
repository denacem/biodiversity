import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from select_crop import select_crop, crop_selector, crops_data

from format_functions import format_swiss_number_sci
from data_functions import prepare_pdf_data
from calc_biodiversity_swiss import calc_biodiversity_swiss
from calc_biodiversity_world import calc_biodiversity_world

st.set_page_config(layout='wide')

st.title('🌍 Overview')

# Load the lookup tables
countries_data = pd.read_csv('./data/countries.csv')
pdf_data = pd.read_csv('./data/pdf.csv')
crops_data = pd.read_csv('./data/crops.csv', dtype={"code": str})

# Prepare PDF Data
pdf_data = prepare_pdf_data(pdf_data)

# Initialize an empty list to store the data for each iteration
all_results = []

# Loop over crops
for index, row in crops_data.iterrows():
    crop_data = {}
    selected_crop_emoji, crop_type, impex_world_data, impex_swiss_data, yield_data = select_crop(row['code'])
    result_swiss_data, total_swiss_pdf, result_swiss_data_top = calc_biodiversity_swiss(impex_swiss_data, countries_data, pdf_data, crop_type, yield_data)
    result_world_data, total_world_pdf, result_world_data_top = calc_biodiversity_world(impex_world_data, countries_data, pdf_data, crop_type, yield_data)
    
    # Store the data for the current crop in a dictionary
    crop_data['code'] = row['code']
    crop_data['title'] = row['title']
    crop_data['selected_crop_emoji'] = selected_crop_emoji
    crop_data['crop_type'] = crop_type
    crop_data['result_swiss_data'] = result_swiss_data
    crop_data['total_swiss_pdf'] = total_swiss_pdf
    crop_data['result_swiss_data_top'] = result_swiss_data_top
    crop_data['result_world_data'] = result_world_data
    crop_data['total_world_pdf'] = total_world_pdf
    crop_data['result_world_data_top'] = result_world_data_top

    crop_data['yield_data'] = yield_data
    
    # Append the dictionary to the list
    all_results.append(crop_data)

#st.write(all_results)

# Extract total Swiss and total world PDFs for each crop
crop_names = [crop['title'] for crop in all_results]
total_swiss_pdfs = [crop['total_swiss_pdf'] for crop in all_results]
total_world_pdfs = [crop['total_world_pdf'] for crop in all_results]

# Create a bar plot to compare total Swiss and total world PDFs
plt.figure(figsize=(10, 6))
plt.bar(crop_names, total_swiss_pdfs, color='red', alpha=0.7, label='Total Swiss PDF')
plt.bar(crop_names, total_world_pdfs, color='blue', alpha=0.7, label='Total World PDF')
plt.xlabel('Crop')
plt.ylabel('Total PDF')
plt.title('Comparison of Total Swiss and Total World Potentially Disappeared Fraction for Different Crops')
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()

# Show the plot
st.pyplot(plt)

# Create a list of dataframes for Swiss top data
swiss_top_dataframes = [crop_data['result_swiss_data_top']['PDF Factor'] for crop_data in all_results]

# Create a list of dataframes for world top data
world_top_dataframes = [crop_data['result_world_data_top']['PDF Factor'] for crop_data in all_results]

# Concatenate the lists of dataframes
combined_top_data = pd.concat(swiss_top_dataframes + world_top_dataframes, axis=1, keys=[crop_data['title'] for crop_data in all_results])

st.write(combined_top_data)

# Get country names
country_names = [countries_data[countries_data['short'] == code]['Name'].values[0] for code in combined_top_data.index]

# Plot the combined data
plt.figure(figsize=(12, 8))

# Plot top Swiss PDFs
for index, (crop_name, pdf_factors) in enumerate(combined_top_data.iteritems(), start=1):
    plt.barh(np.arange(len(pdf_factors)) + index * 0.4, pdf_factors, height=0.4, label=crop_name)

plt.yticks(np.arange(len(combined_top_data.index)), country_names)
plt.xlabel('PDF Factor')
plt.ylabel('Country')
plt.title('Top Countries for Each Crop')
plt.legend()

plt.gca().invert_yaxis()
plt.tight_layout()

# Show the plot
st.pyplot(plt)