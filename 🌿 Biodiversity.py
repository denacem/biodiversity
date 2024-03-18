import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from crop_selector import select_crop

from functions import format_swiss_number
from functions import format_swiss_number_sci

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

# Fill NaN values with 0
impex_swiss_data = impex_swiss_data.fillna(0)

# Convert to numbers
impex_swiss_data['Import Quantity (kg)'] = pd.to_numeric(impex_swiss_data['Import Quantity (kg)'], errors='coerce')
impex_swiss_data['Export Quantity (kg)'] = pd.to_numeric(impex_swiss_data['Export Quantity (kg)'], errors='coerce')

# Calculate the net quantity
impex_swiss_data['Net (kg)'] = impex_swiss_data['Import Quantity (kg)'] - impex_swiss_data['Export Quantity (kg)']

# Calculate the total sum considering only positive net values
positive_net_sum = impex_swiss_data['Net (kg)'][impex_swiss_data['Net (kg)'] > 0].sum()

# Calculate the share in percentage, clip to ensure it's not negative
impex_swiss_data['Share (%)'] = (impex_swiss_data['Net (kg)'] / positive_net_sum * 100).clip(lower=0)

# Calculate the total share excluding NaN values
total_share = impex_swiss_data['Share (%)'].sum(skipna=True)

# Reset index to make 'Trade Partner' a regular column
impex_swiss_data = impex_swiss_data.reset_index()

# Make sure the 'Area' values are unique before setting the index
impex_swiss_data_unique_areas = impex_swiss_data.set_index('Trade Partner').drop_duplicates()

# Filter impex_swiss_data to only include rows with valid 'Area' values
impex_swiss_data = impex_swiss_data[impex_swiss_data['Trade Partner'].isin(impex_swiss_data_unique_areas.index)]

# Keep 'Area Code (M49)' in the result table
#impex_swiss_data['Area Code (M49)'] = impex_swiss_data_unique_areas.loc[impex_swiss_data['Trade Partner'], 'Area Code (M49)'].values

# Remove leading whitespaces
impex_swiss_data['Trade Partner'] = impex_swiss_data['Trade Partner'].str.lstrip()

# Drop redundant columns
impex_swiss_data = impex_swiss_data.drop(['index'], axis=1)

# Perform a lookup to get 'Yield' from yield_data
impex_swiss_data = pd.merge(impex_swiss_data, yield_data[['Area', 'Value']], left_on='Trade Partner', right_on='Area', how='left')

# Fill NaN values in 'Yield' with 0
impex_swiss_data['Yield (m^2/kg)'] = impex_swiss_data['Value'].fillna(0)

# Convert 'Yield' from 100g/ha to kg/m² and then invert to get m²/kg
#then it's land use!
impex_swiss_data['Yield (m^2/kg)'] = 1 / (impex_swiss_data['Yield (m^2/kg)'] / 100000)  # 1 / (100g/ha) = kg/m²

# Replace infinite values with NaN
impex_swiss_data = impex_swiss_data.replace([np.inf, -np.inf], np.nan)

# Replace NaN values with 0
impex_swiss_data = impex_swiss_data.fillna(0)

# Calculate the 'Weighted (m^2/kg)' column
impex_swiss_data['Weighted (m^2/kg)'] = (impex_swiss_data['Yield (m^2/kg)'] * impex_swiss_data['Share (%)']) / total_share

# Merge with countries lookup table to get short codes
impex_swiss_data = pd.merge(impex_swiss_data, countries_data[['Name', 'short']], left_on='Trade Partner', right_on='Name', how='left')

# Merge the columns so get pdf factors
impex_swiss_data_merged = pd.merge(impex_swiss_data, pdf_data, left_on='short', right_on='country_code', how='left')

impex_swiss_data_merged['occupation'].fillna('', inplace=True)  # Replace NaN with empty string

# Filter to just use the current crop
impex_swiss_data_merged = impex_swiss_data_merged[impex_swiss_data_merged['occupation'].str.contains(crop_type)]
impex_swiss_data_merged.reset_index(drop=True, inplace=True)

# Get the PDF factor
impex_swiss_data['PDF Factor'] = impex_swiss_data_merged['amount']

impex_swiss_data['PDF (PDF/kg)'] = impex_swiss_data['PDF Factor'] * impex_swiss_data['Weighted (m^2/kg)']

# Reorder the columns
impex_swiss_data = impex_swiss_data[['Trade Partner', 'Import Quantity (kg)', 'Export Quantity (kg)', 'Net (kg)', 'Yield (m^2/kg)', 'Share (%)', 'Weighted (m^2/kg)', 'PDF Factor', 'PDF (PDF/kg)']]

#Get top PDF countries
impex_swiss_data_viz = impex_swiss_data.nlargest(25, 'PDF (PDF/kg)')

# Calculate total PDF
total_swiss_pdf = impex_swiss_data['PDF (PDF/kg)'].sum(skipna=True)

# Apply the custom formatting function
impex_swiss_data['Import Quantity (kg)'] = impex_swiss_data['Import Quantity (kg)'].apply(format_swiss_number)
impex_swiss_data['Export Quantity (kg)'] = impex_swiss_data['Export Quantity (kg)'].apply(format_swiss_number)
impex_swiss_data['Net (kg)'] = impex_swiss_data['Net (kg)'].apply(format_swiss_number)
impex_swiss_data['Yield (m^2/kg)'] = impex_swiss_data['Yield (m^2/kg)'].apply(format_swiss_number_sci)
impex_swiss_data['Share (%)'] = impex_swiss_data['Share (%)'].apply(format_swiss_number)
impex_swiss_data['Weighted (m^2/kg)'] = impex_swiss_data['Weighted (m^2/kg)'].apply(format_swiss_number_sci)
impex_swiss_data['PDF (PDF/kg)'] = impex_swiss_data['PDF (PDF/kg)'].apply(format_swiss_number_sci)
impex_swiss_data['PDF Factor'] = impex_swiss_data['PDF Factor'].apply(format_swiss_number_sci)

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

# Filter only import and export data
import_world_data = impex_world_data[impex_world_data['Element'] == 'Import Quantity'].set_index('Area')['Value']
export_world_data = impex_world_data[impex_world_data['Element'] == 'Export Quantity'].set_index('Area')['Value']

# Create a DataFrame with import, export, and net columns
result_world_data = pd.DataFrame({
    'Import (t)': import_world_data,
    'Export (t)': export_world_data
})

# Fill NaN values with 0
result_world_data = result_world_data.fillna(0)

# Calculate the net quantity
result_world_data['Net Export (t)'] = result_world_data['Export (t)'] - result_world_data['Import (t)']

# Calculate the total sum considering only positive net values
positive_net_sum = result_world_data['Net Export (t)'][result_world_data['Net Export (t)'] > 0].sum()

# Calculate the share in percentage, clip to ensure it's not negative
result_world_data['Share (%)'] = (result_world_data['Net Export (t)'] / positive_net_sum * 100).clip(lower=0)

# Calculate the total share excluding NaN values
total_share = result_world_data['Share (%)'].sum(skipna=True)

# Reset index to make 'Area' a regular column
result_world_data = result_world_data.reset_index()

# Make sure the 'Area' values are unique before setting the index
impex_world_data_unique_areas = impex_world_data[impex_world_data['Element'] == 'Import Quantity'].set_index('Area').drop_duplicates()

# Filter result_world_data to only include rows with valid 'Area' values
result_world_data = result_world_data[result_world_data['Area'].isin(impex_world_data_unique_areas.index)]

# Merge with countries lookup table to get short codes
result_world_data = pd.merge(result_world_data, countries_data[['Name', 'short']], left_on='Area', right_on='Name', how='left')

# Drop redundant columns
result_world_data = result_world_data.drop(['Name'], axis=1)

# Keep 'Area Code (M49)' in the result table
result_world_data['Area Code (M49)'] = impex_world_data_unique_areas.loc[result_world_data['Area'], 'Area Code (M49)'].values

# Perform a lookup to get 'Yield' from yield_data
result_world_data = pd.merge(result_world_data, yield_data[['Area Code (M49)', 'Value']], left_on='Area Code (M49)', right_on='Area Code (M49)', how='left')

# Fill NaN values in 'Yield' with 0
result_world_data['Yield (m^2/kg)'] = result_world_data['Value'].fillna(0)

# Convert 'Yield' from 100g/ha to kg/m² and then invert to get m²/kg
result_world_data['Yield (m^2/kg)'] = 1 / (result_world_data['Yield (m^2/kg)'] / 100000)  # 1 / (100g/ha) = kg/m²

# Replace infinite values with NaN
result_world_data = result_world_data.replace([np.inf, -np.inf], np.nan)

# Replace NaN values with 0
result_world_data = result_world_data.fillna(0)

# Calculate the 'Weighted (m^2/kg)' column
result_world_data['Weighted (m^2/kg)'] = (result_world_data['Yield (m^2/kg)'] * result_world_data['Share (%)']) / total_share

# Now, you can use these two columns for merging
result_world_data_merged = pd.merge(result_world_data, pdf_data, left_on='short', right_on='country_code', how='left')

# Fill NaN values in 'amount' with 0
result_world_data['PDF Factor'] = result_world_data_merged['amount'].fillna(0)

#st.write(type(result_world_data['PDF Factor'][0]))

result_world_data['PDF (PDF/kg)'] = result_world_data['PDF Factor'] * result_world_data['Weighted (m^2/kg)']

# Rename columns
result_world_data = result_world_data.rename(columns={'Area': 'Trade Partner', 'short': 'Code', 'Value_x': 'Import (t)', 'Value_y': 'Yield (m^2/kg)'})

# Reorder the columns
result_world_data = result_world_data[['Trade Partner', 'Code', 'Import (t)', 'Export (t)', 'Net Export (t)', 'Yield (m^2/kg)', 'Share (%)', 'Weighted (m^2/kg)', 'PDF (PDF/kg)']]

# Get top PDF countries
result_world_data_viz = result_world_data.nlargest(25   , 'PDF (PDF/kg)')

# Calculate total PDF
total_world_pdf = result_world_data['PDF (PDF/kg)'].sum(skipna=True)

# Apply the custom formatting function
result_world_data['Import (t)'] = result_world_data['Import (t)'].apply(format_swiss_number)
result_world_data['Export (t)'] = result_world_data['Export (t)'].apply(format_swiss_number)
result_world_data['Net Export (t)'] = result_world_data['Net Export (t)'].apply(format_swiss_number)
result_world_data['Yield (m^2/kg)'] = result_world_data['Yield (m^2/kg)'].apply(format_swiss_number_sci)
result_world_data['Share (%)'] = result_world_data['Share (%)'].apply(format_swiss_number)
result_world_data['Weighted (m^2/kg)'] = result_world_data['Weighted (m^2/kg)'].apply(format_swiss_number_sci)
result_world_data['PDF (PDF/kg)'] = result_world_data['PDF (PDF/kg)'].apply(format_swiss_number_sci)

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