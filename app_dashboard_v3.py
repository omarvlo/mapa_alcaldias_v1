# ==========================================
# 🚨 Dashboard de Incidentes Delictivos – CDMX
# Versión 3.4 – Simplificada sin stqdm
# ==========================================

import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from data_loader import load_data
from map_utils import load_geojson, render_folium_map
from metro_utils import load_metro_stations, add_metro_icons
from geo_utils import calcular_incidentes_cercanos

# --- Configuración general ---
st.set_page_config(page_title="Dashboard CDMX", layout="wide")
st.title("🚨 Dashboard de Incidentes Delictivos – CDMX")

# === 1️⃣ Carga de datos y GeoJSON ===
url_geojson = (
    "https://datos.cdmx.gob.mx/dataset/7fcbad2f-2f25-4c65-a6f5-8fef98fdaa6e/"
    "resource/ca1766b2-60c4-4e4b-b888-38b7b9e8e67e/download/limite-de-las-alcaldias.json"
)
delegaciones = load_geojson(url_geojson)
df = load_data("df_streamlit.csv")
df_metro = load_metro_stations("metro_stations.csv")

# === 🔍 Verificación de estaciones cargadas ===
st.subheader("🚇 Estaciones del Metro cargadas")
st.info(f"Total de estaciones detectadas: **{len(df_metro)}**")
st.dataframe(df_metro.head(10))

# ==========================================
# 🎯 Filtrado de delitos cercanos al Metro
# ==========================================

st.subheader("🎯 Filtrando delitos cercanos a las estaciones del Metro")

RADIO_METROS = 300
R = 6371000  # radio medio de la Tierra (m)

# 🔹 Submuestreo temporal para pruebas (25%)
df = df.sample(frac=0.10, random_state=42)
st.caption(f"🧩 Procesando una muestra del 25 % del dataset: {len(df)} registros.")

# --- Cálculo vectorizado con barra de progreso ---
lat1 = np.radians(df["latitud"].values)
lon1 = np.radians(df["longitud"].values)
mask = np.zeros(len(df), dtype=bool)

progress_bar = st.progress(0)
total = len(df_metro)

for i, (_, est) in enumerate(df_metro.iterrows()):
    lat2, lon2 = np.radians([est["latitud"], est["longitud"]])
    dlat, dlon = lat1 - lat2, lon1 - lon2
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    dist = 2 * R * np.arcsin(np.sqrt(a))
    mask |= dist < RADIO_METROS

    # Actualizar barra de progreso
    progress_bar.progress((i + 1) / total)

progress_bar.empty()

df_filtrado = df[mask]
st.success(f"✅ {len(df_filtrado)} incidentes dentro de {RADIO_METROS} m de una estación del Metro.")

# === 4️⃣ Render del mapa ===
m = render_folium_map(df_filtrado, delegaciones, show_points=True, show_heatmap=True)
m = add_metro_icons(m, df_metro, icon_path="metro_icon.png", icon_size=(40, 40))
st_folium(m, width=800, height=600)

# ==========================================
# 📊 Reto: comparación de resultados
# ==========================================

st.subheader("📊 Reto: comparación de incidentes cercanos al Metro")

# --- Cálculo base (oficial) ---
df_ref = calcular_incidentes_cercanos(df, df_metro, radio=RADIO_METROS)
'''
st.download_button(
    "📥 Descargar resultados base (referencia oficial)",
    df_ref.to_csv(index=False).encode("utf-8"),
    "resultado_base.csv",
    "text/csv",
)
'''
# --- Carga y comparación ---
archivo_usuario = st.file_uploader("Sube tu archivo CSV", type=["csv"])
if archivo_usuario:
    try:
        df_user = pd.read_csv(archivo_usuario)
        if {"estacion", "delitos_cercanos"}.issubset(df_user.columns):
            df_cmp = pd.merge(df_ref, df_user, on="estacion", suffixes=("_real", "_usuario"))
            df_cmp["diferencia"] = abs(df_cmp["delitos_cercanos_real"] - df_cmp["delitos_cercanos_usuario"])
            similitud = np.clip(
                100 * (1 - df_cmp["diferencia"].sum() / df_cmp["delitos_cercanos_real"].sum()), 0, 100
            )

            st.metric("📈 Similitud general", f"{similitud:.2f}%")
            with st.expander("Ver comparación detallada"):
                st.dataframe(df_cmp)
        else:
            st.error("El CSV debe contener las columnas: 'estacion' y 'delitos_cercanos'.")
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.caption("📂 Esperando la carga del CSV del estudiante…")

st.markdown("---")
st.caption("© 2025 – Proyecto académico sobre datos abiertos CDMX. Elaborado con fines educativos.")
