import streamlit as st
import pandas as pd
import plotly.express as px
from supabase_client import get_supabase_client 

supabase = get_supabase_client()
st.set_page_config(page_title="NBooks", page_icon="📚", layout="wide")
# --- Redirección si no hay usuario ---
if "user" not in st.session_state:
    st.switch_page("pages/0_login.py")

st.title("📊 Estadísticas de lectura")

# Obtener datos
data = supabase.table("vista_libros").select("*").execute()
libros = data.data or []

if not libros:
    st.info("Aún no hay libros registrados.")
    st.stop()

df = pd.DataFrame(libros)

# --- Libros leídos por mes ---
df["fecha_leido"] = pd.to_datetime(df["fecha_leido"], errors="coerce")
leidos = df.dropna(subset=["fecha_leido"])
leidos["Mes"] = leidos["fecha_leido"].dt.to_period("M").astype(str)

st.subheader("📅 Libros leídos por mes")
if not leidos.empty:
    conteo_mes = leidos["Mes"].value_counts().sort_index()
    fig_mes = px.bar(
        conteo_mes,
        x=conteo_mes.index,
        y=conteo_mes.values,
        labels={"x": "Mes", "y": "Cantidad"},
        title="Libros leídos por mes",
    )
    st.plotly_chart(fig_mes, use_container_width=True)
else:
    st.write("Aún no hay libros marcados como leídos.")

# --- Libros por tipo ---
st.subheader("🏷️ Libros por tipo de novela")
if "tipos" in df.columns and df["tipos"].notna().any():
    tipos_list = df["tipos"].dropna().str.split(", ")
    tipos_exploded = tipos_list.explode()
    conteo_tipos = tipos_exploded.value_counts()
    fig_tipos = px.pie(
        values=conteo_tipos.values,
        names=conteo_tipos.index,
        title="Distribución por tipo de novela",
    )
    st.plotly_chart(fig_tipos, use_container_width=True)
else:
    st.write("Aún no hay tipos asignados a los libros.")

# --- Libros por estado ---
st.subheader("📖 Estado de lectura")
conteo_estado = df["estado_lectura"].value_counts()
fig_estado = px.bar(
    conteo_estado,
    x=conteo_estado.index,
    y=conteo_estado.values,
    title="Cantidad de libros por estado",
    labels={"x": "Estado", "y": "Cantidad"},
)
st.plotly_chart(fig_estado, use_container_width=True)
