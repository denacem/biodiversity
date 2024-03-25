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

st.title('🌿 Biodiversity')

# Select crop
selected_crop = crop_selector(crops_data)
selected_crop_emoji, crop_type, impex_world_data, impex_swiss_data, yield_data = select_crop(selected_crop)

# Display the selected crop
st.write(f"Selected: {selected_crop_emoji + ' ' + selected_crop.title()}")
st.write(f"Type of Crop: {crop_type.title()}")


# Load the lookup tables
countries_data = pd.read_csv('./data/countries.csv')
pdf_data = pd.read_csv('./data/pdf.csv')
crops_data = pd.read_csv('./data/crops.csv')

# Prepare PDF Data
pdf_data = prepare_pdf_data(pdf_data)

### PDF Calculation for Switzerland
result_swiss_data, total_swiss_pdf, result_swiss_data_top = calc_biodiversity_swiss(impex_swiss_data, countries_data, pdf_data, crop_type, yield_data)

# Show the result
st.subheader(f'Biodiversity Calculation (Swiss Trade) for {selected_crop.title()}')
st.dataframe(result_swiss_data)

# Display the total sum
st.write(f'Total PDF: {format_swiss_number_sci(total_swiss_pdf)}')


# Create the bar plot for result_swiss_data
plt.figure(figsize=(10, 6))
plt.bar(result_swiss_data_top['Trade Partner'], result_swiss_data_top['PDF (PDF/kg)'].astype(float))
plt.xlabel('Country')
plt.ylabel('PDF (PDF/kg)')
plt.title(f'PDF Value by Country for {selected_crop.title()}')
plt.xticks(rotation=90)
st.pyplot(plt)

### PDF Calculation for World

result_world_data, total_world_pdf, result_world_data_top = calc_biodiversity_world(impex_world_data, countries_data, pdf_data, crop_type, yield_data)

# Show the result
st.subheader(f'Biodiversity Calculation (World Trade) for {selected_crop.title()}')
st.dataframe(result_world_data)

# Display the total sum
# st.write(f'Total PDF: {format_swiss_number(positive_net_sum)}')
# st.write(f'Total Share: {format_swiss_number(total_share)}')
st.write(f'Total PDF: {format_swiss_number_sci(total_world_pdf)}')

# Create the bar plot for impex_world_data
plt.figure(figsize=(10, 6))
plt.bar(result_world_data_top['Trade Partner'], result_world_data_top['PDF (PDF/kg)'].astype(float))
plt.xlabel('Country')
plt.ylabel('PDF (PDF/kg)')
plt.title(f'PDF Value by Country for {selected_crop.title()}')
plt.xticks(rotation=90)
st.pyplot(plt)

### Comparison

st.subheader(f'Biodiversity Comparison Swiss/World for {selected_crop.title()}')

# Create a figure and two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))

# Plot Swiss
ax1.barh(result_swiss_data_top['Trade Partner'], result_swiss_data_top['PDF (PDF/kg)'], color='red', label='Swiss')
ax1.set_xlabel('PDF (PDF/kg)')
ax1.set_ylabel('Trade Partner')
ax1.set_title('Swiss PDF')


# Plot World
ax2.barh(result_world_data_top['Trade Partner'], result_world_data_top['PDF (PDF/kg)'], color='blue', label='World')
ax2.set_xlabel('PDF (PDF/kg)')
ax2.set_ylabel('Trade Partner')
ax2.set_title('World PDF')
ax2.yaxis.set_label_position("right")
ax2.yaxis.tick_right()

# Set the same x-axis limits for both subplots
max_pdf = max(max(result_swiss_data_top['PDF (PDF/kg)']), max(result_world_data_top['PDF (PDF/kg)']))
ax1.set_xlim(0, max_pdf)
ax2.set_xlim(0, max_pdf)
ax1.invert_xaxis()  # Invert x-axis to make pyramid shape

# Adjust y-axis labels for the right plot
ax2.tick_params(axis='y', direction='inout')

# Adjust layout
plt.tight_layout()

# Show plot
st.pyplot(plt)