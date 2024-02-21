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

st.title('Gestión de residuos Madrid')

#Select box
bin_type = st.selectbox('Selecciona el tipo de residuo:', ['Ropa', 'Varios', 'Resto', 'Orgánica', 'Envases', 'Papel','Vidrio','Pilas','Aceite'])

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
    'Envases': [255, 255, 0],  # Yellow
    'Vidrio': [0, 128, 0],  # Green
    'Pilas': [160, 32, 240],  # Purple
    'Ropa': [255, 192, 203],  # Pink
    'Varios': [128, 128, 128]  # Grey for combined categories
}

standard_size = 50

if bin_type in dataframes_map:
     df_to_display = dataframes_map[bin_type]
elif bin_type == 'Varios':
    # Combine DataFrames for 'Varios'
    df_to_display = pd.concat([fijos, moviles])
else:
    st.write("Selected bin type is not recognized.")
    df_to_display = pd.DataFrame()  # Empty DataFrame to prevent errors

# Ensure the DataFrame to display is not empty
if not df_to_display.empty:
    # Convert LATITUDE and LONGITUDE to float if they are not already
    df_to_display['LATITUDE'] = pd.to_numeric(df_to_display['LATITUDE'], errors='coerce')
    df_to_display['LONGITUDE'] = pd.to_numeric(df_to_display['LONGITUDE'], errors='coerce')
    
    # Create the PyDeck layer
    layer = pdk.Layer(
        'ScatterplotLayer',
        df_to_display,
        get_position='[LONGITUDE, LATITUDE]',
        get_color=color_map[bin_type],
        get_radius=standard_size,
        pickable=True,
        auto_highlight=True,
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
    # Set the view
    view_state = pdk.ViewState(latitude=df_to_display['LATITUDE'].mean(), longitude=df_to_display['LONGITUDE'].mean(), zoom=11)

    # Render the map
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, map_style='mapbox://styles/mapbox/light-v9',tooltip=tooltip)
    st.pydeck_chart(r)