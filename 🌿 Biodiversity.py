import streamlit as st
import pandas as pd
import locale
import numpy as np

from crop_selector import select_crop

# Set the default locale for all numbers
# locale.setlocale(locale.LC_NUMERIC, 'de_CH')

st.set_page_config(layout="wide")

st.title("🌿 Biodiversity")

selected_crop, crop_type, impex_data, yield_data = select_crop()

# Load the countries lookup table
countries_data = pd.read_csv("./data/countries.csv")

# Filter only import and export data
import_data = impex_data[impex_data['Element'] == 'Import Quantity'].set_index('Area')['Value']
export_data = impex_data[impex_data['Element'] == 'Export Quantity'].set_index('Area')['Value']

# Create a DataFrame with import, export, and net columns
result_data = pd.DataFrame({
    'Import (t))': import_data,
    'Export (t))': export_data
})

# Fill NaN values with 0
result_data = result_data.fillna(0)

# Calculate the net quantity
result_data['Net (t)'] = result_data['Import (t))'] - result_data['Export (t))']

# Calculate the total sum considering only positive net values
positive_net_sum = result_data['Net (t)'][result_data['Net (t)'] > 0].sum()

# Calculate the share in percentage, clip to ensure it's not negative
result_data['Share (%)'] = (result_data['Net (t)'] / positive_net_sum * 100).clip(lower=0)

# Calculate the total share excluding NaN values
total_share = result_data['Share (%)'].sum(skipna=True)

# Reset index to make 'Area' a regular column
result_data = result_data.reset_index()

# Make sure the "Area" values are unique before setting the index
impex_data_unique_areas = impex_data[impex_data['Element'] == 'Import Quantity'].set_index('Area').drop_duplicates()

# Filter result_data to only include rows with valid "Area" values
result_data = result_data[result_data['Area'].isin(impex_data_unique_areas.index)]

# Merge with countries lookup table to get short codes
result_data = pd.merge(result_data, countries_data[['Name', 'short']], left_on='Area', right_on='Name', how='left')

# Drop redundant columns
result_data = result_data.drop(['Name'], axis=1)

# Keep 'Area Code (M49)' in the result table
result_data['Area Code (M49)'] = impex_data_unique_areas.loc[result_data['Area'], 'Area Code (M49)'].values

# Perform a lookup to get "Yield" from yield_data
result_data = pd.merge(result_data, yield_data[['Area Code (M49)', 'Value']], left_on='Area Code (M49)', right_on='Area Code (M49)', how='left')

# Fill NaN values in "Yield" with 0
result_data['Yield (m^2/kg)'] = result_data['Value'].fillna(0)

# Convert "Yield" from 100g/ha to kg/m² and then invert to get m²/kg
result_data['Yield (m^2/kg)'] = 1 / (result_data['Yield (m^2/kg)'] / 100)  # 1 / (100g/ha) = kg/m²

# Replace infinite values with NaN
result_data = result_data.replace([np.inf, -np.inf], np.nan)

# Replace NaN values with 0
result_data = result_data.fillna(0)

# Calculate the 'Weighted (m^2/kg)' column
result_data['Weighted (m^2/kg)'] = (result_data['Yield (m^2/kg)'] * result_data['Share (%)']) / total_share

# Rename columns
result_data = result_data.rename(columns={'Area': 'Trade Partner', 'short': 'Code', 'Value_x': 'Import (t))', 'Value_y': 'Yield (m^2/kg)'})

# Reorder the columns
result_data = result_data[['Trade Partner', 'Area Code (M49)', 'Code', 'Import (t))', 'Export (t))', 'Net (t)', 'Yield (m^2/kg)', 'Share (%)', 'Weighted (m^2/kg)']]

# Custom function for Swiss number formatting
def format_swiss_number(number):
    formatted_number = locale.format("%0.4f", number, grouping=True)
    return formatted_number.replace(locale.localeconv()['decimal_point'], '.')

# Apply the custom formatting function
result_data['Import (t))'] = result_data['Import (t))'].apply(format_swiss_number)
result_data['Export (t))'] = result_data['Export (t))'].apply(format_swiss_number)
result_data['Net (t)'] = result_data['Net (t)'].apply(format_swiss_number)
result_data['Yield (m^2/kg)'] = result_data['Yield (m^2/kg)'].apply(format_swiss_number)
result_data['Share (%)'] = result_data['Share (%)'].apply(format_swiss_number)
result_data['Weighted (m^2/kg)'] = result_data['Weighted (m^2/kg)'].apply(format_swiss_number)

# Show the result in Streamlit
st.subheader(f"Biodiversity Calculation for {selected_crop.title()}")
st.dataframe(result_data)

# Display the total sum
st.write(f"Total Sum: {format_swiss_number(positive_net_sum)}")
st.write(f"Total Share: {format_swiss_number(total_share)}")
