import requests
import streamlit as st
from acquisition import m_puntos_limpios_fijos as fijos
from acquisition import m_ropa as ropa
from acquisition import m_resto as resto
from acquisition import m_envases as envases
from acquisition import m_papel as papel
from acquisition import m_vidrio as vidrio
from acquisition import m_organica as organica
from acquisition import m_pilas_marquesinas as pilas
from acquisition import m_puntos_limpios_moviles as moviles
from acquisition import m_aceite as aceite
import pydeck as pdk
import pandas as pd
from geopy.geocoders import Nominatim
from sklearn.metrics.pairwise import haversine_distances
from math import radians
import time 
from geopy.distance import geodesic
from api import client as api
import os


st.title('Gestión de residuos Madrid')

#Select box
bin_type = st.selectbox('Selecciona el tipo de residuo:', ['Ropa', 'Resto', 'Orgánica', 'Envases', 'Papel','Vidrio','Pilas','Aceite','Enseres','Restos de poda','Jeringuillas','Cintas y CDs','Escombros','Metal','Cápsulas café', 'Electrodomésticos','Material peligroso'])

# Display the map based on the selection
dataframes_map = {
    'Ropa': ropa,
    'Resto': resto,
    'Orgánica': organica,
    'Envases': envases,
    'Papel': papel,
    'Vidrio': vidrio,
    'Pilas': pilas,
    'Aceite': aceite 
}

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

standard_size = 50
specific_bin_types = [
    'Enseres','Restos de poda','Jeringuillas','Cintas y CDs',
    'Escombros','Metal','Cápsulas café', 'Electrodomésticos','Material peligroso'
]
if bin_type in dataframes_map:
     df_to_display = dataframes_map[bin_type]
elif bin_type in specific_bin_types:
    # Combine DataFrames for 'Varios'
    df_to_display = pd.concat([fijos, moviles])
else:
    st.write("Selected bin type is not recognized.")
    df_to_display = pd.DataFrame()  # Empty DataFrame to prevent errors

# User inputs for location

user_address = st.text_input("Ingresa tu dirección:", "")

if user_address:
    geolocator = Nominatim(user_agent="streamlit_example")
    try:
        time.sleep(1)  # To avoid hitting usage limits
        location = geolocator.geocode(user_address)
        if location:
            user_lat, user_lon = location.latitude, location.longitude
            df_to_display['LATITUDE'] = pd.to_numeric(df_to_display['LATITUDE'], errors='coerce')
            df_to_display['LONGITUDE'] = pd.to_numeric(df_to_display['LONGITUDE'], errors='coerce')
            df_to_display.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)

            # Calculate distances and find the nearest location
            df_to_display['DISTANCE'] = df_to_display.apply(lambda row: geodesic((user_lat, user_lon), (row['LATITUDE'], row['LONGITUDE'])).km, axis=1)
            nearest_location = df_to_display.loc[df_to_display['DISTANCE'].idxmin()]
            nearest_df = pd.DataFrame([nearest_location])

            if bin_type in specific_bin_types or bin_type == 'Varios':
                is_in_moviles = nearest_df.index.isin(moviles.index).any()
                if is_in_moviles:
                    schedule_info = nearest_location.get('SCHEDULE', 'No disponible')
                    st.write(f"El punto limpio móvil más cercano para {bin_type} está en: {nearest_location['DIRECTIONS']}, a {nearest_location['DISTANCE']:.2f} km de distancia.\nHorario: {schedule_info}")
                else:
                    st.write(f"El punto limpio más cercano para {bin_type} está en: {nearest_location['DIRECTIONS']}, a {nearest_location['DISTANCE']:.2f} km de distancia.")
            else:
                st.write(f"El contenedor de {bin_type} más cercano está en: {nearest_location['DIRECTIONS']}, a {nearest_location['DISTANCE']:.2f} km de distancia.")
            
            def get_route(start_lat, start_lon, end_lat, end_lon, api_key):
                url = f"https://api.openrouteservice.org/v2/directions/driving-car"
                api_key = os.getenv('token')
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
            route = get_route(user_lat, user_lon, nearest_location['LATITUDE'], nearest_location['LONGITUDE'], api)
            if route:
                # Extracting the geometry from the route to display on the map
                route_geometry = route['features'][0]['geometry']
                route_layer = pdk.Layer(
                    'PathLayer',
                    data=pd.DataFrame({"path": [route_geometry['coordinates']]}),
                    get_path="path",
                    width_scale=20,
                    width_min_pixels=2,
                    get_color=[255, 100, 100],
                    pickable=True,
                )
            else:
                st.error("No se pudo obtener la ruta. Asegúrate de que tu API key es válida y tienes acceso a Internet.")
            # Map setup
            all_locations_layer = pdk.Layer(
                'ScatterplotLayer',
                df_to_display,
                get_position='[LONGITUDE, LATITUDE]',
                get_color=color_map[bin_type] if bin_type in color_map else color_map['Varios'],
                get_radius=50,
                pickable=True,
                auto_highlight=True
            )
            nearest_location_layer = pdk.Layer(
                'ScatterplotLayer',
                nearest_df,
                get_position='[LONGITUDE, LATITUDE]',
                get_color=[0, 33, 243],  # Highlight color
                get_radius=50,  # Larger to highlight
                pickable=True,
                auto_highlight=True
            )
            tooltip = {
            "html": "{DIRECTIONS}",
            "style": {
            "backgroundColor": "steelblue",
            "color": "white",
            "fontSize": "10px",
            "padding": "3px",
            "maxWidth": "100px"
                }
            }
            view_state = pdk.ViewState(latitude=user_lat, longitude=user_lon, zoom=13)
            r = pdk.Deck(
                layers=[all_locations_layer, nearest_location_layer, route_layer],  # Include route_layer here
                initial_view_state=pdk.ViewState(latitude=user_lat, longitude=user_lon, zoom=13),
                map_style='mapbox://styles/mapbox/light-v9',
                tooltip=tooltip
            )
            st.pydeck_chart(r)
        else:
            st.error("No se pudo identificar la ubicación. Intenta con una dirección más específica.")
    except Exception as e:
        st.error(f"Error al encontrar la dirección: {e}")