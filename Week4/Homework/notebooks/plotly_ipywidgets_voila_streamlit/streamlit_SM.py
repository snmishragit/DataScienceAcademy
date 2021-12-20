import streamlit as st
import pandas as pd
import numpy as np
import csv
import plotly.express as px

#df = px.data.gapminder() C:\Users\snmishra\OneDrive - Educational Testing Service\DataScienceAcademy\Week4\OneDrive_2021-11-29 (1)\data for week4

df = pd.read_csv('C://Users/snmishra/OneDrive - Educational Testing Service/DataScienceAcademy/Week4/OneDrive_2021-11-29 (1)/data for week4/science_response.csv')

print(df)

st.title('Welcome to the Streamlit Dashboard - SM')

#conti = st.sidebar.selectbox("Please select one continent: ", ['Asia', 'Europe', 'Africa', 'Americas', 'Oceania'])
gender = st.sidebar.selectbox("Please select a gender: ", ['Male', 'Female'])

#fig = px.scatter(df.query('continent==@conti'), x="gdpPercap", y="lifeExp", size="pop", color="country", hover_name="country", log_x=True, size_max=60,animation_frame='year',range_y=[20,100])

fig = px.scatter(df.query('gender==@gender'), x="playerID", y="sum_score",  color="gender", hover_name="gender")


st.plotly_chart(fig)

