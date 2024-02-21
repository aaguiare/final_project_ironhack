import pandas as pd

#Madrid - contenedores varios y puntos limpios - Data load
m_puntos_limpios_moviles = pd.read_csv('../data/Madrid/PuntosLimpiosMoviles.csv', sep = ';')
m_ropa = pd.read_csv('../data/Madrid/ContenedoresRopa.csv', sep = ';')
m_puntos_limpios_fijos = pd.read_csv('../data/Madrid/200284-0-puntos-limpios-fijos.csv', sep = ';', encoding='ISO-8859-1')
m_aceite = pd.read_csv('../data/Madrid/RecogidaContenedoresAceiteUsado.csv', sep = ';')
m_contenedores_varios = pd.read_csv('../data/Madrid/Contenedores_varios.csv', sep = ';')
m_vidrio = m_contenedores_varios[m_contenedores_varios['Tipo Contenedor'] == 'VIDRIO']
m_papel = m_contenedores_varios[m_contenedores_varios['Tipo Contenedor'] == 'PAPEL-CARTON']
m_resto = m_contenedores_varios[m_contenedores_varios['Tipo Contenedor'] == 'RESTO']
m_envases = m_contenedores_varios[m_contenedores_varios['Tipo Contenedor'] == 'ENVASES']
m_organica = m_contenedores_varios[m_contenedores_varios['Tipo Contenedor'] == 'ORGANICA']
m_pilas_marquesinas = pd.read_csv('../data/Madrid/Marquesinas_contenedores_pilas_2022.csv', sep = ';')

#Madrid - contenedores varios y puntos limpios - Data cleaning

#Puntos limpios fijos
m_puntos_limpios_fijos = m_puntos_limpios_fijos.rename(columns={'LATITUD': 'LATITUDE'})
m_puntos_limpios_fijos = m_puntos_limpios_fijos.rename(columns={'LONGITUD': 'LONGITUDE'})
m_puntos_limpios_fijos['DIRECTIONS'] = m_puntos_limpios_fijos['NOMBRE-VIA'].astype(str) + ' '+ m_puntos_limpios_fijos['NUM'].astype(str)
#Ropa
m_ropa = m_ropa.rename(columns={'LATITUD': 'LATITUDE'})
m_ropa = m_ropa.rename(columns={'LONGITUD': 'LONGITUDE'})
m_ropa['LATITUDE'] = pd.to_numeric(m_ropa['LATITUDE'].str.replace(',', '.'))
m_ropa['LONGITUDE'] = pd.to_numeric(m_ropa['LONGITUDE'].str.replace(',', '.'))
m_ropa = m_ropa.rename(columns={'DIRECCION_COMPLETA': 'DIRECTIONS'})
#Resto
m_resto = m_resto.rename(columns={'LATITUD': 'LATITUDE'})
m_resto = m_resto.rename(columns={'LONGITUD': 'LONGITUDE'})
m_resto = m_resto.rename(columns={'DIRECCION': 'DIRECTIONS'})
#Envases
m_envases = m_envases.rename(columns={'LATITUD': 'LATITUDE'})
m_envases = m_envases.rename(columns={'LONGITUD': 'LONGITUDE'})
m_envases = m_envases.rename(columns={'DIRECCION': 'DIRECTIONS'})
#Papel
m_papel = m_papel.rename(columns={'LATITUD': 'LATITUDE'})
m_papel = m_papel.rename(columns={'LONGITUD': 'LONGITUDE'})
m_papel = m_papel.rename(columns={'DIRECCION': 'DIRECTIONS'})
#Vidrio
m_vidrio = m_vidrio.rename(columns={'LATITUD': 'LATITUDE'})
m_vidrio = m_vidrio.rename(columns={'LONGITUD': 'LONGITUDE'})
m_vidrio = m_vidrio.rename(columns={'DIRECCION': 'DIRECTIONS'})
#Organica
m_organica = m_organica.rename(columns={'LATITUD': 'LATITUDE'})
m_organica = m_organica.rename(columns={'LONGITUD': 'LONGITUDE'})
m_organica = m_organica.rename(columns={'DIRECCION': 'DIRECTIONS'})
#Pilas
m_pilas_marquesinas = m_pilas_marquesinas.rename(columns={'Latitud': 'LATITUDE'})
m_pilas_marquesinas = m_pilas_marquesinas.rename(columns={'Longitud': 'LONGITUDE'})
m_pilas_marquesinas = m_pilas_marquesinas.rename(columns={'Direccion_completa': 'DIRECTIONS'})
#Puntos limpios móviles
m_puntos_limpios_moviles = m_puntos_limpios_moviles.rename(columns={'LATITUD': 'LATITUDE'})
m_puntos_limpios_moviles = m_puntos_limpios_moviles.rename(columns={'LONGITUD': 'LONGITUDE'})
m_puntos_limpios_moviles = m_puntos_limpios_moviles.rename(columns={'DIRECCION_COMPLETA': 'DIRECTIONS'})
#Aceite
m_aceite = m_aceite.rename(columns={'LATITUD': 'LATITUDE'})
m_aceite = m_aceite.rename(columns={'LONGITUD': 'LONGITUDE'})
m_aceite = m_aceite.rename(columns={'DIRECCION COMPLETA': 'DIRECTIONS'})
m_aceite['LATITUDE'] = pd.to_numeric(m_aceite['LATITUDE'].str.replace(',', '.'))
m_aceite['LONGITUDE'] = pd.to_numeric(m_aceite['LONGITUDE'].str.replace(',', '.'))