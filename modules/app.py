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


if bin_type in dataframes_map:
    st.map(dataframes_map[bin_type][['LATITUDE', 'LONGITUDE']])
elif bin_type == 'Varios':
    combined_df = pd.concat([fijos, moviles])
    st.map(combined_df[['LATITUDE', 'LONGITUDE']])
else:

    st.write("Selected bin type is not recognized.")