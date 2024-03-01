import streamlit as st
import pandas as pd
import locale
import numpy as np

from crop_selector import select_crop

# Set the default locale for all numbers
# locale.setlocale(locale.LC_NUMERIC, 'de_CH')

st.set_page_config(layout="wide")

st.title("🌿 Biodiversity")

selected_crop, crop_type, impex_world_data, impex_swiss_data, yield_data = select_crop()

# Load the countries lookup table
countries_data = pd.read_csv("./data/countries.csv")

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
result_world_data['Net (t)'] = result_world_data['Import (t)'] - result_world_data['Export (t)']

# Calculate the total sum considering only positive net values
positive_net_sum = result_world_data['Net (t)'][result_world_data['Net (t)'] > 0].sum()

# Calculate the share in percentage, clip to ensure it's not negative
result_world_data['Share (%)'] = (result_world_data['Net (t)'] / positive_net_sum * 100).clip(lower=0)

# Calculate the total share excluding NaN values
total_share = result_world_data['Share (%)'].sum(skipna=True)

# Reset index to make 'Area' a regular column
result_world_data = result_world_data.reset_index()

# Make sure the "Area" values are unique before setting the index
impex_world_data_unique_areas = impex_world_data[impex_world_data['Element'] == 'Import Quantity'].set_index('Area').drop_duplicates()

# Filter result_world_data to only include rows with valid "Area" values
result_world_data = result_world_data[result_world_data['Area'].isin(impex_world_data_unique_areas.index)]

# Merge with countries lookup table to get short codes
result_world_data = pd.merge(result_world_data, countries_data[['Name', 'short']], left_on='Area', right_on='Name', how='left')

# Drop redundant columns
result_world_data = result_world_data.drop(['Name'], axis=1)

# Keep 'Area Code (M49)' in the result table
result_world_data['Area Code (M49)'] = impex_world_data_unique_areas.loc[result_world_data['Area'], 'Area Code (M49)'].values

# Perform a lookup to get "Yield" from yield_data
result_world_data = pd.merge(result_world_data, yield_data[['Area Code (M49)', 'Value']], left_on='Area Code (M49)', right_on='Area Code (M49)', how='left')

# Fill NaN values in "Yield" with 0
result_world_data['Yield (m^2/kg)'] = result_world_data['Value'].fillna(0)

# Convert "Yield" from 100g/ha to kg/m² and then invert to get m²/kg
result_world_data['Yield (m^2/kg)'] = 1 / (result_world_data['Yield (m^2/kg)'] / 100)  # 1 / (100g/ha) = kg/m²

# Replace infinite values with NaN
result_world_data = result_world_data.replace([np.inf, -np.inf], np.nan)

# Replace NaN values with 0
result_world_data = result_world_data.fillna(0)

# Calculate the 'Weighted (m^2/kg)' column
result_world_data['Weighted (m^2/kg)'] = (result_world_data['Yield (m^2/kg)'] * result_world_data['Share (%)']) / total_share

# Rename columns
result_world_data = result_world_data.rename(columns={'Area': 'Trade Partner', 'short': 'Code', 'Value_x': 'Import (t)', 'Value_y': 'Yield (m^2/kg)'})

# Reorder the columns
result_world_data = result_world_data[['Trade Partner', 'Area Code (M49)', 'Code', 'Import (t)', 'Export (t)', 'Net (t)', 'Yield (m^2/kg)', 'Share (%)', 'Weighted (m^2/kg)']]

# Custom function for Swiss number formatting
def format_swiss_number(number):
    formatted_number = locale.format("%0.4f", number, grouping=True)
    return formatted_number.replace(locale.localeconv()['decimal_point'], '.')

# Apply the custom formatting function
result_world_data['Import (t)'] = result_world_data['Import (t)'].apply(format_swiss_number)
result_world_data['Export (t)'] = result_world_data['Export (t)'].apply(format_swiss_number)
result_world_data['Net (t)'] = result_world_data['Net (t)'].apply(format_swiss_number)
result_world_data['Yield (m^2/kg)'] = result_world_data['Yield (m^2/kg)'].apply(format_swiss_number)
result_world_data['Share (%)'] = result_world_data['Share (%)'].apply(format_swiss_number)
result_world_data['Weighted (m^2/kg)'] = result_world_data['Weighted (m^2/kg)'].apply(format_swiss_number)

# Show the result
st.subheader(f"Biodiversity Calculation (World Trade) for {selected_crop.title()}")
st.dataframe(result_world_data)

# Display the total sum
st.write(f"Total Sum: {format_swiss_number(positive_net_sum)}")
st.write(f"Total Share: {format_swiss_number(total_share)}")



### Same stuff for Swiss

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

# Make sure the "Area" values are unique before setting the index
impex_swiss_data_unique_areas = impex_swiss_data.set_index('Trade Partner').drop_duplicates()

# Filter impex_swiss_data to only include rows with valid "Area" values
impex_swiss_data = impex_swiss_data[impex_swiss_data['Trade Partner'].isin(impex_swiss_data_unique_areas.index)]

# Keep 'Area Code (M49)' in the result table
#impex_swiss_data['Area Code (M49)'] = impex_swiss_data_unique_areas.loc[impex_swiss_data['Trade Partner'], 'Area Code (M49)'].values

# Remove leading whitespaces
impex_swiss_data['Trade Partner'] = impex_swiss_data['Trade Partner'].str.lstrip()

# Drop redundant columns
impex_swiss_data = impex_swiss_data.drop(['index'], axis=1)

# Perform a lookup to get "Yield" from yield_data
impex_swiss_data = pd.merge(impex_swiss_data, yield_data[['Area', 'Value']], left_on='Trade Partner', right_on='Area', how='left')

# Fill NaN values in "Yield" with 0
impex_swiss_data['Yield (m^2/kg)'] = impex_swiss_data['Value'].fillna(0)

# Convert "Yield" from 100g/ha to kg/m² and then invert to get m²/kg
impex_swiss_data['Yield (m^2/kg)'] = 1 / (impex_swiss_data['Yield (m^2/kg)'] / 100)  # 1 / (100g/ha) = kg/m²

# Replace infinite values with NaN
impex_swiss_data = impex_swiss_data.replace([np.inf, -np.inf], np.nan)

# Replace NaN values with 0
impex_swiss_data = impex_swiss_data.fillna(0)

# Calculate the 'Weighted (m^2/kg)' column
impex_swiss_data['Weighted (m^2/kg)'] = (impex_swiss_data['Yield (m^2/kg)'] * impex_swiss_data['Share (%)']) / total_share

# Rename columns
#impex_swiss_data = impex_swiss_data.rename(columns={'Value_x': 'Import (t)', 'Value_y': 'Yield (m^2/kg)'})

#st.write(impex_swiss_data)

# Reorder the columns
impex_swiss_data = impex_swiss_data[['Trade Partner', 'Import Quantity (kg)', 'Export Quantity (kg)', 'Net (kg)', 'Yield (m^2/kg)', 'Share (%)', 'Weighted (m^2/kg)']]

# Custom function for Swiss number formatting
def format_swiss_number(number):
    formatted_number = locale.format("%0.4f", number, grouping=True)
    return formatted_number.replace(locale.localeconv()['decimal_point'], '.')

# Apply the custom formatting function
impex_swiss_data['Import Quantity (kg)'] = impex_swiss_data['Import Quantity (kg)'].apply(format_swiss_number)
impex_swiss_data['Export Quantity (kg)'] = impex_swiss_data['Export Quantity (kg)'].apply(format_swiss_number)
impex_swiss_data['Net (kg)'] = impex_swiss_data['Net (kg)'].apply(format_swiss_number)
impex_swiss_data['Yield (m^2/kg)'] = impex_swiss_data['Yield (m^2/kg)'].apply(format_swiss_number)
impex_swiss_data['Share (%)'] = impex_swiss_data['Share (%)'].apply(format_swiss_number)
impex_swiss_data['Weighted (m^2/kg)'] = impex_swiss_data['Weighted (m^2/kg)'].apply(format_swiss_number)

# Show the result
st.subheader(f"Biodiversity Calculation (Swiss Trade) for {selected_crop.title()}")
st.dataframe(impex_swiss_data)

# Display the total sum
st.write(f"Total Sum: {format_swiss_number(positive_net_sum)}")
st.write(f"Total Share: {format_swiss_number(total_share)}")