import streamlit as st
from supabase_client import get_supabase_client 

# 2. Llama a la función para obtener el cliente
supabase = get_supabase_client()

st.set_page_config(page_title="NBooks", page_icon="📚", layout="wide")

# --- Redirección si no hay usuario ---
if "user" not in st.session_state:
    st.switch_page("pages/0_login.py")

col1, col2 = st.columns([5,1])
with col1:
    st.title("📚 Bienvenido a NBooks")
with col2:
    st.markdown("")
    if st.button("Cerrar sesión"):
        st.session_state.pop("user", None)
        st.switch_page("pages/0_login.py")

st.markdown("Explora tus libros registrados y gestiona su progreso de lectura.")

#================== FUNCIONES =========================
def obtener_badge_estado(estado):
    estado_limpio = estado.strip()
    
    # Mapeo de estado a color y ícono (usando los íconos de Material Design):
    color_map = {
        "leído": ("green", "check_circle"),
        "por leer": ("blue", "bookmark_add"),
        "en proceso": ("orange", "hourglass_top"),
        "no leído": ("gray", "visibility_off"),
        "abandonado": ("red", "cancel"),
    }
    
    color, icon = color_map.get(estado_limpio.lower(), ("gray", "help"))
    return f":{color}-badge[:material/{icon}: {estado_limpio}]"

def actualizar_estado(libro_id, nuevo_estado):
    """Actualiza el estado de lectura de un libro y refresca la página."""
    if nuevo_estado:
        supabase.table("libros").update({"estado_lectura": nuevo_estado}).eq("id", libro_id).execute()
        st.success(f"Estado actualizado.")
        st.rerun()

#================ FILTROS Y LIBROS ====================
# --- Cargar libros ---
data = supabase.table("vista_libros").select("*").execute()
libros = data.data or []

# --- Función auxiliar para obtener tipos únicos ---
def get_unique_types(libros):
    """Extrae todos los tipos únicos de la lista de libros."""
    tipos_unicos = set()
    for libro in libros:
        tipos_str = libro["tipos"]
        if tipos_str:
            # Dividir la cadena por coma y añadir cada tipo único al set
            for tipo in tipos_str.split(','):
                tipo_limpio = tipo.strip()
                if tipo_limpio:
                    tipos_unicos.add(tipo_limpio)
    
    # Devolvemos una lista, asegurando que "Todos" sea la primera opción
    return ["Todos"] + sorted(list(tipos_unicos))

# Obtener la lista de tipos únicos una sola vez al cargar la app
tipos_disponibles = get_unique_types(libros)

# --- Filtros ---
col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1.5]) # Añadimos una columna para la búsqueda general

# 1. Campo de Búsqueda General
busqueda_filtro = col1.text_input("🔍 Buscar (Título/Autor/Tipo)")

# 2. Filtro por Tipo (Selectbox)
tipo_filtro = col2.selectbox(
    "🏷️ Tipo",
    tipos_disponibles 
)

# 3. Filtro por Autor (manteniendo el text_input para búsquedas parciales)
autor_filtro = col3.text_input("👤 Autor")

# 4. Filtro por Estado (Selectbox)
estado_filtro = col4.selectbox(
    "📖 Estado",
    ["Todos", "Leído", "Por leer", "En proceso", "No leído", "Abandonado"]
)


# --- Aplicar filtros ---
libros_filtrados = []
busqueda_lower = busqueda_filtro.lower()

for libro in libros:
    # 1. Filtro de Búsqueda General (Título o Autor o Tipos)
    texto_libro = f"{libro.get('nombre', '')} {libro.get('autor', '')} {libro.get('tipos', '')}".lower()
    match_busqueda = busqueda_lower in texto_libro
    
    # 2. Filtro por Autor
    match_autor = autor_filtro.lower() in (libro.get("autor") or "").lower()
    
    # 3. Filtro por Tipo (Selectbox)
    tipos_del_libro = (libro.get("tipos") or "").lower()
    match_tipo = (
        tipo_filtro == "Todos" 
        or tipo_filtro.lower() in tipos_del_libro # Verifica si el tipo seleccionado está en los tipos del libro
    )
    
    # 4. Filtro por Estado
    match_estado = (
        estado_filtro == "Todos" 
        or libro["estado_lectura"] == estado_filtro
    )
    
    # Combinar todos los filtros
    if match_busqueda and match_autor and match_tipo and match_estado:
        libros_filtrados.append(libro)
        
st.divider()

# --- Mostrar libros en filas de 3 ---
if not libros_filtrados:
    st.info("No hay libros que coincidan con los filtros.")
else:
    for i in range(0, len(libros_filtrados), 4):
        cols = st.columns(4)
        for j, col in enumerate(cols):
            if i + j < len(libros_filtrados):
                libro = libros_filtrados[i + j]
                libro_id = libro['id'] # Obtener el ID para las claves y la actualización

                with col.container(border=True):
                    # Usamos columnas internas para la portada y los datos
                    portada_col, datos_col = st.columns([1, 2]) 

                    # --- Columna de la Portada ---
                    with portada_col:
                        portada_url = (
                            f"https://osanryewvmaofxtfnzqk.supabase.co/storage/v1/object/public/"
                            f"portadas_libros/{libro['portada_path']}"
                        ) if libro["portada_path"] else "https://placehold.co/100x150?text=Sin+portada"
                        # Usamos HTML para aplicar un ancho y alto fijo.
                        # object-fit: cover asegura que la imagen cubra el área sin distorsionarse si su proporción es diferente.
                        st.markdown(
                            f"""
                            <img src="{portada_url}" 
                                style="width: 150px; height: 140px; object-fit: cover;" 
                                alt="Portada del libro">
                            """, 
                            unsafe_allow_html=True
                        ) 

                    # --- Columna de Datos Simplificados (Panel Principal) ---
                    with datos_col:
                        # Título del libro (Agrandado con H3)
                        st.markdown(
                            f"""
                            <p style='
                                margin: 0 0 3px 0; /* Margen de 5px debajo de la línea */
                                padding-bottom: 1px; /* Pequeño espacio entre el texto y la línea */
                                font-size: 28px; 
                                text-align: center; 
                                line-height: 1; 
                                border-bottom: 1px solid #F0F0F0; /* Línea gris muy delgada */
                            '>
                                <b>{libro['nombre'] or 'Título Desconocido'}</b>
                            </p>
                            <p style='
                                margin: 0 0 6px 0; 
                                padding: 0; 
                                font-size: 20px; 
                                text-align: center; 
                                line-height: 1;
                            '>
                                {libro['autor'] or 'Desconocido'}
                            </p>
                            """,
                            unsafe_allow_html=True
                        )

                        # Datos ultra compactos (Solo nombre, autor, tipo, estado y kindle)

                        tipos_cadena = libro['tipos'] or ""
                        tipos_lista = [t.strip() for t in tipos_cadena.split(',') if t.strip()]
                        tipos_badges_markdown = ""
                        if tipos_lista:
                            tipos_badges_markdown = " ".join([f":violet-badge[:material/star: {tipo}]" for tipo in tipos_lista])
                        else:
                            tipos_badges_markdown = ":gray-badge[-]"

                        badge_estado = obtener_badge_estado(libro['estado_lectura'])

                        st.markdown(tipos_badges_markdown)
                        estado_col, kindle_col = st.columns([3, 2])

                        with estado_col:
                            st.markdown(badge_estado)

                        with kindle_col:
                            st.markdown(
                                f"""
                                <p style='padding: 0; line-height: 1; font-size: 14px; text-align: center;'>
                                    Kindle {'✅' if libro['en_kindle'] else '❌'}
                                </p>
                                """,
                                unsafe_allow_html=True,
                            )

                    # --- Modal (Pop-up) para Ver Detalles y Cambiar Estado ---
                    with st.popover("Ver Detalles", use_container_width=True):

                        #st.header(libro['nombre'])

                        pop_col1, pop_col2 = st.columns([3, 1]) 
                        

                        with pop_col1:
                            # Título del libro (Agrandado con H3)
                            st.markdown(
                                f"""
                                <p style='
                                    margin: 0 0 3px 0; /* Margen de 5px debajo de la línea */
                                    padding-bottom: 1px; /* Pequeño espacio entre el texto y la línea */
                                    font-size: 28px; 
                                    text-align: center; 
                                    line-height: 1; 
                                    border-bottom: 1px solid #F0F0F0; /* Línea gris muy delgada */
                                '>
                                    <b>{libro['nombre'] or 'Título Desconocido'}</b>
                                </p>
                                <p style='
                                    margin: 0 0 6px 0; 
                                    padding: 0; 
                                    font-size: 20px; 
                                    text-align: center; 
                                    line-height: 1;
                                '>
                                    {libro['autor'] or 'Desconocido'}
                                </p>
                                """,
                                unsafe_allow_html=True
                            )

                            tipos_cadena = libro['tipos'] or ""
                            tipos_lista = [t.strip() for t in tipos_cadena.split(',') if t.strip()]
                            tipos_badges_markdown = ""
                            if tipos_lista:
                                tipos_badges_markdown = " ".join([f":violet-badge[:material/star: {tipo}]" for tipo in tipos_lista])
                            else:
                                tipos_badges_markdown = ":gray-badge[-]"

                            badge_estado = obtener_badge_estado(libro['estado_lectura'])

                            st.markdown(tipos_badges_markdown)
                            estado_col, kindle_col, espacio_blanco = st.columns([1, 1, 3])

                            with estado_col:
                                st.markdown(badge_estado)

                            with kindle_col:
                                st.markdown(
                                    f"""
                                    <p style='margin-top: 6px; padding: 0; line-height: 1; font-size: 14px; text-align: left;'>
                                        Kindle {'✅' if libro['en_kindle'] else '❌'}
                                    </p>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            with espacio_blanco:
                                st.markdown("")

                            st.write(libro.get('descripcion', 'No hay descripción disponible.')) 
                            
                        # --- Columna 2: Portada Grande (Derecha) ---
                        with pop_col2:
                            # La URL de la portada ya debe estar definida arriba
                            #st.image(portada_url, width=700)
                            st.markdown(
                                f"""
                                <img src="{portada_url}" 
                                    style="width: 410px; height: 210px; object-fit: cover; border-radius: 10px;" 
                                    alt="Portada del libro">
                                """, 
                                unsafe_allow_html=True
                            ) 
                            nuevo_estado = st.selectbox(
                                    "Cambiar estado", 
                                ["Leído", "Por leer", "En proceso", "No leído", "Abandonado"],
                                index=[
                                    "Leído", "Por leer", "En proceso", "No leído", "Abandonado"
                                ].index(libro["estado_lectura"]),
                                key=f"popover_estado_{libro_id}",
                                # 2. Agrega este parámetro para ocultar la etiqueta y su espacio.
                                label_visibility="collapsed" 
                            )
                            
                            if st.button("Guardar Estado", key=f"btn_guardar_{libro_id}"):
                                # Llama a la función de actualización si el estado cambió
                                if nuevo_estado != libro["estado_lectura"]:
                                    actualizar_estado(libro_id, nuevo_estado)
                                else:
                                    st.info("El estado no ha cambiado.")
                            

                        