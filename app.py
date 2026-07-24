# pyrefly: ignore [missing-import]
import streamlit as st
import requests
from datetime import datetime
import urllib.parse

# ========================================================
# CONFIGURACIÓN DE PÁGINA
# ========================================================
st.set_page_config(
    page_title="Chat de Proyecto",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbw_7gj4gU5WTruy0HqYs7RUgj75aD4rpj5g3osX_NGg31uF58QhaUls8W6PE_YaX1gE1w/exec"

# ========================================================
# DISEÑO UI/UX (CSS PERSONALIZADO)
# ========================================================
def inject_custom_css():
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            css_content = f.read()
    except FileNotFoundError:
        css_content = ""

    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# ========================================================
# GESTIÓN DE ESTADO
# ========================================================
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'session_email' not in st.session_state:
        st.session_state.session_email = ""
    if 'session_nombre' not in st.session_state:
        st.session_state.session_nombre = ""
    if 'session_area' not in st.session_state:
        st.session_state.session_area = ""
    if 'current_project' not in st.session_state:
        st.session_state.current_project = ""
    if 'sidebar_tab' not in st.session_state:
        st.session_state.sidebar_tab = "mensajes"
    if 'auto_login_error' not in st.session_state:
        st.session_state.auto_login_error = ""

# ========================================================
# FUNCIONES API & UTILIDADES URL
# ========================================================
def api_login(email, clave):
    try:
        res = requests.get(WEBHOOK_URL, params={"action": "login", "email": email, "clave": clave}, timeout=10)
        return res.json()
    except Exception:
        return {"success": False, "message": "Error de conexión con el servidor."}
    
def api_auto_login(email):
    try:
        res = requests.get(WEBHOOK_URL, params={"action": "auto_login", "email": email}, timeout=10)
        return res.json()
    except Exception as e:
        return {"success": False, "message": f"Error de conexión API: {str(e)}"}

def get_url_param(param_name):
    """Obtiene un parámetro de la URL de forma compatible."""
    try:
        if hasattr(st, "query_params"):
            val = st.query_params.get(param_name)
            if isinstance(val, list):
                return val[0] if val else None
            return val
        elif hasattr(st, "experimental_get_query_params"):
            params = st.experimental_get_query_params()
            val = params.get(param_name)
            if isinstance(val, list):
                return val[0] if val else None
            return val
    except Exception:
        pass
    return None

def process_url_auto_login():
    """Ejecuta la autenticación desde la URL antes de renderizar la app."""
    if not st.session_state.logged_in:
        email_param = get_url_param("email")
        if email_param:
            with st.spinner(f"Verificando credenciales para {email_param}..."):
                data = api_auto_login(email_param)
                if data.get("success"):
                    st.session_state.logged_in = True
                    st.session_state.session_email = email_param
                    st.session_state.session_nombre = data.get("nombre", "Usuario")
                    st.session_state.session_area = data.get("area", "")
                    st.session_state.auto_login_error = ""
                    
                    # Cargar proyecto si viene especificado
                    proyecto_param = get_url_param("proyecto")
                    if proyecto_param:
                        st.session_state.current_project = proyecto_param
                        st.session_state.sidebar_tab = "mensajes"
                    
                    st.rerun()
                else:
                    msg = data.get('message', 'Usuario no registrado')
                    st.session_state.auto_login_error = f"⚠️ Auto-login falló para '{email_param}': {msg}"

@st.cache_data(ttl=300, show_spinner=False)
def api_get_projects(area):
    try:
        res = requests.get(WEBHOOK_URL, params={"action": "get_projects", "area": area}, timeout=10)
        data = res.json()
        return data.get("projects", [])
    except Exception:
        return []

@st.cache_data(ttl=10, show_spinner=False)
def api_get_chat(project_id):
    try:
        res = requests.get(WEBHOOK_URL, params={"action": "get_chat", "id_proyecto": project_id}, timeout=10)
        data = res.json()
        return data.get("messages", [])
    except Exception:
        return []

def api_post_message(payload):
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception:
        pass

@st.cache_data(ttl=3600, show_spinner=False)
def api_get_users():
    try:
        res = requests.get(WEBHOOK_URL, params={"action": "get_users"}, timeout=10)
        data = res.json()
        return data.get("users", [])
    except Exception:
        return []

# ========================================================
# PANTALLA 1: LOGIN
# ========================================================
def show_login():
    if st.session_state.auto_login_error:
        st.error(st.session_state.auto_login_error)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        sub_c1, sub_c2, sub_c3 = st.columns([1, 1.5, 1])
        with sub_c2:
            st.image("assets/Logo_Ingeap1.png", use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #333333; margin-top:0;'>Inicio de Sesión</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888888; font-size:14px;'>Ingresa tus credenciales corporativas</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        email = st.text_input("Email", placeholder="tu@email.com")
        clave = st.text_input("Clave", type="password", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Ingresar", type="primary", use_container_width=True):
            if not email or not clave:
                st.error("Completar todos los campos")
            else:
                with st.spinner("Verificando..."):
                    data = api_login(email, clave)
                    if data.get("success"):
                        st.session_state.logged_in = True
                        st.session_state.session_email = email
                        st.session_state.session_nombre = data.get("nombre")
                        st.session_state.session_area = data.get("area")
                        st.session_state.auto_login_error = ""
                        st.rerun()
                    else:
                        st.error(data.get("message", "Error de credenciales"))

# ========================================================
# PANTALLA 2: SELECCIÓN DE PROYECTO
# ========================================================
def show_project_selection():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        sub_c1, sub_c2, sub_c3 = st.columns([1, 1.5, 1])
        with sub_c2:
            st.image("assets/Logo_Ingeap1.png", use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #333333; margin-top:0;'>Selección de Proyecto</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        areas_base = ["I", "M", "A", "S"]
        if st.session_state.session_area not in areas_base and st.session_state.session_area:
            areas_base.append(st.session_state.session_area)
            
        idx_area = areas_base.index(st.session_state.session_area) if st.session_state.session_area in areas_base else 0
        selected_area = st.selectbox("Filtrar por Área:", options=areas_base, index=idx_area)
        
        with st.spinner("Cargando proyectos..."):
            proyectos_brutos = api_get_projects(selected_area)
            proyectos_unicos = list(dict.fromkeys(proyectos_brutos)) if proyectos_brutos else []
            
        if not proyectos_unicos:
            proyectos_unicos = ["No hay proyectos activos en esta área"]
            
        selected_project = st.selectbox("Proyecto:", options=proyectos_unicos)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Abrir Chat", type="primary", use_container_width=True):
            if selected_project and selected_project != "No hay proyectos activos en esta área":
                st.session_state.current_project = selected_project
                st.session_state.session_area = selected_area
                st.rerun()

# Fragmento para actualización en tiempo real de los mensajes
@st.fragment(run_every=5)
def render_live_messages(project_id):
    messages = api_get_chat(project_id)
    
    if not messages:
        st.info("No hay mensajes aún en este proyecto. ¡Sé el primero en escribir!")
        return

    for msg in messages:
        user_name = msg.get('usuario', 'Usuario')
        fecha_str = msg.get('fecha', '')
        hora_str = msg.get('hora', '')
        
        full_time = f"{fecha_str} {hora_str}".strip() if (fecha_str or hora_str) else ""
        text = msg.get('mensaje', '').replace('\n', '<br>')
        avatar_url = f"https://ui-avatars.com/api/?name={urllib.parse.quote(user_name)}&background=random&color=fff&size=100"
        
        is_own = (user_name == st.session_state.session_nombre)
        own_class = "own" if is_own else ""
        align_style = "flex-end" if is_own else "flex-start"

        st.markdown(f"""
            <div style="display:flex; flex-direction:column; align-items: {align_style}; width:100%;">
                <div class="chat-msg-container {own_class}">
                    <img src="{avatar_url}" class="chat-avatar">
                    <div class="chat-bubble-wrapper">
                        <div class="chat-meta {own_class}">
                            <span class="chat-name">{user_name}</span>
                            <span class="chat-time">{full_time}</span>
                        </div>
                        <div class="chat-bubble {own_class}">
                            {text}
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# ========================================================
# PANTALLA 3: CHAT DE PROYECTO
# ========================================================
def show_chat():
    project_id = st.session_state.current_project
    my_avatar = f"https://ui-avatars.com/api/?name={urllib.parse.quote(st.session_state.session_nombre)}&background=random&color=fff&size=100"
    
    st.markdown(f"""
        <div class="chat-header">
            <div class="chat-header-left">
                <div class="chat-header-title">{project_id}</div>
                <div class="chat-header-subtitle">Canal de discusión del proyecto</div>
            </div>
            <div class="chat-header-right">
                <div class="header-profile">
                    <div class="header-profile-info">
                        <span class="header-profile-name">{st.session_state.session_nombre}</span>
                        <span class="header-profile-role">{st.session_state.session_area}</span>
                    </div>
                    <img src="{my_avatar}">
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Renderizado en vivo de mensajes
    render_live_messages(project_id)
                    
    # Entrada de texto
    if prompt := st.chat_input(f"Escribe un mensaje en #{project_id}..."):
        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M:%S")
        
        payload = {
            "ID_Proyecto": project_id,
            "Area": st.session_state.session_area,
            "Nombre_Usuario": st.session_state.session_nombre,
            "Email": st.session_state.session_email,
            "Mensaje": prompt,
            "Fecha": fecha,
            "Hora": hora
        }
        
        api_post_message(payload)
        api_get_chat.clear(project_id)
        st.rerun()

# ========================================================
# BARRA LATERAL (SIDEBAR) - BLINDADA
# ========================================================
def show_sidebar():
    with st.sidebar:
        # 1. BOTÓN VOLVER
        if st.button("🏠 Volver al Menú", type="primary", use_container_width=True):
            st.session_state.current_project = ""
            st.session_state.sidebar_tab = "mensajes"
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. PESTAÑAS
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            btn_type_m = "primary" if st.session_state.get("sidebar_tab") == "mensajes" else "secondary"
            if st.button("💬 Chat", type=btn_type_m, use_container_width=True):
                st.session_state.sidebar_tab = "mensajes"
                st.rerun()
        with col_t2:
            btn_type_u = "primary" if st.session_state.get("sidebar_tab") == "usuarios" else "secondary"
            if st.button("👥 Equipo", type=btn_type_u, use_container_width=True):
                st.session_state.sidebar_tab = "usuarios"
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        
        # 3. PESTAÑA USUARIOS
        if st.session_state.get("sidebar_tab") == "usuarios":
            st.markdown('<div class="sidebar-title">MIEMBROS DEL EQUIPO</div>', unsafe_allow_html=True)
            
            try:
                users = api_get_users() or []
            except Exception as e:
                users = []
                st.caption(f"Error al cargar usuarios: {e}")
                
            if not users:
                st.markdown("<div style='font-size:12px; color:gray; padding:10px;'>No hay usuarios registrados</div>", unsafe_allow_html=True)
                
            for u_name in users:
                avatar_url = f"https://ui-avatars.com/api/?name={urllib.parse.quote(str(u_name))}&background=random&color=fff&size=100"
                is_me = (u_name == st.session_state.get("session_nombre", ""))
                
                status_text = ' (Tú)' if is_me else ''
                status_class = 'online' if is_me else 'offline'
                
                st.markdown(f"""
                    <div class="member-item">
                        <img src="{avatar_url}">
                        <span>{u_name}<small style="color:#CC3333; font-weight:600;">{status_text}</small></span>
                        <div class="status-dot {status_class}"></div>
                    </div>
                """, unsafe_allow_html=True)
                
        # 4. PESTAÑA PROYECTOS
        else:
            st.markdown('<div class="sidebar-title">INTERNO CHAT</div>', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-section">ÚLTIMOS PROYECTOS</div>', unsafe_allow_html=True)
            
            user_area = st.session_state.get("session_area", "")
            
            try:
                proyectos_brutos = api_get_projects(user_area) or []
                proyectos = list(dict.fromkeys(proyectos_brutos))[:5] if proyectos_brutos else []
            except Exception as e:
                proyectos = []
                st.caption(f"Error al cargar proyectos: {e}")
                
            if not proyectos:
                 st.markdown("<div style='font-size:12px; color:gray; padding:10px;'>No hay proyectos activos</div>", unsafe_allow_html=True)
                
            for idx, p in enumerate(proyectos):
                is_active = (p == st.session_state.get("current_project"))
                active_class = "active" if is_active else ""
                
                st.markdown(f"""
                    <div class="project-item {active_class}">
                        {p}
                        <div class="dot"></div>
                    </div>
                """, unsafe_allow_html=True)
                
                if not is_active:
                    if st.button("Cambiar", key=f"btn_side_{p}_{idx}", type="secondary", use_container_width=True):
                        st.session_state.current_project = p
                        st.rerun()
        
        st.markdown("<br><hr>", unsafe_allow_html=True)
        
        # 5. CERRAR SESIÓN
        if st.button("Cerrar Sesión", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.session_email = ""
            st.session_state.session_nombre = ""
            st.session_state.session_area = ""
            st.session_state.current_project = ""
            st.session_state.sidebar_tab = "mensajes"
            st.session_state.auto_login_error = ""
            if hasattr(st, "query_params"):
                st.query_params.clear()
            st.rerun()

# ========================================================
# INICIO DE LA APP
# ========================================================
def main():
    init_session_state()
    inject_custom_css()
    process_url_auto_login()
    
    # Manejo de visibilidad del sidebar según el estado de inicio de sesión
    if not st.session_state.logged_in:
        # En pantalla de login ocultamos la barra
        st.markdown("""
            <style>
                [data-testid="stSidebar"] { display: none !important; }
            </style>
        """, unsafe_allow_html=True)
        show_login()
    else:
        # Una vez logueado FORZAMOS a que la barra lateral sea visible
        st.markdown("""
            <style>
                [data-testid="stSidebar"] { 
                    display: block !important; 
                    visibility: visible !important; 
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Renderizar la barra lateral
        show_sidebar()
        
        # Renderizar la vista principal
        if not st.session_state.current_project:
            show_project_selection()
        else:
            show_chat()

if __name__ == "__main__":
    main()