import os
import subprocess
import datetime
import io
import contextlib
import threading
from smolagents import LiteLLMModel, Tool, ToolCallingAgent

# --- IMPORTACIONES DE TEXTUAL ---
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, RichLog, Label
from textual.containers import Container, Horizontal, VerticalScroll
from textual import work

# --- TU CORE (SIN MODIFICACIONES) ---
PROJECT_BASE = os.getcwd()

def write_log(tool_name, inputs, output):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f" [{'='*10} {timestamp} {tool_name} {'='*10}]\n INPUTS: {inputs}\n OUTPUT: {output}\n\n"
    with open("agent_audit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

def safe_path(path):
    if not path or path == "/": return PROJECT_BASE
    full_path = os.path.abspath(os.path.join(PROJECT_BASE, path.lstrip("/")))
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
        if not path: return "❌ Error: Debes proporcionar una ruta."
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f"--- CONTENIDO DE {path} ---\n{f.read()}"
        except Exception as e: return f"❌ Error leyendo {path}: {str(e)}"

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

# --- CONFIGURACIÓN AGENTE ---
model = LiteLLMModel(model_id="ollama/qwen2.5-coder:7b-instruct-q4_K_M", api_base="http://localhost:11434")
agent = ToolCallingAgent(
    tools=[RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool()],
    model=model,
    add_base_tools=True,
    max_steps=30
)

SYSTEM_PROMPT = f"""
Eres un Arquitecto de Software Senior. 
TRABAJO LOCAL: Estás limitado exclusivamente a la carpeta: {PROJECT_BASE}
REGLAS: ... (Aquí va tu prompt completo) ...
"""

# --- INTERFAZ TEXTUAL ---

class ArquitectoApp(App):
    """Una interfaz profesional para el Agente."""
    
    CSS = """
    Screen {
        background: #1a1b26;
    }
    #main_container {
        layout: horizontal;
        height: 1fr;
    }
    #chat_area {
        width: 75%;
        border: solid #414868;
        padding: 1;
    }
    #log_area {
        width: 25%;
        border: solid #414868;
        background: #16161e;
        color: #7aa2f7;
    }
    .user-msg {
        color: #9ece6a;
        margin: 1 0;
        text-style: bold;
    }
    .agent-msg {
        color: #7dcfff;
        margin: 1 0;
        border-left: solid #7dcfff;
        padding-left: 1;
    }
    Input {
        dock: bottom;
        margin: 1;
        border: double #bb9af7;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="Arquitecto M4")
        with Container(id="main_container"):
            with VerticalScroll(id="chat_area"):
                yield Label("✨ Bienvenido. Esperando tu comando...", id="welcome-text")
            yield RichLog(id="log_area", highlight=True, markup=True)
        yield Input(placeholder="Escribe tu mensaje aquí y presiona Enter...", id="user-input")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Arquitecto Senior M4"
        self.sub_title = f"Ruta: {PROJECT_BASE}"
        # Iniciar monitor de logs
        self.set_interval(1, self.update_logs)

    def update_logs(self):
        """Lee el archivo de auditoría y actualiza el panel lateral."""
        if os.path.exists("agent_audit.log"):
            with open("agent_audit.log", "r") as f:
                content = f.read().splitlines()
                # Solo mostrar las últimas líneas nuevas
                log_widget = self.query_one("#log_area", RichLog)
                log_widget.clear()
                for line in content[-50:]: # Últimas 50 líneas
                    log_widget.write(line)

    @work(exclusive=True)
    async def process_task(self, user_text: str) -> None:
        chat_area = self.query_one("#chat_area")
        
        # 1. Agregar mensaje del usuario al chat
        chat_area.mount(Label(f"➜ Tú: {user_text}", classes="user-msg"))
        
        # 2. Silenciador y ejecución
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            try:
                # Ejecutamos el agente (esto corre en un hilo separado gracias a @work)
                response = agent.run(f"{SYSTEM_PROMPT}\n\nTarea: {user_text}")
                chat_area.mount(Label(f"🤖 Arquitecto:\n{response}", classes="agent-msg"))
            except Exception as e:
                chat_area.mount(Label(f"❌ Error: {str(e)}", classes="agent-msg"))
        
        chat_area.scroll_end()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.process_task(event.value)
            event.input.value = "" # Limpiar input

if __name__ == "__main__":
    app = ArquitectoApp()
    app.run()