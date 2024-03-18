import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from select_crop import select_crop

from format_functions import format_swiss_number_sci
from calc_biodiversity_swiss import calc_biodiversity_swiss
from calc_biodiversity_world import calc_biodiversity_world

st.set_page_config(layout='wide')

st.title('🌿 Biodiversity')

selected_crop, crop_type, impex_world_data, impex_swiss_data, yield_data = select_crop()

# Load the lookup tables
countries_data = pd.read_csv('./data/countries.csv')
pdf_data = pd.read_csv('./data/pdf.csv')
crops_data = pd.read_csv('./data/crops.csv')

# Extract the 'occupation' based on the 'crop' from selected_crop
occupation = crops_data.loc[crops_data['crop'] == selected_crop, 'occupation'].iloc[0]

# Prepare PDF Data
split_columns = pdf_data['occupation/transformation'].str.split(',', n=3, expand=True)
pdf_data['occupation'] = split_columns[1].str.strip()
pdf_data['country_code'] = split_columns[2].str.strip()

### PDF Calculation for Switzerland

impex_swiss_data, total_swiss_pdf, impex_swiss_data_viz = calc_biodiversity_swiss(impex_swiss_data, countries_data, pdf_data, crop_type, yield_data)

# Show the result
st.subheader(f'Biodiversity Calculation (Swiss Trade) for {selected_crop.title()}')
st.dataframe(impex_swiss_data)

# Display the total sum
# st.write(f'Total Sum: {format_swiss_number(positive_net_sum)}')
# st.write(f'Total Share: {format_swiss_number(total_share)}')
st.write(f'Total PDF: {format_swiss_number_sci(total_swiss_pdf)}')


# Create the bar plot for impex_world_data
plt.figure(figsize=(10, 6))
plt.bar(impex_swiss_data_viz['Trade Partner'], impex_swiss_data_viz['PDF (PDF/kg)'].astype(float))
plt.xlabel('Country')
plt.ylabel('PDF (PDF/kg)')
plt.title(f'PDF Value by Country for {selected_crop.title()}')
plt.xticks(rotation=90)
st.pyplot(plt)

### PDF Calculation for World

result_world_data, total_world_pdf, result_world_data_viz = calc_biodiversity_world(impex_world_data, countries_data, pdf_data, crop_type, yield_data)

# Show the result
st.subheader(f'Biodiversity Calculation (World Trade) for {selected_crop.title()}')
st.dataframe(result_world_data)

# Display the total sum
# st.write(f'Total PDF: {format_swiss_number(positive_net_sum)}')
# st.write(f'Total Share: {format_swiss_number(total_share)}')
st.write(f'Total PDF: {format_swiss_number_sci(total_world_pdf)}')

# Create the bar plot for impex_world_data
plt.figure(figsize=(10, 6))
plt.bar(result_world_data_viz['Trade Partner'], result_world_data_viz['PDF (PDF/kg)'].astype(float))
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
ax1.barh(impex_swiss_data_viz['Trade Partner'], impex_swiss_data_viz['PDF (PDF/kg)'], color='red', label='Swiss')
ax1.set_xlabel('PDF (PDF/kg)')
ax1.set_ylabel('Trade Partner')
ax1.set_title('Swiss PDF')


# Plot World
ax2.barh(result_world_data_viz['Trade Partner'], result_world_data_viz['PDF (PDF/kg)'], color='blue', label='World')
ax2.set_xlabel('PDF (PDF/kg)')
ax2.set_ylabel('Trade Partner')
ax2.set_title('World PDF')
ax2.yaxis.set_label_position("right")
ax2.yaxis.tick_right()

# Set the same x-axis limits for both subplots
max_pdf = max(max(impex_swiss_data_viz['PDF (PDF/kg)']), max(result_world_data_viz['PDF (PDF/kg)']))
ax1.set_xlim(0, max_pdf)
ax2.set_xlim(0, max_pdf)
ax1.invert_xaxis()  # Invert x-axis to make pyramid shape

# Adjust y-axis labels for the right plot
ax2.tick_params(axis='y', direction='inout')

# Adjust layout
plt.tight_layout()

# Show plot
st.pyplot(plt)