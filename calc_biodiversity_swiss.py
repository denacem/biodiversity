import pandas as pd
import numpy as np
import streamlit as st

from format_functions import format_swiss_number, format_swiss_number_sci

def calc_biodiversity_swiss(impex_swiss_data, countries_data, pdf_data, crop_type, yield_data):
    # Fill NaN values with 0
    result_swiss_data = impex_swiss_data.fillna(0)

    # Convert to numbers
    result_swiss_data['Import Quantity (kg)'] = pd.to_numeric(result_swiss_data['Import Quantity (kg)'], errors='coerce')
    result_swiss_data['Export Quantity (kg)'] = pd.to_numeric(result_swiss_data['Export Quantity (kg)'], errors='coerce')

    # Calculate the net quantity
    result_swiss_data['Net (kg)'] = result_swiss_data['Import Quantity (kg)'] - result_swiss_data['Export Quantity (kg)']

    # Calculate the total sum considering only positive net values
    positive_net_sum = result_swiss_data['Net (kg)'][result_swiss_data['Net (kg)'] > 0].sum()

    # Calculate the share in percentage, clip to ensure it's not negative
    result_swiss_data['Share (%)'] = (result_swiss_data['Net (kg)'] / positive_net_sum * 100).clip(lower=0)

    # Calculate the total share excluding NaN values
    total_share = result_swiss_data['Share (%)'].sum(skipna=True)

    # Reset index to make 'Trade Partner' a regular column
    result_swiss_data = result_swiss_data.reset_index()

    # Make sure the 'Area' values are unique before setting the index
    result_swiss_data_unique_areas = result_swiss_data.set_index('Trade Partner').drop_duplicates()

    # Filter result_swiss_data to only include rows with valid 'Area' values
    result_swiss_data = result_swiss_data[result_swiss_data['Trade Partner'].isin(result_swiss_data_unique_areas.index)]

    # Keep 'Area Code (M49)' in the result table
    #result_swiss_data['Area Code (M49)'] = result_swiss_data_unique_areas.loc[result_swiss_data['Trade Partner'], 'Area Code (M49)'].values

    # Remove leading whitespaces
    result_swiss_data['Trade Partner'] = result_swiss_data['Trade Partner'].str.lstrip()

    # Drop redundant columns
    result_swiss_data = result_swiss_data.drop(['index'], axis=1)

    # Perform a lookup to get 'Yield' from yield_data
    result_swiss_data = pd.merge(result_swiss_data, yield_data[['Area', 'Value']], left_on='Trade Partner', right_on='Area', how='left')

    # Fill NaN values in 'Yield' with 0
    result_swiss_data['Yield (m^2/kg)'] = result_swiss_data['Value'].fillna(0)

    # Convert 'Yield' from 100g/ha to kg/m² and then invert to get m²/kg
    #then it's land use!
    result_swiss_data['Yield (m^2/kg)'] = 1 / (result_swiss_data['Yield (m^2/kg)'] / 100000)  # 1 / (100g/ha) = kg/m²

    # Replace infinite values with NaN
    result_swiss_data = result_swiss_data.replace([np.inf, -np.inf], np.nan)

    # Replace NaN values with 0
    result_swiss_data = result_swiss_data.fillna(0)

    # Calculate the 'Weighted (m^2/kg)' column
    result_swiss_data['Weighted (m^2/kg)'] = (result_swiss_data['Yield (m^2/kg)'] * result_swiss_data['Share (%)']) / total_share

    # Merge with countries lookup table to get short codes
    result_swiss_data = pd.merge(result_swiss_data, countries_data[['Name', 'short']], left_on='Trade Partner', right_on='Name', how='left')

    # Merge the columns so get pdf factors
    result_swiss_data_merged = pd.merge(result_swiss_data, pdf_data, left_on='short', right_on='country_code', how='left')

    result_swiss_data_merged['occupation'].fillna('', inplace=True)  # Replace NaN with empty string

    # Filter to just use the current crop type
    result_swiss_data_merged = result_swiss_data_merged[result_swiss_data_merged['occupation'].str.contains(crop_type)]
    result_swiss_data_merged.reset_index(drop=True, inplace=True)

    # Get the PDF factor
    result_swiss_data['PDF Factor'] = result_swiss_data_merged['amount']

    result_swiss_data['PDF (PDF/kg)'] = result_swiss_data['PDF Factor'] * result_swiss_data['Weighted (m^2/kg)']

    # Reorder the columns
    result_swiss_data = result_swiss_data[['Trade Partner', 'Import Quantity (kg)', 'Export Quantity (kg)', 'Net (kg)', 'Yield (m^2/kg)', 'Share (%)', 'Weighted (m^2/kg)', 'PDF Factor', 'PDF (PDF/kg)']]

    #Get top PDF countries
    result_swiss_data_top = result_swiss_data.nlargest(25, 'PDF (PDF/kg)')

    # Calculate total PDF
    total_swiss_pdf = result_swiss_data['PDF (PDF/kg)'].sum(skipna=True)

    # Apply the custom formatting function
    result_swiss_data['Import Quantity (kg)'] = result_swiss_data['Import Quantity (kg)'].apply(format_swiss_number)
    result_swiss_data['Export Quantity (kg)'] = result_swiss_data['Export Quantity (kg)'].apply(format_swiss_number)
    result_swiss_data['Net (kg)'] = result_swiss_data['Net (kg)'].apply(format_swiss_number)
    result_swiss_data['Yield (m^2/kg)'] = result_swiss_data['Yield (m^2/kg)'].apply(format_swiss_number_sci)
    result_swiss_data['Share (%)'] = result_swiss_data['Share (%)'].apply(format_swiss_number)
    result_swiss_data['Weighted (m^2/kg)'] = result_swiss_data['Weighted (m^2/kg)'].apply(format_swiss_number_sci)
    result_swiss_data['PDF Factor'] = result_swiss_data['PDF Factor'].apply(format_swiss_number_sci)
    result_swiss_data['PDF (PDF/kg)'] = result_swiss_data['PDF (PDF/kg)'].apply(format_swiss_number_sci)

    return result_swiss_data, total_swiss_pdf, result_swiss_data_top