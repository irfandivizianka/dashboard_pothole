import streamlit as st
from google.cloud import firestore
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium
import plotly.express as px

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json("firestore-key.json")

# Create a reference to the collection 'pothole'.
posts_ref = db.collection("pothole")

# Get all documents from the collection.
docs = posts_ref.stream()

# Initialize lists to store the documents data.
data = []
locations = []
details = [] 
pictures = []

for doc in docs:
    doc_dict = doc.to_dict()
    doc_dict["id"] = doc.id  # Add the document ID to the data.
    data.append(doc_dict)
    
    # Extract latitude and longitude for location plotting
    location = doc_dict.get("location")
    if location:
        locations.append((location.latitude, location.longitude))
    
    # Extract details and append to details list
    details.append(doc_dict.get("details", ""))

    # Extract picture URLs and append to pictures list
    pictures.append(doc_dict.get("pict", ""))

    

# Convert the data to a Pandas DataFrame.
df = pd.DataFrame(data)

# Display the DataFrame in Streamlit.
# st.title("Dashboard Monitoring Jalan Berlubang")
# st.write("Kenali Jalan Berlubang Di Sekitarmu",text_align='center')

st.markdown("<h1 style='text-align: center;'>Dashboard Monitoring </h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Jalan Berlubang</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Kota Bekasi</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Kenali Jalan Berlubang Disekitarmu!</p>", unsafe_allow_html=True)

# Create a Folium map.
if not df.empty:
    # Convert Firestore timestamp to string for better readability.
    df['createdAt'] = df['createdAt'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if isinstance(x, datetime) else x)

    # Initialize a Folium map
    m = folium.Map(location=[-6.200000, 106.816666], zoom_start=10, control_scale=True)  # Jakarta coordinates as initial point

    # Add markers to the map.
    for index, row in df.iterrows():
        # Format the location if it's a GeoPoint
        location = row["location"]
        if isinstance(location, firestore.GeoPoint):
            latitude = location.latitude
            longitude = location.longitude
            popup_content = f"""
            <div style="width: 300px;">
                <div style="font-size: 14pt;">
                    <b>Title:</b> {row['title']}<br>
                    <b>Details:</b> {row['details']}<br>
                    <b>Created At:</b> {row['createdAt']}<br>
                    <b>Location:</b> {latitude}° S, {longitude}° E<br>
                    <b>Picture:</b> <br> <img src="{row['pict']}" width="150"/>
                </div>
            </div>
            """
            folium.Marker(
                [latitude, longitude],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=row['title']
            ).add_to(m)

    # Display the map in Streamlit with increased size
    st_folium(m, width=1000, height=700)

    # # Display additional plots below the map
    # st.subheader("Visualisasi Data Jalan Berlubang")

    
    st.markdown("<h1 style='text-align: center;'>Visualisasi Data Jalan Berlubang</h1>", unsafe_allow_html=True)

    # Plot a bar chart for details count
    details_df = pd.DataFrame({"Details": details})  # Create DataFrame for details
    details_counts = details_df["Details"].value_counts().reset_index()
    details_counts.columns = ["Details", "Jumlah"]
    fig_bar = px.bar(details_counts, x="Details", y="Jumlah", labels={"x": "Details", "y": "Jumlah"}, title="Detail Penyebaran Lokasi")
    st.plotly_chart(fig_bar)

    # # Plot a pie chart for location distribution
    # locations_df = pd.DataFrame(locations, columns=["Latitude", "Longitude"])
    # fig_pie = px.scatter_mapbox(locations_df, lat="Latitude", lon="Longitude", title="Locations Distribution")
    # fig_pie.update_layout(mapbox_style="open-street-map", mapbox_zoom=10, mapbox_center={"lat": -6.200000, "lon": 106.816666})
    # st.plotly_chart(fig_pie)

    # st.markdown("<h1 style='text-align: center;'>Galeri Gambar</h1>", unsafe_allow_html=True)
    
    # # Display a grid gallery of images
    # if not df.empty and pictures:
    #     st.subheader("")
    
    # # Display images in a grid
    #     col1, col2, col3 = st.columns(3)  # Create 3 columns for the grid layout
    #     for i, picture_url in enumerate(pictures):
    #         with col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3:
    #             st.image(picture_url, caption=f"Picture {i+1}", use_column_width=True)
            
    # st.write("No data found in the collection.")
