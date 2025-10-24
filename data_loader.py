import pandas as pd
import streamlit as st

@st.cache_data
def load_data(path="df_streamlit.csv", for_stmap=False):
    """
    Carga y limpia el dataset base de incidentes.
    
    Parámetros:
        path (str): ruta del archivo CSV.
        for_stmap (bool): si True, renombra las columnas para usar con st.map().
    
    Retorna:
        pd.DataFrame: datos listos para visualización.
    """
    try:
        # 1️⃣ Leer el CSV
        df = pd.read_csv(path)
        st.info(f"Archivo cargado: {len(df)} registros totales.")
        
        # 2️⃣ Eliminar filas sin coordenadas válidas
        df = df.dropna(subset=["latitud", "longitud"])
        st.success(f"Datos limpios: {len(df)} registros con coordenadas válidas.")

        # 3️⃣ Si se usará con st.map(), crear columnas compatibles
        if for_stmap:
            df = df.rename(columns={"latitud": "latitude", "longitud": "longitude"})
            st.caption("🗺️ Columnas renombradas a 'latitude' y 'longitude' para st.map().")
        
        return df

    except Exception as e:
        st.error(f"Error al cargar el dataset: {e}")
        return pd.DataFrame()
