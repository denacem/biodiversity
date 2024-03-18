import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

from crop_selector import select_crop

st.set_page_config(layout="wide")

st.title("📊 Import / Export and Yield Data")

selected_crop, crop_type, impex_world_data, impex_swiss_data, yield_data = select_crop()

# Display the impex world data using st.dataframe
st.subheader(f"Impex World Data for {selected_crop.title()}")
st.dataframe(impex_world_data)

# Create the bar plot for impex_world_data
plt.figure(figsize=(10, 6))
plt.bar(impex_world_data["Area"], impex_world_data["Value"].astype(float))
plt.xlabel("Country")
plt.ylabel("Value")
plt.title(f"Impex World Value by Country for {selected_crop.title()}")
plt.xticks(rotation=90)
st.pyplot(plt)

# Display the impex swiss data using st.dataframe
st.subheader(f"Impex Swiss Data for {selected_crop.title()}")
st.dataframe(impex_swiss_data)

# Create the bar plot for impex_swiss_data
# Remove commas from the "Value" column and convert to float
#impex_swiss_data["Import Quantity (kg)"] = impex_swiss_data["Import Quantity (kg)"].str.replace(',', '').astype(float)

plt.figure(figsize=(10, 6))
plt.bar(impex_swiss_data["Trade Partner"], impex_swiss_data["Import Quantity (kg)"].astype(float))
plt.xlabel("Country")
plt.ylabel("Value")
plt.title(f"Impex Swiss Value by Country for {selected_crop.title()}")
plt.xticks(rotation=90)
st.pyplot(plt)

# Separate data into import and export DataFrames
import_world_data = impex_world_data[impex_world_data['Element'] == 'Import Quantity'].nlargest(20, 'Value')
export_world_data = impex_world_data[impex_world_data['Element'] == 'Export Quantity'].nlargest(20, 'Value')
import_swiss_data = impex_swiss_data.nlargest(20, 'Import Quantity (kg)')

# Create a horizontal bar chart for world import and export
fig, ax = plt.subplots(figsize=(10, 8))

# Plot world import quantity on the left side
ax.barh(import_world_data['Area'], import_world_data['Value'], color='blue', label='World Import Quantity')

# Plot world export quantity on the right side
ax.barh(export_world_data['Area'], export_world_data['Value'], color='orange', label='World Export Quantity')

# Set labels and title for world
ax.set_xlabel('Quantity (t)')
ax.set_ylabel('Country')
ax.set_title('World Import and Export of ' + selected_crop.title() + ' by Country (top countries)')

# Display legend for world
ax.legend()

# Display the plot for world
st.pyplot(plt)

st.write(import_world_data)
st.write(import_swiss_data)

# Create a horizontal bar chart for Swiss import and export
fig, ax = plt.subplots(figsize=(10, 8))

# Plot Swiss import quantity on the left side
ax.barh(import_swiss_data['Trade Partner'], import_swiss_data['Import Quantity (kg)'], color='red', label='Swiss Import Quantity')

# Set labels and title for Swiss Import
ax.set_xlabel('Import Quantity (kg)')
ax.set_ylabel('Country')
ax.set_title('Swiss Import of ' + selected_crop.title() + ' by Country (top countries)')

# Display legend for Swiss
ax.legend()

# Display the plot for Swiss
st.pyplot(plt)

# Display the yield data using st.dataframe
st.subheader(f"Yield Data for {selected_crop.title()}")
st.dataframe(yield_data)

# Create the bar plot for yield_data
plt.figure(figsize=(10, 6))
plt.bar(yield_data["Area"], yield_data["Value"].astype(float))
plt.xlabel("Country")
plt.ylabel("Value")
plt.title(f"Yield Value by Country for {selected_crop.title()}")
plt.xticks(rotation=90)
st.pyplot(plt)
