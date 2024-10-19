import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import branca.colormap as cm
import random
import string

# Load Florida county GeoJSON file
florida_counties = gpd.read_file(r'C:\Users\yousi\Desktop\python\geojson-fl-counties-fips.json')

# Generate random data for members with different conditions in Jacksonville, FL
def generate_member_data():
    conditions = ['Hypertension'] * 5 + ['CKD'] * 10 + ['Diabetes'] * 20
    latitudes = [random.uniform(30.2, 30.4) for _ in range(35)]
    longitudes = [random.uniform(-81.7, -81.5) for _ in range(35)]
    
    def generate_id():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def generate_phone():
        return f"(904) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    def generate_address():
        streets = ["Main St", "Oak Ave", "Pine Rd", "Maple Ln", "Cedar Blvd"]
        return f"{random.randint(100, 9999)} {random.choice(streets)}, Jacksonville, FL {random.randint(32200, 32277)}"
    
    return pd.DataFrame({
        'MemberID': [generate_id() for _ in range(35)],
        'Condition': conditions,
        'Latitude': latitudes,
        'Longitude': longitudes,
        'Address': [generate_address() for _ in range(35)],
        'Phone': [generate_phone() for _ in range(35)]
    })




special_member = {
  'MemberID': 'ABC12345',
  'Condition': 'Heart Disease',  # Set the desired condition
  'Latitude': 30.32,  # Set the desired latitude (Jacksonville)
  'Longitude': -81.65,  # Set the desired longitude (Jacksonville)
  'Address': '123 Main St, Jacksonville, FL 32222',  # Set the desired address
  'Phone': '(904) 555-1212'  # Set the desired phone number
}

# Combine special member data with randomly generated data
member_data = pd.concat([pd.DataFrame([special_member]), generate_member_data()])

# Assuming you have a DataFrame with member data for counties
df_members = pd.DataFrame({
    'COUNTY': ['Duval', 'Nassau', 'Baker', 'Orange', 'Putnam'],
    'MEMBERS': [2000, 800, 600, 700, 750]
})

# Merge GeoDataFrame with member data
florida_counties = florida_counties.merge(df_members, left_on='NAME', right_on='COUNTY', how='left')
florida_counties['MEMBERS'] = florida_counties['MEMBERS'].fillna(0)

# Create a color map for counties
min_members = florida_counties['MEMBERS'].min()
max_members = florida_counties['MEMBERS'].max()
colormap = cm.LinearColormap(colors=['#FFEDA0', '#FEB24C', '#F03B20'], 
                             vmin=min_members, vmax=max_members)

# Streamlit app
st.title('Florida Health Map')

# Toggle between county view and member view
view_option = st.radio("Select View", ["County View", "Member View"])

# Condition selection for member view
if view_option == "Member View":
    selected_condition = st.selectbox("Select Condition", ["All", "Hypertension", "CKD", "Diabetes"])

# Create a map centered on Florida
if view_option == "County View":
    m = folium.Map(location=[28.1, -83.5], zoom_start=7)
else:  # Member View
    m = folium.Map(location=[30.3, -81.6], zoom_start=11)  # Centered on Jacksonville

if view_option == "County View":
    # Add county polygons to the map
    folium.GeoJson(
        florida_counties,
        style_function=lambda feature: {
            'fillColor': colormap(feature['properties']['MEMBERS']),
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=['NAME', 'MEMBERS'], 
                                      aliases=['County:', 'Members:'],
                                      localize=True),
    ).add_to(m)

    # Add a color legend
    colormap.add_to(m)

else:  # Member View
    # Filter data based on selected condition
    if selected_condition != "All":
        filtered_data = member_data[member_data['Condition'] == selected_condition]
    else:
        filtered_data = member_data

    # Add member markers to the map
    for _, row in filtered_data.iterrows():
        popup_html = f"""
        <b>Member ID:</b> {row['MemberID']}<br>
        <b>Condition:</b> {row['Condition']}<br>
        <b>Address:</b> {row['Address']}<br>
        <b>Phone:</b> {row['Phone']}<br>
        <a href="https://www.care.com/{row['MemberID']}" target="_blank">View in Member Research Tool</a>
        """
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"Member {row['MemberID']}",
            color="red",
            fill=True,
            fillColor="red"
        ).add_to(m)

# Display the map using st_folium
st_folium(m, returned_objects=[])

# Display information about the view
if view_option == "County View":
    st.write("Click on a county to see membership information.")
else:
    st.write("Click on a member marker to see detailed information and access the Member Research Tool.")

# Display selected member information
if view_option == "Member View":
    st.subheader("Selected Member Information")
    selected_member = st.selectbox("Select a Member ID", options=filtered_data['MemberID'].tolist())
    member_info = filtered_data[filtered_data['MemberID'] == selected_member].iloc[0]
    st.write(f"**Member ID:** {member_info['MemberID']}")
    st.write(f"**Condition:** {member_info['Condition']}")
    st.write(f"**Address:** {member_info['Address']}")
    st.write(f"**Phone:** {member_info['Phone']}")
    st.markdown(f"[View in Member Research Tool](https://www.care.com/{member_info['MemberID']})")