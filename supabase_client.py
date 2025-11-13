import streamlit as st
from supabase import create_client, Client

def initialize_supabase_client(secrets: dict) -> Client:
    try:
        SUPABASE_URL = secrets["supabase"]["url"]
        SUPABASE_KEY = secrets["supabase"]["key"]
    except KeyError as e:
        # Esto nos asegura que si falla la importación es por el secreto
        st.error("Error de configuración: Falta la clave de Supabase.") 
        st.stop()
        
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔑 Definimos la función de acceso con caché aquí para que todos la usen.
@st.cache_resource 
def get_supabase_client() -> Client:
    """Devuelve la instancia del cliente Supabase, cacheada globalmente."""
    return initialize_supabase_client(st.secrets)

# No se define ninguna variable global 'supabase' aquí.