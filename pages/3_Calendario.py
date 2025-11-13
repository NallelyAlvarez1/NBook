import streamlit as st
import pandas as pd
import plotly.express as px
from supabase_client import get_supabase_client 

supabase = get_supabase_client()

st.title("📅 Calendario de lectura")

libros = supabase.table("libros").select("nombre, estado_lectura, fecha_leido, fecha_inicio").execute().data or []

# Convertir a DataFrame
df = pd.DataFrame(libros)

if not df.empty:
    df["fecha"] = df["fecha_leido"].fillna(df["fecha_inicio"])
    df = df.dropna(subset=["fecha"])
    df["fecha"] = pd.to_datetime(df["fecha"])

    st.write("Libros marcados como 'leídos' o 'en progreso'")
    fig = px.timeline(df, x_start="fecha", x_end="fecha", y="nombre", color="estado_lectura")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aún no hay libros con fechas registradas.")
