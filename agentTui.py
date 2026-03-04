import os
import subprocess
import datetime
import logging
import io
import contextlib
import threading
import time
from smolagents import LiteLLMModel, Tool, ToolCallingAgent
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.spinner import Spinner
from rich.padding import Padding

# --- CONFIGURACIÓN BASE ---
PROJECT_BASE = os.getcwd()
MODEL_ID = "qwen2.5-coder:7b-instruct-q4_K_M"
logging.getLogger("smolagents").setLevel(logging.ERROR)
console = Console()

if os.path.exists("agent_audit.log"):
    os.remove("agent_audit.log")

# --- UTILIDADES ---
def write_log(tool_name, inputs, output):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    # Formato corto para la TUI
    log_entry = f"[{timestamp}] {tool_name.upper()}: {str(inputs)[:30]}... -> OK\n"
    with open("agent_audit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

def safe_path(path):
    if not path or path == "/": return PROJECT_BASE
    full_path = os.path.abspath(os.path.join(PROJECT_BASE, path.lstrip("/")))
    return full_path if full_path.startswith(PROJECT_BASE) else PROJECT_BASE

class ChatState:
    def __init__(self):
        self.working = False
        self.messages = []  # Lista de tuplas (rol, contenido)
        self.current_logs = ""


# --- HERRAMIENTAS (Incluyen safe_path y write_log) ---
class RepoMapTool(Tool):
    name = "repo_mapper"
    description = "Muestra carpetas del proyecto."
    inputs = {"root_dir": {"type": "string", "description": "Subcarpeta", "nullable": True}}
    output_type = "string"
    def forward(self, root_dir: str = "."):
        target = safe_path(root_dir)
        tree = [f"{os.path.basename(root)}/" for root, dirs, files in os.walk(target) if ".git" not in root][:20]
        res = "\n".join(tree)
        write_log(self.name, root_dir, "Mapped")
        return res

class FileWriteTool(Tool):
    name = "file_writer"
    description = "Escribe archivos."
    inputs = {"path": {"type": "string", "description": "Ruta", "nullable": True}, "content": {"type": "string", "description": "Contenido", "nullable": True}}
    output_type = "string"
    def forward(self, path: str = None, content: str = None):
        target = safe_path(path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w") as f: f.write(content or "")
        write_log(self.name, path, "Saved")
        return f"✅ Guardado: {path}"

class FileReadTool(Tool):
    name = "file_reader"
    description = "Lee archivos."
    inputs = {"path": {"type": "string", "description": "Ruta", "nullable": True}}
    output_type = "string"
    def forward(self, path: str = None):
        target = safe_path(path)
        with open(target, "r") as f: content = f.read()
        write_log(self.name, path, "Read")
        return content

class TerminalTool(Tool):
    name = "terminal"
    description = "Ejecuta comandos."
    inputs = {"command": {"type": "string", "description": "Comando", "nullable": True}}
    output_type = "string"
    def forward(self, command: str = None):
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=PROJECT_BASE)
        write_log(self.name, command, "Executed")
        return result.stdout

# --- LÓGICA DE LA TUI ---
def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=5), # Aumentamos el tamaño a 5
    )
    layout["main"].split_row(
        Layout(name="chat_body", ratio=3),
        Layout(name="side_logs", ratio=1),
    )
    return layout

class AgentState:
    def __init__(self):
        self.working = False
        self.result = ""
        self.last_logs = ""
        self.prompt = ""
        self.messages = []  # <--- Esta es la que faltaba para el Chat

state = AgentState()

def run_agent_thread(agent, user_prompt):
    # Limpiamos los logs de la tarea anterior para que el panel lateral esté fresco
    with open("agent_audit.log", "w") as f: f.write("") 
    
    state.working = True
    state.messages.append(("User", user_prompt))
    
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        try:
            # Aquí el SYSTEM_PROMPT ayuda a que el modelo sepa qué hacer
            result = agent.run(f"{SYSTEM_PROMPT}\n\nTarea: {user_prompt}")
            state.messages.append(("Agent", result))
        except Exception as e:
            state.messages.append(("Agent", f"❌ Error: {str(e)}"))
    
    state.working = False


def get_chat_history():
    group_elements = []
    
    if not state.messages:
        return Text("\n Esperando tu primer comando...", style="dim italic", justify="center")

    for role, content in state.messages:
        if role == "User":
            # Cuadro para el usuario (alineado a la izquierda por defecto)
            group_elements.append(
                Panel(
                    Text(content, style="bright_white"), 
                    title="[bold green] Tú [/bold green]", 
                    border_style="green", 
                    title_align="left"
                )
            )
        else:
            # Cuadro para el agente
            group_elements.append(
                Panel(
                    Text(content, style="cyan"), 
                    title="[bold blue] Arquitecto [/bold blue]", 
                    border_style="blue", 
                    title_align="left"
                )
            )
    
    if state.working:
        group_elements.append(
            Padding(Spinner("dots", text="[bold yellow] Razonando...[/bold yellow]"), (1, 2))
        )
    
    return Group(*group_elements)

def get_recent_logs():
    if not os.path.exists("agent_audit.log"): return Text("Esperando...", style="dim")
    with open("agent_audit.log", "r") as f:
        return Text.from_markup("".join(f.readlines()[-15:]))

def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3), # El espacio para el "input" (visual)
    )
    layout["main"].split_row(
        Layout(name="chat_body", ratio=3),
        Layout(name="side_logs", ratio=1),
    )
    return layout

# --- INICIALIZACIÓN ---
model = LiteLLMModel(model_id=f"ollama/{MODEL_ID}", api_base="http://localhost:11434")
agent = ToolCallingAgent(tools=[RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool()], model=model, add_base_tools=False)

SYSTEM_PROMPT = f"Eres un Arquitecto Senior. Solo operas en {PROJECT_BASE}."

def refresh_ui(layout):
    layout["header"].update(Panel(
        Text(f"🤖 Modelo: {MODEL_ID} | 📂 {PROJECT_BASE}", justify="center"), 
        style="bold white on blue"
    ))
    
    layout["chat_body"].update(Panel(get_chat_history(), title=" Historial de Chat ", border_style="white"))
    layout["side_logs"].update(Panel(get_recent_logs(), title=" Actividad Técnica ", border_style="magenta"))
    
    # FOOTER DINÁMICO
    if state.working:
        footer_text = Text("⏳ El Arquitecto está procesando tu solicitud...", justify="center", style="bold yellow")
    else:
        footer_text = Text("✨ Listo para recibir órdenes. Escribe abajo:", justify="center", style="dim")
        
    layout["footer"].update(Panel(footer_text, border_style="dim"))

    if state.working:
        footer_content = Text("\n⏳ El Arquitecto está procesando...", justify="center", style="bold yellow")
    else:
        # Dibujamos el indicador de entrada dentro del panel
        footer_content = Text("\n> Esperando comando...", style="bold green")
        
    layout["footer"].update(Panel(footer_content, title=" Terminal de Entrada ", border_style="bright_magenta"))

if __name__ == "__main__":
    layout = make_layout()
    
    while True:
        console.clear()
        refresh_ui(layout)
        console.print(layout)
        
        # El cursor aparecerá justo debajo del cuadro de la terminal.
        # Al usar un prompt vacío o muy corto en console.input, 
        # se siente como parte de la interfaz.
        try:
            user_input = console.input("[bold magenta] > [/bold magenta]")
        except EOFError:
            break
            
        if user_input.lower() in ["exit", "salir"]:
            break
        
        # ... (lanzar el hilo del agente igual que antes) ...
        with Live(layout, refresh_per_second=4, screen=True):
            while state.working:
                refresh_ui(layout)
                time.sleep(0.1)

# --- MAIN ---
SYSTEM_PROMPT = f"""
Eres un Ingeniero de Software Senior en modo EJECUCIÓN TOTAL. 
Tu objetivo no es solo analizar, es DEJAR EL TRABAJO HECHO en el sistema de archivos.

ENTORNO DE TRABAJO: Estás anclado a {PROJECT_BASE}.

DIRECTIVAS CRÍTICAS DE ACCIÓN:
1. NO TE DETENGAS hasta que los archivos solicitados existan físicamente.
2. Si el usuario pide un script, tu respuesta FINAL solo debe darse DESPUÉS de haber usado 'file_writer'.
3. 'repo_mapper' es solo el primer paso. Una vez que conozcas la ruta, procede INMEDIATAMENTE a escribir o leer.
4. Si necesitas crear una carpeta, simplemente define la ruta en 'file_writer' (ej: 'test/script.py') y la herramienta la creará por ti. No pidas permiso.

PROTOCOLO DE PASOS SEGUIDOS:
Paso 1: Mapear ubicación actual con 'repo_mapper'.
Paso 2: Leer archivos relevantes con 'file_reader' si el contexto lo requiere.
Paso 3: Crear/Modificar archivos con 'file_writer' inyectando el código completo y profesional.
Paso 4: Validar mediante 'terminal' que el archivo se guardó o ejecutarlo para probarlo.

REGLA DE SEGURIDAD: Prohibido usar '/' o rutas absolutas. Todo es relativo a '.'.
"""

model = LiteLLMModel(model_id=f"ollama/{MODEL_ID}", api_base="http://localhost:11434")
agent = ToolCallingAgent(tools=[RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool()], model=model, max_steps=30)

if __name__ == "__main__":
    # 1. Pantalla de Bienvenida e Input
    console.clear()
    console.print(Panel(f"[bold blue]AGENTE ARQUITECTO M4[/bold blue]\n[dim]Modelo: {MODEL_ID}[/dim]", expand=False))
    
    user_prompt = console.input("\n[bold yellow]🚀 ¿Qué quieres construir?: [/bold yellow]")
    
    state.prompt = user_prompt
    state.working = True

    # 2. Configurar Layout
    layout = make_layout()
    
    # 3. Lanzar Agente
    thread = threading.Thread(
        target=run_agent_thread, 
        args=(agent, f"{SYSTEM_PROMPT}\n\nTarea: {user_prompt}")
    )
    thread.start()

    # 4. Interfaz en Vivo
    try:
        with Live(layout, refresh_per_second=4, screen=True):
            while state.working:
                # HEADER
                layout["header"].update(Panel(
                    Text.from_markup(f"🤖 [bold]Modelo:[/bold] {MODEL_ID} | [bold green]TRABAJANDO[/bold green]"),
                    border_style="blue"
                ))
                
                # CUERPO (IZQUIERDA) - Aquí mostramos el prompt y el progreso
                body_group = Group(
                    Panel(Text(f"Tu Prompt: {state.prompt}", style="yellow italic"), title="Entrada", border_style="dim"),
                    Text("\n"),
                    Spinner("dots", text="[bold white] El agente está razonando y ejecutando herramientas...[/bold white]", style="blue")
                )
                layout["body"].update(Panel(body_group, title="Estado de la Ejecución", border_style="green"))
                
                # LATERAL (DERECHA) - Logs con autoscroll (leemos el final del archivo)
                layout["side"].update(Panel(get_recent_logs(), title="Actividad Herramientas", border_style="magenta"))
                
                time.sleep(0.1)
    except KeyboardInterrupt:
        state.working = False

    # 5. Resultado Final
    console.clear()
    console.print(Panel(f"[bold blue]PROMPT ORIGINAL:[/bold blue]\n{state.prompt}", border_style="blue"))
    console.print(Panel(state.result, title="[bold green]RESULTADO FINAL DEL ARQUITECTO[/bold green]", border_style="green"))