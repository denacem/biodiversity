import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from crop_selector import select_crop

st.set_page_config(layout="wide")

st.title("📊 Import / Export and Yield Data")

selected_crop, crop_type, impex_data, yield_data = select_crop()

# Display the impex data using st.dataframe
st.subheader(f"Impex Data for {selected_crop.title()}")
st.dataframe(impex_data)

# Create the bar plot for impex_data
plt.figure(figsize=(10, 6))
plt.bar(impex_data["Area"], impex_data["Value"].astype(float))
plt.xlabel("Country")
plt.ylabel("Value")
plt.title(f"Impex Value by Country for {selected_crop.title()}")
plt.xticks(rotation=90)
st.pyplot(plt)

# Separate data into import and export DataFrames
import_data = impex_data[impex_data['Element'] == 'Import Quantity'].nlargest(20, 'Value')
export_data = impex_data[impex_data['Element'] == 'Export Quantity'].nlargest(20, 'Value')

# Create a horizontal bar chart
fig, ax = plt.subplots(figsize=(10, 8))

# Plot import quantity on the left side
ax.barh(import_data['Area'], import_data['Value'], color='blue', label='Import Quantity')

# Plot export quantity on the right side
ax.barh(export_data['Area'], export_data['Value'], color='orange', label='Export Quantity')

# Set labels and title
ax.set_xlabel('Quantity (t)')
ax.set_ylabel('Country')
ax.set_title('Import and Export of ' + selected_crop.title() + ' by Country (ton countries)')

# Display legend
ax.legend()

# Display the plot
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