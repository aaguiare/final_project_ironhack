import requests
import streamlit as st
import pydeck as pdk
import pandas as pd
from geopy.geocoders import Nominatim
import time
from geopy.distance import geodesic
import os
import base64

# Import your local modules here
from api import client as api
from acquisition import (
    m_puntos_limpios_fijos as fijos,
    m_ropa as ropa,
    m_resto as resto,
    m_envases as envases,
    m_papel as papel,
    m_vidrio as vidrio,
    m_organica as organica,
    m_pilas_marquesinas as pilas,
    m_puntos_limpios_moviles as moviles,
    m_aceite as aceite
)

st.title('Gestión de residuos Madrid')

# Function definitions
def get_nearest_locations(user_lat, user_lon, df, bin_type):
    df['DISTANCE'] = df.apply(lambda row: geodesic((user_lat, user_lon), (row['LATITUDE'], row['LONGITUDE'])).km, axis=1)

    if len(bin_type) > 1:
        # Aggregate distances by location and count unique bin types per location
        aggregated = df.groupby(['LATITUDE', 'LONGITUDE']).agg({'DISTANCE': 'mean', 'TYPE': pd.Series.nunique}).reset_index()
        # Sort by the number of bin types (descending) and then by distance (ascending)
        best_location = aggregated.sort_values(by=['TYPE', 'DISTANCE'], ascending=[False, True]).head(1)
        # Find the original row(s) from df that matches the best location's latitude and longitude
        nearest_locations = df[(df['LATITUDE'] == best_location['LATITUDE'].values[0]) & (df['LONGITUDE'] == best_location['LONGITUDE'].values[0])]
        return nearest_locations
    else:
        # For a single bin type, find the nearest location as before
        return df.loc[df['DISTANCE'].idxmin()].to_frame().T

def get_route(start_lat, start_lon, end_lat, end_lon):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    api_key = os.getenv('token')  # Ensure your API key is stored in an environment variable named 'token'
    headers = {"Authorization": api_key}
    params = {
        "start": f"{start_lon},{start_lat}",
        "end": f"{end_lon},{end_lat}"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def display_map(user_lat, user_lon, df_to_display, route=None,endpoint_icon_path=None):
    layers = []
    color_map = {
    'Aceite': [255, 165, 0],  # Orange
    'Resto': [255, 0, 0],  # Red
    'Orgánica': [165, 42, 42],  # Brown
    'Papel': [0, 0, 255],  # Blue
    'Envases': [255, 87, 51],  # Yellow Mustard
    'Vidrio': [0, 128, 0],  # Green
    'Pilas': [160, 32, 240],  # Purple
    'Ropa': [255, 192, 203],  # Pink
    'Varios': [128, 128, 128]  # Grey for combined categories
    }
    tooltip = {
        "html": "<b>Dirección:</b> {DIRECTIONS}",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white",
            "fontSize": "10px",
            "padding": "3px",
            "maxWidth": "100px"
        }
    }
    # Check if more than one type is selected and add colored layers accordingly
    if len(df_to_display['TYPE'].unique()) > 1:
        for bin_type in df_to_display['TYPE'].unique():
            df_filtered = df_to_display[df_to_display['TYPE'] == bin_type]
            color = color_map.get(bin_type, color_map['Varios'])  # Default to 'Varios' if not found
            layer = pdk.Layer(
                'ScatterplotLayer',
                df_filtered,
                get_position='[LONGITUDE, LATITUDE]',
                get_color=color,  # Use the color map
                get_radius=50,
                pickable=True,
                auto_highlight=True,
                tooltip=tooltip
            )
            layers.append(layer)
    else:
        # Fallback to a single layer in neutral color if only one type is selected or if df_to_display is not properly tagged
        neutral_layer = pdk.Layer(
            'ScatterplotLayer',
            df_to_display,
            get_position='[LONGITUDE, LATITUDE]',
            get_color=[128, 128, 128],  # Neutral color
            get_radius=50,
            pickable=True,
            auto_highlight=True
        )
        layers.append(neutral_layer)

    # Add route layer if route data is available
    if route:
        route_geometry = route['features'][0]['geometry']
        route_layer = pdk.Layer(
            'PathLayer',
            data=pd.DataFrame({"path": [route_geometry['coordinates']]}),
            get_path="path",
            width_scale=20,
            width_min_pixels=2,
            get_color=[255, 100, 100],  # Color for the route
            pickable=True,
        )
        layers.append(route_layer)
    if endpoint_icon_path:
        with open(endpoint_icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        # Prepare the endpoint icon data
        endpoint_icon_data = [{
           "coordinates": route['features'][0]['geometry']['coordinates'][-1],  # The endpoint of the route
            "icon_data": f"data:image/png;base64,{encoded_string}"  # Use base64 image string here
        }]

        # Create an IconLayer for the end points
        icon_layer = pdk.Layer(
            "IconLayer",
            data=endpoint_icon_data,
            get_icon="icon_data",
            get_size=15,
            size_scale=100,
            get_position="coordinates",
            pickable=True
        )
        layers.append(icon_layer)

    r = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=user_lat, longitude=user_lon, zoom=13),
        map_style='mapbox://styles/mapbox/light-v9',
        tooltip=tooltip
    )
    st.pydeck_chart(r)


# Data preparation
dataframes_map = {
    'Textil (No-reusable)': ropa,
    'Resto': resto,
    'Orgánica': organica,
    'Envases': envases,
    'Papel': papel,
    'Vidrio': vidrio,
    'Pilas': pilas,
    'Aceite': aceite 
}

# User selections
bin_type = st.multiselect(
    'Selecciona el tipo de residuo:',
    [
        'Textil (No-reusable)', 'Resto', 'Orgánica', 'Envases', 'Papel',
        'Vidrio', 'Pilas', 'Aceite', 'Enseres', 'Restos de poda', 'Jeringuillas',
        'Cintas y CDs', 'Escombros', 'Metal', 'Cápsulas café', 'Electrodomésticos',
        'Material peligroso'
    ]
)

# User inputs for location
user_address = st.text_input("Ingresa tu dirección:", "")
if user_address:
    geolocator = Nominatim(user_agent="streamlit_example")
    try:
        time.sleep(1)  # To comply with Nominatim usage policy
        location = geolocator.geocode(user_address)
        if location:
            user_lat, user_lon = location.latitude, location.longitude
            df_to_display = pd.DataFrame()

            for selection in bin_type:
                if selection in dataframes_map:
                    temp_df = dataframes_map[selection].copy()  # Make a copy to avoid modifying the original
                    temp_df['TYPE'] = selection  # Assign TYPE based on the selection
                    df_to_display = pd.concat([df_to_display, temp_df], ignore_index=True)
                else:
                    # Handle selections not in dataframes_map, assuming general disposal points are needed
                    # Ensure fijos and moviles have the 'TYPE' column assigned before concatenation
                    fijos['TYPE'] = 'Fijos'  # Assign a generic type or specific if available
                    moviles['TYPE'] = 'Moviles'
                    combined_df = pd.concat([fijos, moviles], ignore_index=True)
                    df_to_display = pd.concat([df_to_display, combined_df], ignore_index=True)

            # Ensure latitudes and longitudes are numeric and not null
            df_to_display['LATITUDE'] = pd.to_numeric(df_to_display['LATITUDE'], errors='coerce')
            df_to_display['LONGITUDE'] = pd.to_numeric(df_to_display['LONGITUDE'], errors='coerce')
            df_to_display.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)

            if not df_to_display.empty:
                #nearest_location = get_nearest_locations(user_lat, user_lon, df_to_display, bin_type)
                df_to_display['DISTANCE'] = df_to_display.apply(lambda row: geodesic((user_lat, user_lon), (row['LATITUDE'], row['LONGITUDE'])).km, axis=1)
                all_nearest_locations = pd.DataFrame()
                    # Display nearest location information to the user
                for selected_type in bin_type:
        # Filter the DataFrame for each selected bin type
                    df_filtered = df_to_display[df_to_display['TYPE'] == selected_type]
                    if not df_filtered.empty:
                        nearest_location = df_filtered.loc[df_filtered['DISTANCE'].idxmin()]
                        all_nearest_locations = pd.concat([all_nearest_locations, nearest_location.to_frame().T])
                        
                if not all_nearest_locations.empty:        
                    displayed_addresses = set()  # Track displayed addresses to avoid duplicates
        # Format the bin types selected by the user for display
                    types_str = ", ".join(bin_type[:-1]) + " y " + bin_type[-1] if len(bin_type) > 1 else bin_type[0]

                    for _, loc in all_nearest_locations.iterrows():
                        address = f"{loc['DIRECTIONS']}, a {loc['DISTANCE']:.2f} km de distancia."
                        if address not in displayed_addresses:
                # Display the message with user-selected bin types (not the 'TYPE' column from df)
                            st.write(f"Los contenedores de {types_str} más cercanos están en: {address}")
                            displayed_addresses.add(address)  # Mark this address as displayed
                    if displayed_addresses:
                        summary_message = f"Los contenedores de {types_str} más cercanos están en: " + "; ".join(displayed_addresses)
                        st.write(summary_message)
                    optimal_route = None  # This would be replaced by actual route obtained from a routing API
                    if optimal_route:
                        try:
                            display_map(user_lat=user_lat, user_lon=user_lon, df_to_display=all_nearest_locations, route=optimal_route, endpoint_icon_path="../data/red2.png")
                        except Exception as e:
                            st.error(f"Error al mostrar el mapa: {e}")
        # Calculate and display the route to the first nearest location
                    #first_nearest_location = nearest_location.iloc[0]
                    #route = get_route(user_lat, user_lon, first_nearest_location['LATITUDE'], first_nearest_location['LONGITUDE'])
                    #if route:
                        #display_map(user_lat=user_lat, user_lon=user_lon, df_to_display=df_to_display, route=route,endpoint_icon_path="../data/red2.png")
                    #else:
                            #st.error("No se pudo obtener la ruta. Asegúrate de que tu API key es válida y tienes acceso a Internet.")
                        #display_map(user_lat=user_lat, user_lon=user_lon, df_to_display=all_nearest_locations, route=optimal_route, endpoint_icon_path="../data/red2.png")
                    #else:
            # Example to display map without the route
                        #display_map(user_lat=user_lat, user_lon=user_lon, df_to_display=all_nearest_locations, route=None, endpoint_icon_path="../data/red2.png")
                else:
                    st.write("No se encontraron puntos de recogida cercanos para los tipos de residuos seleccionados.")
            else:
                st.write("No se han encontrado datos para los tipos de residuos seleccionados.")
        else:
            st.error("No se pudo identificar la ubicación. Intenta con una dirección más específica.")
    except Exception as e:
        st.error(f"Error al encontrar la dirección: {e}")