import os
import subprocess
import datetime
import io
import contextlib
from smolagents import LiteLLMModel, Tool, ToolCallingAgent

from rich.console import Console

# Definimos la base del proyecto (donde ejecutas el script)
PROJECT_BASE = os.getcwd()

def run_agent_silent(agent, prompt):
    # Creamos un "buffer" para capturar la basura de la librería
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        # Todo lo que pase aquí adentro no se verá en la terminal
        result = agent.run(prompt)
    return result

def write_log(tool_name, inputs, output):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f" [{'='*10} {timestamp} {tool_name} {'='*10}]\n INPUTS: {inputs}\n OUTPUT: {output}\n\n"
    with open("agent_audit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

def safe_path(path):
    """Evita que el agente escape de la carpeta del proyecto."""
    if not path or path == "/": return PROJECT_BASE
    # Unimos la base con la ruta sugerida y sacamos la ruta absoluta real
    full_path = os.path.abspath(os.path.join(PROJECT_BASE, path.lstrip("/")))
    # Si la ruta resultante no empieza con PROJECT_BASE, es un intento de hackeo/error
    if not full_path.startswith(PROJECT_BASE):
        return PROJECT_BASE
    return full_path

# --- HERRAMIENTAS BLINDADAS ---

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
    inputs = {
        "path": {"type": "string", "description": "Ruta relativa", "nullable": True},
        "content": {"type": "string", "description": "Contenido", "nullable": True}
    }
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
        except Exception as e:
            return f"❌ Error: {str(e)}"

# --- 2. HERRAMIENTA: LECTURA (AÑADIDA) ---
class FileReadTool(Tool):
    name = "file_reader"
    description = "Lee el contenido de un archivo."
    inputs = {
        "path": {"type": "string", "description": "Ruta del archivo", "nullable": True}
    }
    output_type = "string"

    def forward(self, path: str = None): # Agregado = None para coincidir con nullable: True
        if not path: return "❌ Error: Debes proporcionar una ruta."
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f"--- CONTENIDO DE {path} ---\n{f.read()}"
        except Exception as e:
            return f"❌ Error leyendo {path}: {str(e)}"

# --- 3. HERRAMIENTA: TERMINAL (AÑADIDA) ---
class TerminalTool(Tool):
    name = "terminal"
    description = "Ejecuta comandos DENTRO de la carpeta del proyecto."
    inputs = {"command": {"type": "string", "description": "Comando", "nullable": True}}
    output_type = "string"

    def forward(self, command: str = None):
        if not command: return "❌ No hay comando."
        # Forzamos a que el comando se ejecute siempre en PROJECT_BASE
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=PROJECT_BASE)
            write_log(self.name, command, "Ejecutado.")
            return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        except Exception as e:
            return str(e)

# --- CONFIGURACIÓN ---
model = LiteLLMModel(model_id="ollama/qwen2.5-coder:7b-instruct-q4_K_M", api_base="http://localhost:11434")

agent = ToolCallingAgent(
    tools=[RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool()], # Asegúrate de incluir FileReadTool aquí
    model=model,
    add_base_tools=True,
    max_steps=30
)


SYSTEM_PROMPT = f"""
Eres un Arquitecto de Software Senior. 

TRABAJO LOCAL: Estás limitado exclusivamente a la carpeta: {PROJECT_BASE}

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

if __name__ == "__main__":
    task = input("🤖 Tarea: ")
    
    print("\n🚀 El Arquitecto está trabajando en silencio...")
    
    # Ejecutamos con el silenciador
    respuesta = run_agent_silent(agent, f"{SYSTEM_PROMPT}\n\nTarea: {task}")
    
    print("\n✅ Tarea completada.")
    print("-" * 30)
    print(respuesta)
    print("-" * 30)