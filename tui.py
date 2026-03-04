import os
import subprocess
import datetime
import io
import contextlib
from smolagents import LiteLLMModel, Tool, ToolCallingAgent

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, RichLog, Label, LoadingIndicator
from textual.containers import Container, VerticalScroll, Vertical
from textual import work

PROJECT_BASE = os.getcwd()
MODEL_ID = "qwen2.5-coder:7b-instruct-q4_K_M"
PROVIDER = "Ollama"

def write_log(tool_name, inputs, output):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f" [{'='*10} {timestamp} {tool_name} {'='*10}]\n INPUTS: {inputs}\n OUTPUT: {output}\n\n"
    with open("agent_audit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

def safe_path(path):
    if not path or path == "/": return PROJECT_BASE
    # Eliminamos cualquier intento de ruta absoluta que envíe el modelo para forzar relativa
    clean_path = path.replace(PROJECT_BASE, "").lstrip("/")
    full_path = os.path.abspath(os.path.join(PROJECT_BASE, clean_path))
    
    if not full_path.startswith(PROJECT_BASE):
        return PROJECT_BASE
    return full_path

# --- HERRAMIENTAS (TUS CLASES ORIGINALES) ---
class RepoMapTool(Tool):
    name = "repo_mapper"
    description = "Muestra carpetas del proyecto. Solo funciona dentro del directorio actual."
    inputs = {"root_dir": {"type": "string", "description": "Subcarpeta (opcional)", "nullable": True}}
    output_type = "string"
    def forward(self, root_dir: str = "."):
        target = safe_path(root_dir)
        exclude = {'.git', 'vendor', 'node_modules', 'storage', 'bootstrap/cache', '__pycache__', 'agent-venv'}
        tree = []
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in exclude]
            level = root.replace(target, '').count(os.sep)
            indent = ' ' * 4 * level
            tree.append(f"{indent}{os.path.basename(root)}/")
            valid_exts = ('.php', '.js', '.jsx', '.ts', '.tsx', '.rb', '.py', '.md', '.yml', '.json')
            for f in files:
                if f.endswith(valid_exts):
                    tree.append(f"{' ' * 4 * (level + 1)}{f}")
        res = "\n".join(tree[:100])
        write_log(self.name, root_dir, "Mapa generado.")
        return res

class FileWriteTool(Tool):
    name = "file_writer"
    description = "Escribe archivos DENTRO del proyecto. Crea carpetas automáticamente."
    inputs = {"path": {"type": "string", "description": "Ruta relativa", "nullable": True}, "content": {"type": "string", "description": "Contenido", "nullable": True}}
    output_type = "string"
    def forward(self, path: str = None, content: str = None):
        if not path: return "❌ Error: Ruta vacía."
        target = safe_path(path)
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content if content else "")
            write_log(self.name, path, f"Guardado en {target}")
            return f"✅ Archivo guardado en: {path}"
        except Exception as e: return f"❌ Error: {str(e)}"

class FileReadTool(Tool):
    name = "file_reader"
    description = "Lee el contenido de un archivo."
    inputs = {"path": {"type": "string", "description": "Ruta del archivo", "nullable": True}}
    output_type = "string"

    def forward(self, path: str = None):
        if not path: return "❌ Error: Ruta vacía."
        target = safe_path(path) # Usamos safe_path por seguridad
        try:
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()
                write_log(self.name, path, "Lectura exitosa") # Añadimos el log
                return f"--- CONTENIDO DE {path} ---\n{content}"
        except Exception as e:
            return f"❌ Error leyendo {path}: {str(e)}"

class TerminalTool(Tool):
    name = "terminal"
    description = "Ejecuta comandos DENTRO de la carpeta del proyecto."
    inputs = {"command": {"type": "string", "description": "Comando", "nullable": True}}
    output_type = "string"
    def forward(self, command: str = None):
        if not command: return "❌ No hay comando."
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=PROJECT_BASE)
            write_log(self.name, command, "Ejecutado.")
            return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        except Exception as e: return str(e)

# --- AGENTE ---
agent = ToolCallingAgent(
    tools=[RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool()],
    model=LiteLLMModel(model_id=f"ollama/{MODEL_ID}", api_base="http://localhost:11434"),
    add_base_tools=True,
    max_steps=30
)

# PROMPT DE ACCESO TOTAL
SYSTEM_PROMPT = f"""
ERES UN AGENTE DE ACCIÓN LOCAL, Arquitecto de Software Senior.

TRABAJO LOCAL: Estás limitado exclusivamente a la carpeta: {PROJECT_BASE}
TU DIRECTORIO DE TRABAJO ES: {PROJECT_BASE}

INSTRUCCIONES CRÍTICAS:
1. TIENES ACCESO TOTAL a las herramientas proporcionadas (repo_mapper, file_writer, etc.). 
2. NO PIDAS PERMISO para acceder a archivos, YA LO TIENES. Ejecuta las herramientas directamente.
3. Si el usuario te pide crear un archivo, USA 'file_writer'. No digas "necesitaríamos acceder", simplemente HAZLO.
4. Todas las rutas que uses deben ser RELATIVAS al proyecto.

REGLAS:
1. NUNCA intentes acceder a rutas fuera de esta carpeta.
2. NUNCA uses '/' como root_dir en repo_mapper. Usa '.' para el proyecto actual.
3. No uses comandos de Python (os, shutil) para archivos; usa 'file_writer'.
4. Si necesitas una carpeta, 'file_writer' la creará por ti al guardar un archivo.

IMPORTANTE: 'file_writer' crea carpetas automáticamente. No intentes crearlas tú con comandos de Python.

FLUJO OBLIGATORIO:
1. Mapea el proyecto con 'repo_mapper' (usa '.' para la raíz).
2. Si vas a modificar algo, lee primero con 'file_reader'.
3. Escribe los cambios con 'file_writer'.
4. Prueba con 'terminal' (ej: php artisan test, python3 script.py).
"""

class ArquitectoApp(App):
    CSS = """
    Screen { background: #1a1b26; }
    
    #main_container { layout: horizontal; height: 1fr; }
    
    /* Contenedor de la izquierda (Chat + Loader) */
    #left_pane {
        width: 65%;
        height: 1fr;
        layout: vertical;
    }

    #chat_area { 
        height: 1fr; /* Ocupa todo el espacio disponible */
        border: tall #414868; 
        background: #1a1b26; 
        padding: 1; 
    }
    #chat_area.working { border: tall #bb9af7; }

    #log_area { 
        width: 35%; 
        border: tall #414868; 
        background: #16161e; 
        color: #7aa2f7; 
    }
    
    .user-msg { color: #9ece6a; margin: 1 0; text-style: bold; border-bottom: dashed #2e3c64; }
    .agent-msg { color: #7dcfff; margin: 1 0; background: #24283b; padding: 1; border-left: solid #7dcfff; }
    
    #loader-container {
        height: auto;
        min-height: 3;
        background: #1f2335;
        border-top: solid #414868;
        display: none;
        padding: 0 1;
    }
    #loader-container.visible { display: block; layout: horizontal; }
    #loader-text { 
        margin-left: 2; 
        color: #e0af68; 
        content-align: left middle; /* Antes decía middle left, ahora está corregido */
        height: 3; 
    }

    /* Estilo para el TextArea de entrada mejorado */
    #user-input {
        dock: bottom;
        height: 5; 
        margin: 1;
        border: double #bb9af7;
        background: #1a1b26;
        color: white;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main_container"):
            with Vertical(id="chat_vertical"):
                with VerticalScroll(id="chat_area"):
                    yield Label("✨ Arquitecto Online. Esperando instrucciones...", id="welcome-text")
                with Static(id="loader-container"):
                    yield LoadingIndicator()
                    yield Label(" El Arquitecto está operando...", variant="title")
            yield RichLog(id="log_area", highlight=True, markup=True)
        yield Input(placeholder="> Describe la tarea...", id="user-input")
        yield Footer()

    def on_mount(self) -> None:
        self.title = f"Arquitecto Senior M4 [{PROVIDER}]"
        self.sub_title = f"Modelo: {MODEL_ID} | 📂 {PROJECT_BASE}"
        self.set_interval(0.5, self.update_logs)

    def update_logs(self):
        if os.path.exists("agent_audit.log"):
            with open("agent_audit.log", "r") as f:
                lines = f.readlines()
                self.query_one("#log_area").clear()
                self.query_one("#log_area").write("".join(lines[-30:]))

    @work(exclusive=True, thread=True)
    def process_task(self, user_text: str) -> None:
        chat_area = self.query_one("#chat_area")
        loader = self.query_one("#loader-container")
        
        # UI: Activar Loader y cambiar bordes
        self.call_from_thread(chat_area.add_class, "working")
        self.call_from_thread(loader.add_class, "visible")
        self.call_from_thread(chat_area.mount, Label(f"➜ USUARIO: {user_text}", classes="user-msg"))
        self.call_from_thread(chat_area.scroll_end)

        try:
            response = agent.run(f"{SYSTEM_PROMPT}\n\nTarea: {user_text}")
            self.call_from_thread(chat_area.mount, Label(f"🤖 ARQUITECTO:\n{response}", classes="agent-msg"))
        except Exception as e:
            self.call_from_thread(chat_area.mount, Label(f"❌ ERROR: {str(e)}", classes="agent-msg"))
        
        # UI: Desactivar Loader
        self.call_from_thread(chat_area.remove_class, "working")
        self.call_from_thread(loader.remove_class, "visible")
        self.call_from_thread(chat_area.scroll_end)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.process_task(event.value)
            event.input.value = ""

if __name__ == "__main__":
    if os.path.exists("agent_audit.log"): open("agent_audit.log", "w").close()
    ArquitectoApp().run()