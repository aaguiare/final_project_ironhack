import requests
import streamlit as st
import pydeck as pdk
import pandas as pd
from geopy.geocoders import Nominatim
import time
from geopy.distance import geodesic
import os

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

st.title('The Recycling Act - Madrid')

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


def display_map(user_lat, user_lon, df_to_display, route=None, user_address=None):
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

    # Check if more than one type is selected and add colored layers accordingly
    if len(df_to_display['TYPE'].unique()) > 1:
        for bin_type in df_to_display['TYPE'].unique():
            df_filtered = df_to_display[df_to_display['TYPE'] == bin_type]
            color = [255, 0, 0]  # Default to 'Varios' if not found
            layer = pdk.Layer(
                'ScatterplotLayer',
                df_filtered,
                get_position='[LONGITUDE, LATITUDE]',
                get_color=color,  # Use the color map
                get_radius=30,
                pickable=True,
                auto_highlight=True,
                tooltip={"text": f"Dirección: {{DIRECTIONS}}"}
            )
            layers.append(layer)
    else:
        # Fallback to a single layer in neutral color if only one type is selected or if df_to_display is not properly tagged
        neutral_layer = pdk.Layer(
            'ScatterplotLayer',
            df_to_display,
            get_position='[LONGITUDE, LATITUDE]',
            get_color=[255, 0, 0],  # Neutral color
            get_radius=30,
            pickable=True,
            auto_highlight=True,
            tooltip={"text": f"Dirección: {{DIRECTIONS}}"}
        )
        layers.append(neutral_layer)

    # Add route layer if route data is available
    if route and 'features' in route and len(route['features']) > 0:
        #route_geometry = route['features'][0]['geometry']
        route_layer = pdk.Layer(
        'PathLayer',
        data=pd.DataFrame({"path": [route['features'][0]['geometry']['coordinates']]}),
        get_path="path",
        width_scale=20,
        width_min_pixels=2,
        get_color=[255, 100, 100],  # Color for the route
        pickable=True,
    )
    layers.append(route_layer)
    
    origin_layer = pdk.Layer(
                'ScatterplotLayer',
                data=[{
                    "position": [user_lon, user_lat],
                    "DIRECTIONS": user_address if user_address else 'Inicio ruta no especificada'
                }],
                get_position='position',
                get_color=[0, 0, 255],  # Blue color for the origin point
                get_radius=20,  # Adjust size as needed
                pickable=True,
                tooltip = {"text": "{DIRECTIONS}"}
    )
    layers.append(origin_layer)

    if not df_to_display.empty:
        endpoint_address = df_to_display.iloc[0]['DIRECTIONS']  # Assuming this contains the destination address

        # Create an IconLayer for the endpoint
        destination_layer = pdk.Layer(
            "IconLayer",
            data=[{
                "position": route['features'][0]['geometry']['coordinates'][-1],
                "DIRECTIONS": endpoint_address 
            }],
            get_position='position',
            get_color=[255, 0, 0],  # Red color for the destination point
            get_radius=30,
            pickable=True,
            tooltip={"text": "{DIRECTIONS}"}
        )
        layers.append(destination_layer)
           

    r = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=user_lat, longitude=user_lon, zoom=14),
        map_style='mapbox://styles/mapbox/light-v9',
    )
    st.pydeck_chart(r)

def display_single_bin_type_info(selected_type, nearest_location, moviles):
    specific_bin_types = [
        'Enseres', 'Restos de poda', 'Jeringuillas', 'Cintas y CDs',
        'Escombros', 'Metal', 'Cápsulas café', 'Electrodomésticos', 'Material peligroso'
    ]
    schedule_info = nearest_location.get('SCHEDULE', 'No disponible')
    is_in_moviles = nearest_location.name in moviles.index
    if is_in_moviles:
        st.write(f"El punto limpio móvil más cercano para {selected_type} está en: {nearest_location['DIRECTIONS']}, a {nearest_location['DISTANCE']:.2f} km de distancia.\nHorario: {schedule_info}")
    else:
        st.write(f"El punto limpio más cercano para {selected_type} está en: {nearest_location['DIRECTIONS']}, a {nearest_location['DISTANCE']:.2f} km de distancia.")

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
                
                df_to_display['DISTANCE'] = df_to_display.apply(lambda row: geodesic((user_lat, user_lon), (row['LATITUDE'], row['LONGITUDE'])).km, axis=1)

    # Aggregate data to find locations offering the most bin types
                aggregated_data = df_to_display.groupby(['LATITUDE', 'LONGITUDE']).agg({
                    'DISTANCE': 'mean',  # Average distance to user for each group
                    'TYPE': lambda x: len(set(x))  # Count of unique bin types per group
                }).reset_index()

    # Sort by the number of bin types and then by distance
                aggregated_data.sort_values(by=['TYPE', 'DISTANCE'], ascending=[False, True], inplace=True)

            if not aggregated_data.empty:
        # Select the top location offering the most bin types within the shortest distance
                optimal_location = aggregated_data.iloc[0]
                disposal_lat = optimal_location['LATITUDE']
                disposal_lon = optimal_location['LONGITUDE']

    # Fetch the route data from the user's location to the disposal point
                route = get_route(user_lat, user_lon, disposal_lat, disposal_lon)

        # Find all entries in df_to_display that match the optimal location's coordinates
                optimal_entries = df_to_display[(df_to_display['LATITUDE'] == optimal_location['LATITUDE']) & (df_to_display['LONGITUDE'] == optimal_location['LONGITUDE'])]

        # Ensure the display message combines all selected types
                types_str = ", ".join(bin_type[:-1]) + " y " + bin_type[-1] if len(bin_type) > 1 else bin_type[0]
                address = f"{optimal_entries.iloc[0]['DIRECTIONS']}, a {optimal_location['DISTANCE']:.2f} km de distancia"
                if 'SCHEDULE' in optimal_entries.columns:
                    schedule = optimal_entries.iloc[0]['SCHEDULE']
                    if pd.isnull(schedule): 
                        summary_message = f"El punto óptimo que reúne los contenedores de {types_str} está en: {address}. Horario no disponible"             
                    else: 
                        summary_message = f"El punto óptimo que reúne los contenedores de {types_str} está en: {address}. Horario: {schedule}"
                else:
                    summary_message = f"El punto óptimo que reúne los contenedores de {types_str} está en: {address}. Horario no disponible"

                st.write(summary_message)
                

        # Display the map pointing to the optimal location
                try:
                    display_map(user_lat=user_lat, user_lon=user_lon, df_to_display=optimal_entries, route=route,user_address=user_address)
                except Exception as e:
                    st.error(f"Error al mostrar el mapa: {e}")
            else:
                st.write("No se encontraron puntos de recogida cercanos para los tipos de residuos seleccionados.")
            #else:
                #st.write("No se han encontrado datos para los tipos de residuos seleccionados.")
        else:
            st.error("No se pudo identificar la ubicación. Intenta con una dirección más específica.")
    except Exception as e:
        st.error(f"Error al encontrar la dirección: {e}")