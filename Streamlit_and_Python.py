# import streamlit as sl
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
    "Motor_Vehicle_Collisions_-_Crashes.csv"
)


st.title("Fatgezim 'Zim' Bela")
st.markdown(
    "Showing the power of Streamlit Dashboards! Through Analysis of Motor Vehicle Collisisons in NYC!")


@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[
                       ['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    data.rename(columns={'LATITUDE': 'latitude'}, inplace=True)
    data.rename(columns={'LONGITUDE': 'longitude'}, inplace=True)
    data.rename(columns={'CRASH_DATE_CRASH_TIME': 'date/time'}, inplace=True)
    return data


data = load_data(10000)


# Good link for Sliders https://discuss.streamlit.io/t/how-to-initialize-the-value-of-slider/12999

st.header("Where are most people injured in NYC?")
injured_people = st.slider("Number of people injured in MVC", 0, 19, value=2)
st.map(data.query("INJURED_PERSONS >= @injured_people")
       [["latitude", "longitude"]].dropna(how="any"))


st.header("How many crashes at any time of day?")

hour = st.slider("hour to look at: ", 0, 23)
data = data[data['date/time'].dt.hour == hour]


st.header("How many collisions between %i:00 and %i:00?" %
          (hour, (hour + 1) % 24))
midpoint = np.average(data['latitude']), np.average(data['longitude'])

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 10,
        "pitch": 60,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],
            get_position=["longitude", "latitude"],
            radius=150,
            elevation_scale=4,
            pickable=True,
            elevation_range=[10, 1000],
            extruded=True,
            coverage=1,

        ),
    ],
))




st.subheader("Breakdown by minute between %i:00 and %i:00" %
             (hour, (hour + 1) % 24))

# filtering the data between two hours and grouping by minute
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]

# grouping by minute and counting the number of crashes
# plotting the histogram
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]

# plotting the chart and setting the dataframe. The x-axis is the minutes and the y-axis is the number of crashes
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})

# show the chart
fig = px.bar(chart_data, x='minute', y='crashes',
             hover_data=['minute', 'crashes'], height=300)
st.write(fig)



st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people', [
                      'Pedestrians', 'Cyclists', 'Motorists'])


if select == 'Pedestrians':
    st.write(data.query("INJURED_PERSONS >= 1")[["ON_STREET_NAME", "date/time", "INJURED_PERSONS"]].sort_values(
        by=['INJURED_PERSONS'], ascending=False).dropna(how="any")[:5])
elif select == 'Cyclists':
    st.write(data.query("INJURED_PERSONS >= 1")[["ON_STREET_NAME", "date/time", "INJURED_PERSONS"]].sort_values(
        by=['INJURED_PERSONS'], ascending=False).dropna(how="any")[:5])
elif select == 'Motorists':
    st.write(data.query("INJURED_PERSONS >= 1")[["ON_STREET_NAME", "date/time", "INJURED_PERSONS"]].sort_values(
        by=['INJURED_PERSONS'], ascending=False).dropna(how="any")[:5])

if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
