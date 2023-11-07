import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Characterisation Factors for Potential Species Loss")

# Read the data from the CSV file
data = pd.read_csv("./data.csv")

# Format numerical columns for display
numerical_columns = ["Mammals", "Birds", "Reptiles", "Amphibians", "Plants"]
for col in numerical_columns:
    data[col] = data[col].apply(lambda x: f"{x:.16f}")

# Display the data using st.dataframe
st.dataframe(data)

# Convert the "Country" column to string type
data["Country"] = data["Country"].astype(str)

# Create the bar plot
plt.figure(figsize=(10, 6))
plt.bar(data["Country"], data["Birds"].astype(float))  # Convert "Birds" back to float for plotting
plt.xlabel("Country")
plt.ylabel("Birds")
plt.title("Birds by Country")
plt.xticks(rotation=90)

# Display the Matplotlib plot in the Streamlit app
st.pyplot(plt)
