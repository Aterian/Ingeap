# pyrefly: ignore [missing-import]
import customtkinter as ctk
import requests
import threading
from datetime import datetime
import json

# ========================================================
# CONFIGURACIÓN
# ========================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Reemplaza esta URL con el Webhook (URL del script web) que te da Google Apps Script
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbws3ZFKLFOszzEimgGGkh0ed-hRpH1ECNYuD2Sdmbzyhj7ItgbcygmZ7qGNba_j1TKDdQ/exec"

class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Chat de Proyecto")
        self.geometry("350x600")
        self.resizable(False, False)
        
        # Propiedad: Flotante / Always on Top
        self.attributes("-topmost", True)

        # Variables de Sesión
        self.session_email = ""
        self.session_nombre = ""
        self.session_area = ""
        self.current_project = ""

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frames de las pantallas
        self.login_frame = LoginFrame(self)
        self.project_frame = ProjectSelectionFrame(self)
        self.chat_frame = ChatFrame(self)

        self.show_frame("login")

    def show_frame(self, frame_name):
        self.login_frame.grid_forget()
        self.project_frame.grid_forget()
        self.chat_frame.grid_forget()

        if frame_name == "login":
            self.login_frame.grid(row=0, column=0, sticky="nsew")
        elif frame_name == "project":
            self.project_frame.load_data()
            self.project_frame.grid(row=0, column=0, sticky="nsew")
        elif frame_name == "chat":
            self.chat_frame.setup_chat()
            self.chat_frame.grid(row=0, column=0, sticky="nsew")


# ========================================================
# PANTALLA 1: LOGIN
# ========================================================
class LoginFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.lbl_title = ctk.CTkLabel(self, text="Inicio de Sesión", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.pack(pady=(120, 30))

        self.entry_email = ctk.CTkEntry(self, placeholder_text="Email", width=250)
        self.entry_email.pack(pady=10)

        self.entry_password = ctk.CTkEntry(self, placeholder_text="Clave", show="*", width=250)
        self.entry_password.pack(pady=10)

        self.btn_login = ctk.CTkButton(self, text="Ingresar", width=250, command=self.login)
        self.btn_login.pack(pady=20)

        self.lbl_msg = ctk.CTkLabel(self, text="", text_color="red")
        self.lbl_msg.pack(pady=5)

    def login(self):
        email = self.entry_email.get().strip()
        clave = self.entry_password.get()

        if not email or not clave:
            self.lbl_msg.configure(text="Completar todos los campos", text_color="red")
            return

        self.btn_login.configure(state="disabled", text="Verificando...")
        self.lbl_msg.configure(text="")
        
        # Ejecutar petición en hilo secundario para no congelar la UI
        threading.Thread(target=self.do_login_request, args=(email, clave)).start()

    def do_login_request(self, email, clave):
        try:
            # Lógica Dummy (para pruebas sin URL real)
            if "DUMMY_URL" in WEBHOOK_URL:
                data = {"success": True, "nombre": "Usuario Prueba", "area": "IT"}
                import time
                time.sleep(1) # Simular latencia
            else:
                res = requests.get(WEBHOOK_URL, params={"action": "login", "email": email, "clave": clave})
                data = res.json()

            if data.get("success"):
                self.master.session_email = email
                self.master.session_nombre = data.get("nombre")
                self.master.session_area = data.get("area")
                
                # Regresar al hilo principal para actualizar UI
                self.after(0, lambda: self.master.show_frame("project"))
            else:
                self.after(0, lambda: self.lbl_msg.configure(text=data.get("message", "Error de credenciales"), text_color="red"))
        except Exception as e:
            print("Login error details:", repr(e))
            self.after(0, lambda: self.lbl_msg.configure(text="Error de conexión (ver consola)", text_color="red"))
        finally:
            self.after(0, lambda: self.btn_login.configure(state="normal", text="Ingresar"))


# ========================================================
# PANTALLA 2: SELECCIÓN DE PROYECTO
# ========================================================
class ProjectSelectionFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.lbl_title = ctk.CTkLabel(self, text="Selección de Proyecto", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(pady=(60, 30))

        self.lbl_area = ctk.CTkLabel(self, text="Área:")
        self.lbl_area.pack(pady=(10, 0))
        
        # Suponiendo que hay áreas fijas o se pueden adaptar
        self.option_area = ctk.CTkOptionMenu(self, values=["I", "M", "A", "S"], 
                                             width=250, command=self.on_area_change)
        self.option_area.pack(pady=(0, 20))

        self.lbl_project = ctk.CTkLabel(self, text="Proyecto:")
        self.lbl_project.pack(pady=(10, 0))

        self.option_project = ctk.CTkOptionMenu(self, values=["Seleccione..."], width=250)
        self.option_project.pack(pady=(0, 30))

        self.btn_open = ctk.CTkButton(self, text="Abrir Chat", width=250, command=self.open_chat)
        self.btn_open.pack(pady=10)
        
        self.btn_logout = ctk.CTkButton(self, text="Cerrar Sesión", width=250, fg_color="transparent", 
                                        border_width=1, text_color=("gray10", "gray90"), command=self.logout)
        self.btn_logout.pack(pady=20)

    def load_data(self):
        user_area = self.master.session_area
        
        # Asegurarnos de que el área del usuario exista en las opciones, si no, agregarla
        current_areas = self.option_area.cget("values")
        if user_area and user_area not in current_areas:
            new_areas = list(current_areas)
            new_areas.append(user_area)
            self.option_area.configure(values=new_areas)

        if user_area:
            self.option_area.set(user_area)
            self.on_area_change(user_area)

    def on_area_change(self, selected_area):
        self.option_project.configure(values=["Cargando proyectos..."])
        self.option_project.set("Cargando proyectos...")
        threading.Thread(target=self.fetch_projects, args=(selected_area,)).start()

    def fetch_projects(self, area):
        try:
            if "DUMMY_URL" in WEBHOOK_URL:
                projects = [f"PROJ-{area}-01", f"PROJ-{area}-02", f"PROJ-{area}-03"]
                import time
                time.sleep(0.5)
            else:
                res = requests.get(WEBHOOK_URL, params={"action": "get_projects", "area": area})
                data = res.json()
                projects = data.get("projects", [])

            if not projects:
                projects = ["No hay proyectos activos"]
                
            self.after(0, lambda: self.update_projects_dropdown(projects))
        except Exception:
            self.after(0, lambda: self.update_projects_dropdown(["Error de conexión"]))

    def update_projects_dropdown(self, projects):
        self.option_project.configure(values=projects)
        self.option_project.set(projects[0])

    def open_chat(self):
        project = self.option_project.get()
        if project and project not in ["Seleccione...", "Cargando proyectos...", "No hay proyectos activos", "Error de conexión"]:
            self.master.current_project = project
            self.master.show_frame("chat")
            
    def logout(self):
        self.master.session_email = ""
        self.master.session_nombre = ""
        self.master.session_area = ""
        self.master.current_project = ""
        self.master.show_frame("login")


# ========================================================
# PANTALLA 3: CHAT DE PROYECTO
# ========================================================
class ChatFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Header (Top)
        self.header_frame = ctk.CTkFrame(self, fg_color=("gray80", "gray15"), corner_radius=0)
        self.header_frame.pack(fill="x")
        
        self.btn_back = ctk.CTkButton(self.header_frame, text="< Volver", width=60, 
                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray25"), command=self.go_back)
        self.btn_back.pack(side="left", padx=5, pady=10)

        self.lbl_title = ctk.CTkLabel(self.header_frame, text="Proyecto", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_title.pack(side="left", padx=10, pady=10, expand=True)
        
        self.btn_refresh = ctk.CTkButton(self.header_frame, text="↻", width=30, 
                                         fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray25"), command=self.load_messages)
        self.btn_refresh.pack(side="right", padx=5, pady=10)

        # Historial de Chat (Middle)
        self.scrollable_chat = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_chat.pack(fill="both", expand=True, padx=5, pady=5)

        # Input Area (Bottom)
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.entry_msg = ctk.CTkEntry(self.input_frame, placeholder_text="Escribe un mensaje...")
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_msg.bind("<Return>", lambda event: self.send_message())

        self.btn_send = ctk.CTkButton(self.input_frame, text="Enviar", width=70, command=self.send_message)
        self.btn_send.pack(side="right")

    def setup_chat(self):
        self.lbl_title.configure(text=self.master.current_project)
        self.load_messages()

    def go_back(self):
        self.master.show_frame("project")

    def clear_chat_area(self):
        for widget in self.scrollable_chat.winfo_children():
            widget.destroy()

    def load_messages(self):
        self.clear_chat_area()
        self.lbl_status = ctk.CTkLabel(self.scrollable_chat, text="Cargando mensajes...", text_color="gray")
        self.lbl_status.pack(pady=20)
        
        project_id = self.master.current_project
        threading.Thread(target=self.fetch_chat_log, args=(project_id,)).start()

    def fetch_chat_log(self, project_id):
        try:
            if "DUMMY_URL" in WEBHOOK_URL:
                messages = [
                    {"usuario": "Admin", "mensaje": f"Canal de chat creado para {project_id}.", "fecha": "2024-01-01", "hora": "09:00:00"}
                ]
                import time
                time.sleep(0.5)
            else:
                res = requests.get(WEBHOOK_URL, params={"action": "get_chat", "id_proyecto": project_id})
                data = res.json()
                messages = data.get("messages", [])

            self.after(0, lambda: self.render_messages(messages))
        except Exception:
            self.after(0, lambda: self.render_error())

    def render_messages(self, messages):
        self.clear_chat_area()
        
        if not messages:
            lbl = ctk.CTkLabel(self.scrollable_chat, text="No hay mensajes aún en este proyecto.", text_color="gray")
            lbl.pack(pady=20)
            return

        for msg in messages:
            self.draw_bubble(msg['usuario'], msg['mensaje'], f"{msg['fecha']} {msg['hora']}")

    def render_error(self):
        self.clear_chat_area()
        lbl = ctk.CTkLabel(self.scrollable_chat, text="Error de conexión al cargar mensajes.", text_color="red")
        lbl.pack(pady=20)

    def draw_bubble(self, user, text, timestamp):
        is_me = (user == self.master.session_nombre)
        
        bubble_wrapper = ctk.CTkFrame(self.scrollable_chat, fg_color="transparent")
        bubble_wrapper.pack(fill="x", pady=5)
        
        bubble_color = "#1f538d" if is_me else "#2b2b2b"
        bubble = ctk.CTkFrame(bubble_wrapper, fg_color=bubble_color, corner_radius=10)
        
        if is_me:
            bubble.pack(side="right", anchor="e", padx=(40, 5))
            
            lbl_text = ctk.CTkLabel(bubble, text=text, wraplength=200, justify="left", text_color="white")
            lbl_text.pack(anchor="e", padx=12, pady=(10, 2))
            
            lbl_time = ctk.CTkLabel(bubble, text=timestamp, font=ctk.CTkFont(size=9), text_color="#a8c1de")
            lbl_time.pack(anchor="e", padx=12, pady=(0, 5))
        else:
            bubble.pack(side="left", anchor="w", padx=(5, 40))
            
            lbl_name = ctk.CTkLabel(bubble, text=user, font=ctk.CTkFont(size=10, weight="bold"), text_color="#a8c1de")
            lbl_name.pack(anchor="w", padx=12, pady=(5, 0))

            lbl_text = ctk.CTkLabel(bubble, text=text, wraplength=200, justify="left", text_color="white")
            lbl_text.pack(anchor="w", padx=12, pady=(2, 2))
            
            lbl_time = ctk.CTkLabel(bubble, text=timestamp, font=ctk.CTkFont(size=9), text_color="#888888")
            lbl_time.pack(anchor="e", padx=12, pady=(0, 5))
        
        # Bajar el scroll al final usando la función de CustomTkinter
        self.scrollable_chat._parent_canvas.yview_moveto(1.0)


    def send_message(self):
        text = self.entry_msg.get().strip()
        if not text:
            return
            
        self.entry_msg.delete(0, "end")
        self.btn_send.configure(state="disabled")
        
        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M:%S")
        
        payload = {
            "ID_Proyecto": self.master.current_project,
            "Area": self.master.session_area,
            "Nombre_Usuario": self.master.session_nombre,
            "Email": self.master.session_email,
            "Mensaje": text,
            "Fecha": fecha,
            "Hora": hora
        }
        
        # Visual Optimism (Muestra el mensaje inmediatamente en el chat)
        self.draw_bubble(self.master.session_nombre, text, f"{fecha} {hora}")
        
        threading.Thread(target=self.post_message, args=(payload,)).start()

    def post_message(self, payload):
        try:
            if "DUMMY_URL" not in WEBHOOK_URL:
                requests.post(WEBHOOK_URL, json=payload)
        except Exception as e:
            print(f"Error: {e}")
            # Aquí se podría manejar el error visualmente si se desea
        finally:
            self.after(0, lambda: self.btn_send.configure(state="normal"))

# ========================================================
# INICIO DE LA APP
# ========================================================
if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
