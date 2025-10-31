import pandas as pd
import folium
from folium.features import CustomIcon
import streamlit as st

#import os
#st.write("Ruta actual:", os.getcwd())
#st.write("¿Existe el ícono?", os.path.exists(icon_path))

@st.cache_data
def load_metro_stations(path="metro_stations.csv"):
    """
    Carga las coordenadas de estaciones del Metro de la CDMX desde un archivo CSV.
    
    Parámetros:
        path (str): ruta del archivo CSV con columnas ['estacion', 'linea', 'latitud', 'longitud'].
    
    Retorna:
        pd.DataFrame: dataframe con estaciones y coordenadas.
    """
    try:
        df_metro = pd.read_csv(path)
        st.success(f"✅ {len(df_metro)} estaciones del Metro cargadas correctamente.")
        return df_metro
    except Exception as e:
        st.error(f"❌ Error al cargar las estaciones del Metro: {e}")
        return pd.DataFrame()


def add_metro_icons(
    m,
    df_metro,
    icon_path="metro_icon.png",
    icon_size=(40, 40),
    estaciones_seleccionadas=None
):
    """
    Agrega íconos del Metro al mapa con tooltip (nombre visible al pasar el cursor)
    y popup (detalle visible al hacer clic).
    """
    if df_metro.empty:
        st.warning("⚠️ No se cargaron estaciones del Metro.")
        return m

    # Si se pasan estaciones específicas, filtrarlas
    if estaciones_seleccionadas:
        df_metro = df_metro[df_metro["estacion"].isin(estaciones_seleccionadas)]

    try:
        icon = CustomIcon(icon_path, icon_size=icon_size)
        for _, row in df_metro.iterrows():
            nombre_estacion = row["estacion"]
            linea = row.get("linea", "N/A")

            folium.Marker(
                location=[row["latitud"], row["longitud"]],
                popup=folium.Popup(f"<b>🚇 {nombre_estacion}</b><br>Línea {linea}", max_width=200),
                tooltip=f"{nombre_estacion} – Línea {linea}",
                icon=icon
            ).add_to(m)
        st.caption("📍 Íconos del Metro agregados con tooltip interactivo.")
    except Exception as e:
        st.warning(f"Error al agregar íconos del Metro: {e}")

    return m