import streamlit as st
from supabase_client import supabase

st.set_page_config(page_title="Inicio de Sesión", page_icon="📚", layout="centered")

st.title("📚 NBooks - Iniciar Sesión")

menu = ["Iniciar sesión", "Registrarse"]
choice = st.radio("Selecciona una opción:", menu)

email = st.text_input("Correo electrónico")
password = st.text_input("Contraseña", type="password")

if choice == "Iniciar sesión":
    if st.button("Entrar"):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user:
                st.session_state["user"] = user
                st.success("Inicio de sesión exitoso ✅")
                st.switch_page("main.py")
        except Exception as e:
            st.error(f"Error al iniciar sesión: {e}")

elif choice == "Registrarse":
    if st.button("Crear cuenta"):
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            st.success("Cuenta creada. Revisa tu correo para confirmar.")
        except Exception as e:
            st.error(f"Error al registrar: {e}")
