import streamlit as st
import datetime
import pandas as pd
from supabase_client import get_supabase_client 

supabase = get_supabase_client()

#================================== FUNCIONES ==================================

def create_autor(nombre_autor: str) -> dict:
    """Crea un nuevo autor en la base de datos."""
    if nombre_autor:
        try:
            result = supabase.table("autores").insert({"nombre": nombre_autor}).execute()
            st.success(f"Autor '{nombre_autor}' registrado.")
            return result.data[0]
        except Exception as e:
            st.error(f"Error al registrar autor: {e}")
            return None
    return None

def create_tipo(nombre_tipo: str) -> dict:
    """Crea un nuevo tipo de novela en la base de datos."""
    if nombre_tipo:
        try:
            result = supabase.table("tipos").insert({"nombre": nombre_tipo}).execute()
            st.success(f"Tipo '{nombre_tipo}' registrado.")
            return result.data[0]
        except Exception as e:
            st.error(f"Error al registrar tipo: {e}")
            return None
    return None

def _selector_entidad_libro(
    datos: list,
    label: str,
    key: str,
    btn_nuevo_label: str,
    modal_title: str,
    placeholder_nombre: str,
    funcion_creacion: callable,
    multiselect: bool = False
) -> any:
    opciones = [d["nombre"] for d in datos]
    nueva_entidad_creada = False

    # --- CASO 1: SELECTBOX (AUTOR) ---

    if not multiselect:
        opciones_select = ["-- Nuevo --"] + opciones
        seleccion_str = st.selectbox(label, opciones_select, key=f"{key}_selectbox")
        
        if seleccion_str == "-- Nuevo --":
            # 1. Definir una clave para el popover.
            popover_key = f"{key}_popover"
            
            with st.popover(btn_nuevo_label, use_container_width=True, key=popover_key): # << AÑADIR KEY AQUÍ
                st.subheader(modal_title)
                nombre_nuevo = st.text_input(placeholder_nombre, key=f"{key}_new_input_selectbox")
                
                # 2. Usar el estado de la sesión para controlar si se debe hacer el rerun
                # Esto es más estable que el retorno de None
                if f"{key}_rerun_flag" not in st.session_state:
                    st.session_state[f"{key}_rerun_flag"] = False

                if st.button(f"Guardar {modal_title.split()[-1]}", key=f"{key}_save_btn_selectbox"):
                    if nombre_nuevo:
                        entidad_creada = funcion_creacion(nombre_nuevo)
                        if entidad_creada:
                            # Establecer la bandera y usar el botón para cerrar el popover si es necesario.
                            st.session_state[f"{key}_rerun_flag"] = True
                            st.success("Guardado. Recargando...")
                        else:
                            st.warning("El nombre no puede estar vacío.")
                    else:
                        st.warning("El nombre no puede estar vacío.")
            
            # 3. Revisar la bandera fuera del popover y hacer el rerun.
            if st.session_state[f"{key}_rerun_flag"]:
                st.session_state[f"{key}_rerun_flag"] = False # Resetear la bandera
                st.rerun() 
                
        return seleccion_str
    # --- CASO 2: MULTISELECT (TIPOS DE NOVELA) ---
    else:
        # 1. Mostrar el multiselect (sin la opción "-- Nuevo --")
        seleccion = st.multiselect(label, opciones, key=f"{key}_multiselect")
        
        # 2. Mostrar el botón del popover inmediatamente debajo (comportamiento vertical)
        with st.popover(btn_nuevo_label, use_container_width=True):
            st.subheader(modal_title)
            nombre_nuevo = st.text_input(placeholder_nombre, key=f"{key}_new_input_multiselect")
            
            if st.button(f"Guardar {modal_title.split()[-1]}", key=f"{key}_save_btn_multiselect"):
                if nombre_nuevo:
                    entidad_creada = funcion_creacion(nombre_nuevo)
                    if entidad_creada:
                        nueva_entidad_creada = True
                        st.rerun() 
                else:
                    st.warning("El nombre no puede estar vacío.")

        return seleccion

st.set_page_config(layout="wide")
st.title("➕ Registrar nuevo libro")
st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
# --- Obtener datos (se mantiene igual) ---
autores_data = supabase.table("autores").select("*").execute().data or []
tipos_data = supabase.table("tipos").select("*").execute().data or []
libros_registrados_data = supabase.table("vista_libros").select("nombre, autor").execute().data or []

# --- Dividir la página en dos columnas principales ---
col_registro, col_tabla = st.columns([2, 1]) 

with col_registro:

    with st.container():
        nombre = st.text_input("Nombre del libro")
        
        # --- NUEVA ESTRUCTURA DE COLUMNAS PARA AUTOR Y TIPOS ---
        col_autor, col_tipos = st.columns(2) # Dos columnas de igual ancho (1:1)

        with col_autor:
            # --- Selector para Autor ---
            autor_seleccionado_nombre = _selector_entidad_libro(
                datos=autores_data,
                label="Autor",
                key="autor_libro",
                btn_nuevo_label="➕ Nuevo Autor",
                modal_title="Registrar Nuevo Autor",
                placeholder_nombre="Nombre del autor",
                funcion_creacion=create_autor
            )
        
        with col_tipos:
            # --- Selector para Tipos de Novela (Multiselect) ---
            tipos_seleccionados_nombres = _selector_entidad_libro(
                datos=tipos_data,
                label="Tipos de novela",
                key="tipos_novela_libro",
                btn_nuevo_label="➕ Nuevo Tipo",
                modal_title="Registrar Nuevo Tipo de Novela",
                placeholder_nombre="Nombre del tipo",
                funcion_creacion=create_tipo,
                multiselect=True # ¡Importante para que funcione como multiselect!
            )
        # --- FIN DE LA ESTRUCTURA DE COLUMNAS ---
        
        # El resto del formulario se mantiene debajo de las columnas
        col1, col2=st.columns([1,1])
        with col1:
            estado = st.selectbox("Estado de lectura", ["por leer", "en proceso", "ya leído", "no leído", "dejado"])
        with col2:
            st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
            en_kindle = st.checkbox("¿Lo tengo en Mi Kindle?")

        portada = st.file_uploader("Subir portada", type=["jpg", "png", "jpeg"])
        
    if st.button("Registrar libro", use_container_width=True):
        if not nombre:
            st.warning("El nombre es obligatorio.")
        elif not autor_seleccionado_nombre: # Validar que se seleccionó o creó un autor
            st.warning("Debe seleccionar o registrar un autor.")
        elif not tipos_seleccionados_nombres: # Validar que se seleccionó o creó al menos un tipo
            st.warning("Debe seleccionar o registrar al menos un tipo de novela.")
        else:
            # --- Lógica de Inserción ---
            
            # Obtener el autor_id
            autor_id = next((a["id"] for a in autores_data if a["nombre"] == autor_seleccionado_nombre), None)
            
            # Subir portada (se mantiene igual)
            portada_path = None
            if portada:
                file_name = f"{nombre.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                portada_path = file_name
                try:
                    supabase.storage.from_("portadas_libros").upload(file_name, portada.read())
                except Exception as e:
                    st.error(f"Error al subir portada: {e}")
                    portada_path = None

            # Insertar libro
            libro_insert = supabase.table("libros").insert({
                "nombre": nombre,
                "autor_id": autor_id,
                "portada_path": portada_path,
                "estado_lectura": estado,
                "en_kindle": en_kindle,
            }).execute()

            libro_id = libro_insert.data[0]["id"]

            # Vincular tipos
            # Recargar tipos_data por si se creó uno nuevo en otro lado
            tipos_data_actualizados_para_vinculacion = supabase.table("tipos").select("*").execute().data or []
            
            for tipo_nombre in tipos_seleccionados_nombres:
                tipo = next((t for t in tipos_data_actualizados_para_vinculacion if t["nombre"] == tipo_nombre), None)
                if tipo:
                    supabase.table("libro_tipos").insert({"libro_id": libro_id, "tipo_id": tipo["id"]}).execute()

            st.success("Libro registrado exitosamente ✅")
            st.balloons()
            st.rerun() 

# ==============================================================================
#                      COLUMNA DERECHA: TABLA DE LIBROS (Se mantiene igual)
# ==============================================================================
with col_tabla:
    st.header("Libros Registrados")

    if libros_registrados_data:
        df = pd.DataFrame(libros_registrados_data)
        df = df.rename(columns={"nombre": "Título del Libro", "autor": "Autor"})

        st.dataframe(
            df, 
            use_container_width=True, 
            column_order=("Título del Libro", "Autor"),
            hide_index=True 
        )
    else:
        st.info("Aún no hay libros registrados.")