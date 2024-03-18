import pandas as pd
import numpy as np
import streamlit as st

from format_functions import format_swiss_number, format_swiss_number_sci

def calc_biodiversity_world(impex_world_data, countries_data, pdf_data, crop_type, yield_data):
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

    # Merge the columns by country code
    result_world_data_merged = pd.merge(result_world_data, pdf_data, left_on='short', right_on='country_code', how='left')

    result_world_data_merged['occupation'].fillna('', inplace=True)  # Replace NaN with empty string

    # Filter to just use the current crop type
    result_world_data_merged = result_world_data_merged[result_world_data_merged['occupation'].str.contains(crop_type)]
    result_world_data_merged.reset_index(drop=True, inplace=True)

    st.write("result", result_world_data)
    st.write("merged", result_world_data_merged)

    # Fill NaN values in 'amount' with 0
    #result_world_data['PDF Factor'] = result_world_data_merged['amount']

    for index, row in result_world_data.iterrows():
        country_code = row['short']
        for idx, merged_row in result_world_data_merged.iterrows():
            if merged_row['country_code'] == country_code:
                result_world_data.at[index, 'PDF Factor'] = merged_row['amount']
                break

    st.write("after loop", result_world_data)

    #st.write(type(result_world_data['PDF Factor'][0]))
    result_world_data['PDF (PDF/kg)'] = result_world_data['PDF Factor'] * result_world_data['Weighted (m^2/kg)']

    # Rename columns
    result_world_data = result_world_data.rename(columns={'Area': 'Trade Partner', 'short': 'Code', 'Value_x': 'Import (t)', 'Value_y': 'Yield (m^2/kg)'})

    # Reorder the columns
    result_world_data = result_world_data[['Trade Partner', 'Code', 'Import (t)', 'Export (t)', 'Net Export (t)', 'Yield (m^2/kg)', 'Share (%)', 'Weighted (m^2/kg)', 'PDF Factor', 'PDF (PDF/kg)']]

    # Get top PDF countries
    result_world_data_viz = result_world_data.nlargest(25, 'PDF (PDF/kg)')

    # Calculate total PDF
    total_world_pdf = result_world_data['PDF (PDF/kg)'].sum(skipna=True)

    # Apply the custom formatting function
    result_world_data['Import (t)'] = result_world_data['Import (t)'].apply(format_swiss_number)
    result_world_data['Export (t)'] = result_world_data['Export (t)'].apply(format_swiss_number)
    result_world_data['Net Export (t)'] = result_world_data['Net Export (t)'].apply(format_swiss_number)
    result_world_data['Yield (m^2/kg)'] = result_world_data['Yield (m^2/kg)'].apply(format_swiss_number_sci)
    result_world_data['Share (%)'] = result_world_data['Share (%)'].apply(format_swiss_number)
    result_world_data['Weighted (m^2/kg)'] = result_world_data['Weighted (m^2/kg)'].apply(format_swiss_number_sci)
    result_world_data['PDF Factor'] = result_world_data['PDF Factor'].apply(format_swiss_number_sci)
    result_world_data['PDF (PDF/kg)'] = result_world_data['PDF (PDF/kg)'].apply(format_swiss_number_sci)

    return result_world_data, total_world_pdf, result_world_data_viz