import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("💯 Characterisation Factors for Potential Disappearing Fraction (PDF)")

# Read the data from the CSV file
data = pd.read_csv("./data/pdf.csv")

# Reduce dataframe to relevant columns
data = data[["occupation/transformation", "amount", "unit"]]

# Split the 'occupation/transformation' column into two columns
#data[['Type of Transformation', 'Country Code']] = data['occupation/transformation'].str.split(', ', n=1, expand=True)

# Set the global float format
data['amount'] = data['amount'].apply(lambda x: '{:.2e}'.format(x))

# Display the data using st.dataframe
st.dataframe(data)

# Create the bar plot
plt.figure(figsize=(10, 6))
plt.bar(data["occupation/transformation"], data["amount"].astype(float))  # Convert "Birds" back to float for plotting
plt.xlabel("occupation/transformation")
plt.ylabel("amount")
plt.title("amount by occupation/transformation")
plt.xticks(rotation=90)

# Display the Matplotlib plot in the Streamlit app
st.pyplot(plt)
