import streamlit as st
import datetime
import pandas as pd
from supabase_client import get_supabase_client 

supabase = get_supabase_client()
st.set_page_config(page_title="Editar", page_icon="📚", layout="wide")
# --- Redirección si no hay usuario ---
if "user" not in st.session_state:
    st.switch_page("pages/0_login.py")

#================== FUNCIONES AUXILIARES =========================
# Las funciones de creación y el selector de entidades se mantienen igual.
# Asumo que tienes estas funciones definidas o importadas.

def create_autor(nombre_autor: str) -> dict:
    # ... (código de tu función create_autor) ...
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
    # ... (código de tu función create_tipo) ...
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
    multiselect: bool = False,
    default_value: any = None
) -> any:
    """Función selector de entidades con soporte para valor inicial."""
    opciones = [d["nombre"] for d in datos]
    nueva_entidad_creada = False

    # --- CASO 1: SELECTBOX (AUTOR) ---
    if not multiselect:
        opciones_select = ["-- Nuevo --"] + opciones
        
        default_index = 0
        if default_value and default_value in opciones_select:
            default_index = opciones_select.index(default_value)

        seleccion_str = st.selectbox(
            label, 
            opciones_select, 
            key=f"{key}_selectbox",
            index=default_index
        )
        
        if seleccion_str == "-- Nuevo --":
            with st.popover(btn_nuevo_label, use_container_width=True):
                st.subheader(modal_title)
                nombre_nuevo = st.text_input(placeholder_nombre, key=f"{key}_new_input_selectbox")
                if st.button(f"Guardar {modal_title.split()[-1]}", key=f"{key}_save_btn_selectbox"):
                    if nombre_nuevo:
                        entidad_creada = funcion_creacion(nombre_nuevo)
                        if entidad_creada:
                            nueva_entidad_creada = True
                            st.rerun() 
                    else:
                        st.warning("El nombre no puede estar vacío.")
            return None if nueva_entidad_creada else seleccion_str
        return seleccion_str

    # --- CASO 2: MULTISELECT (TIPOS DE NOVELA) ---
    else:
        initial_value = default_value if isinstance(default_value, list) else []
        
        seleccion = st.multiselect(
            label, 
            opciones, 
            default=initial_value,
            key=f"{key}_multiselect"
        )
        
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

#================== INICIO DE PÁGINA DE EDICIÓN =========================

st.set_page_config(layout="wide") 
st.title("✏️ Editar Libro")

# --- 1. Cargar todos los datos necesarios ---
try:
    # Cargar todos los libros para el selector (incluyendo las nuevas columnas)
    libros_all_data = supabase.table("vista_libros").select(
        "*, fecha_inicio, fecha_leido, descripcion" 
    ).order("nombre").execute().data or []

    # Cargar datos para selectores de Autor y Tipos
    autores_data = supabase.table("autores").select("*").execute().data or []
    tipos_data = supabase.table("tipos").select("*").execute().data or []

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.stop()

# --- 2. Selector del Libro a Editar ---
st.subheader("Selecciona el libro a editar")
if not libros_all_data:
    st.info("No hay libros registrados para editar.")
    st.stop()

# Usar un selectbox para elegir el libro por nombre
libro_nombres = ["-- Seleccionar un libro --"] + [l['nombre'] for l in libros_all_data]
nombre_seleccionado = st.selectbox(
    "Libro a editar", 
    libro_nombres, 
    key="libro_a_editar_selector",
    index=0 # Por defecto, selecciona el placeholder
)

libro_actual = None
libro_id = None
if nombre_seleccionado != "-- Seleccionar un libro --":
    # Buscar el objeto libro completo
    libro_actual = next((l for l in libros_all_data if l['nombre'] == nombre_seleccionado), None)
    if libro_actual:
        libro_id = libro_actual['id']

st.divider()

# --- 3. Formulario de Edición Condicional ---

if libro_actual and libro_id:
    st.markdown(f"## Editando: **{libro_actual['nombre']}**")
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True) 

    col_form_left, col_form_right = st.columns([1, 1])

    # Función auxiliar para parsear fechas
    def parse_date(date_str):
        if date_str:
            try:
                return datetime.datetime.strptime(str(date_str), '%Y-%m-%d').date()
            except:
                return None
        return None

    with col_form_left:
        st.subheader("Datos Principales")
        
        # Nombre del libro
        nombre_libro = st.text_input("Nombre del libro", value=libro_actual.get('nombre', ''), key=f"edit_nombre_{libro_id}")
        
        col_autor, col_tipos = st.columns(2)

        with col_autor:
            autor_seleccionado_nombre = _selector_entidad_libro(
                datos=autores_data,
                label="Autor",
                key=f"edit_autor_libro_{libro_id}",
                btn_nuevo_label="➕ Nuevo Autor",
                modal_title="Registrar Nuevo Autor",
                placeholder_nombre="Nombre del autor",
                funcion_creacion=create_autor,
                default_value=libro_actual.get('autor', None)
            )
        
        with col_tipos:
            # Corrección: Agregamos 'or '' ' para asegurar que siempre haya una cadena de texto
            tipos_actuales_lista = [t.strip() for t in (libro_actual.get('tipos') or '').split(',') if t.strip()]
            tipos_seleccionados_nombres = _selector_entidad_libro(
                datos=tipos_data,
                label="Tipos de novela",
                key=f"edit_tipos_novela_libro_{libro_id}",
                btn_nuevo_label="➕ Nuevo Tipo",
                modal_title="Registrar Nuevo Tipo de Novela",
                placeholder_nombre="Nombre del tipo",
                funcion_creacion=create_tipo,
                multiselect=True,
                default_value=tipos_actuales_lista
            )
        
        # Estado de lectura (Asegúrate de que 'ya leído' esté en la lista)
        estados_opciones = ["Por leer", "En proceso", "Leído", "No leído", "Abandonado"]
        estado_lectura = st.selectbox(
            "Estado de lectura", 
            estados_opciones,
            index=estados_opciones.index(libro_actual.get('estado_lectura', 'Por leer')),
            key=f"edit_estado_{libro_id}"
        )

        # En Kindle
        en_kindle = st.checkbox("¿Lo tengo en Kindle?", value=libro_actual.get('en_kindle', False), key="edit_kindle")

        # Descripción (Columna: descripcion)
        descripcion = st.text_area(
            "Descripción del libro", 
            value=libro_actual.get('descripcion', ''), 
            height=150, 
            key=f"edit_descripcion_{libro_id}"
        )

    with col_form_right:
        st.subheader("Fechas y Portada")

        # Fecha de inicio de lectura (Columna: fecha_inicio)
        fecha_inicio_lectura = st.date_input(
            "Fecha de inicio de lectura", 
            value=parse_date(libro_actual.get('fecha_inicio')),
            key=f"edit_fecha_inicio_{libro_id}",
            min_value=datetime.date(1900, 1, 1), 
            max_value=datetime.date.today()
        )

        # Fecha de fin de lectura (Columna: fecha_leido)
        fecha_fin_lectura = st.date_input(
            "Fecha de fin de lectura (Leído)", 
            value=parse_date(libro_actual.get('fecha_leido')),
            key=f"edit_fecha_fin_{libro_id}",
            min_value=datetime.date(1900, 1, 1), 
            max_value=datetime.date.today()
        )

        st.markdown("---")
        st.markdown("### Portada")

        portada_url_base = "https://osanryewvmaofxtfnzqk.supabase.co/storage/v1/object/public/portadas_libros"
        portada_url_actual = (
            f"{portada_url_base}/{libro_actual['portada_path']}"
        ) if libro_actual["portada_path"] else "https://placehold.co/200x300?text=Sin+portada"
        
        st.image(portada_url_actual, width=200, caption="Portada actual")

        nueva_portada = st.file_uploader("Cambiar portada", type=["jpg", "png", "jpeg"], key="edit_portada_uploader_{libro_id}")
        mantener_portada = st.checkbox("Mantener portada actual", value=True, key="edit_mantener_portada_{libro_id}")

    st.markdown("---")
    
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("Guardar Cambios", use_container_width=True, key="btn_guardar_cambios_libro"):
            if not nombre_libro or not autor_seleccionado_nombre or not tipos_seleccionados_nombres:
                st.warning("El nombre, autor y tipo son obligatorios.")
            else:
                # --- Lógica de Actualización de Datos y Portada ---
                
                autor_id = next((a["id"] for a in autores_data if a["nombre"] == autor_seleccionado_nombre), None)
                portada_path_final = libro_actual['portada_path']
                
                # [OMITIDO: Lógica de manejo de portada (subida y eliminación) para mantener concisión, 
                # utiliza la lógica que ya tienes de los pensamientos anteriores]
                
                # Actualizar libro en la tabla 'libros'
                update_data = {
                    "nombre": nombre_libro,
                    "autor_id": autor_id,
                    "portada_path": portada_path_final, # Asumiendo que esta variable se actualiza con la lógica omitida
                    "estado_lectura": estado_lectura,
                    "en_kindle": en_kindle,
                    "descripcion": descripcion,
                    "fecha_inicio": fecha_inicio_lectura.isoformat() if fecha_inicio_lectura else None,
                    "fecha_leido": fecha_fin_lectura.isoformat() if fecha_fin_lectura else None,
                }
                
                supabase.table("libros").update(update_data).eq("id", libro_id).execute()

                # Actualizar los tipos de novela (borrar y añadir)
                supabase.table("libro_tipos").delete().eq("libro_id", libro_id).execute()
                
                if tipos_seleccionados_nombres:
                    tipos_data_actualizados_para_vinculacion = supabase.table("tipos").select("*").execute().data or []
                    for tipo_nombre in tipos_seleccionados_nombres:
                        tipo = next((t for t in tipos_data_actualizados_para_vinculacion if t["nombre"] == tipo_nombre), None)
                        if tipo:
                            supabase.table("libro_tipos").insert({"libro_id": libro_id, "tipo_id": tipo["id"]}).execute()

                st.success("Libro actualizado exitosamente ✅")
                st.balloons()
                st.switch_page("main.py") # Vuelve a la página principal

    with col_cancel:
        if st.button("Cancelar", use_container_width=True, key="btn_cancelar_edicion"):
            st.switch_page("main.py") # Vuelve a la página principal

else:
    st.info("Por favor, selecciona un libro de la lista desplegable para cargar el formulario de edición.")