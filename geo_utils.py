import pandas as pd
from geopy.distance import geodesic
import streamlit as st

@st.cache_data
def calcular_incidentes_cercanos(df_incidentes, df_metro, radio=300):
    """
    Calcula el número de incidentes cercanos a cada estación del Metro
    dentro de un radio determinado (en metros).

    Parámetros:
        df_incidentes (pd.DataFrame): Datos con columnas ['latitud', 'longitud'].
        df_metro (pd.DataFrame): Estaciones del metro con ['estacion', 'latitud', 'longitud'].
        radio (float): Radio de búsqueda en metros.

    Retorna:
        pd.DataFrame con columnas ['estacion', 'delitos_cercanos'].
    """
    conteos = []
    try:
        for _, est in df_metro.iterrows():
            lat_m, lon_m = est["latitud"], est["longitud"]
            conteo = sum(
                geodesic((row["latitud"], row["longitud"]), (lat_m, lon_m)).meters < radio
                for _, row in df_incidentes.iterrows()
            )
            conteos.append({"estacion": est["estacion"], "delitos_cercanos": conteo})
        st.success(f"Cálculo completado: {len(conteos)} estaciones procesadas.")
    except Exception as e:
        st.error(f"Error en el cálculo geodésico: {e}")
        return pd.DataFrame()
    return pd.DataFrame(conteos)
