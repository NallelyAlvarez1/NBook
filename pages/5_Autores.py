import streamlit as st
from supabase_client import get_supabase_client 

supabase = get_supabase_client()

st.title("👩‍💼 Autores registrados")

autores = supabase.table("autores").select("*").order("nombre").execute().data or []

for autor in autores:
    st.write("📖", autor["nombre"])

st.divider()
nuevo = st.text_input("Agregar nuevo autor")
if st.button("Agregar"):
    if nuevo:
        supabase.table("autores").insert({"nombre": nuevo}).execute()
        st.success(f"Autor '{nuevo}' agregado.")
        st.rerun()
    else:
        st.warning("Debe ingresar un nombre.")
