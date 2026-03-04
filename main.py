import os
import subprocess
import datetime
from smolagents import CodeAgent, LiteLLMModel, Tool, ToolCallingAgent

def write_log(tool_name, inputs, output):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f" {'='*60}\n"
        f" [{timestamp}] TOOL: {tool_name}\n"
        f" INPUTS: {inputs}\n"
        f" OUTPUT: {output}\n"
        f" {'='*60}\n\n"
    )
    with open("agent_audit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

# --- 1. HERRAMIENTA: MAPA DEL PROYECTO ---
class RepoMapTool(Tool):
    name = "repo_mapper"
    description = "Muestra la estructura de carpetas. Úsalo SIEMPRE al inicio."
    inputs = {
        "root_dir": {"type": "string", "description": "Carpeta raíz", "nullable": True}
    }
    output_type = "string"

    def forward(self, root_dir: str = "."):
        target = root_dir if root_dir else "."
        exclude = {'.git', 'vendor', 'node_modules', 'storage', 'bootstrap/cache', '__pycache__'}
        tree = []
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in exclude]
            level = root.replace(target, '').count(os.sep)
            indent = ' ' * 4 * level
            tree.append(f"{indent}{os.path.basename(root)}/")
            valid_exts = ('.php', '.js', '.jsx', '.ts', '.tsx', '.rb', '.py', '.md', '.yml')
            for f in files:
                if f.endswith(valid_exts):
                    tree.append(f"{' ' * 4 * (level + 1)}{f}")
        return "\n".join(tree[:100])

# --- 2. HERRAMIENTA: LECTURA ---
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

# --- 3. HERRAMIENTA: ESCRITURA ---
class FileWriteTool(Tool):
    name = "file_writer"
    description = "Escribe código en un archivo. Crea carpetas automáticamente si es necesario."
    inputs = {
        "path": {"type": "string", "description": "Ruta donde guardar", "nullable": True},
        "content": {"type": "string", "description": "Código completo", "nullable": True}
    }
    output_type = "string"

    def forward(self, path: str = None, content: str = None):
        if not path or content is None: 
            return "❌ Error: Ruta o contenido faltantes."
        
        try:
            # Obtener el directorio. Si es 'archivo.py', dirname será ''
            directory = os.path.dirname(path)
            
            # Solo intentamos crear el directorio si no es la raíz
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            
            res = f"✅ Archivo guardado con éxito en: {path}"
            write_log(self.name, {"path": path}, "Escritura exitosa.")
            return res
        except Exception as e:
            error_msg = f"❌ Error escribiendo en {path}: {str(e)}"
            write_log(self.name, {"path": path}, error_msg)
            return error_msg

# --- 4. HERRAMIENTA: TERMINAL ---
class TerminalTool(Tool):
    name = "terminal"
    description = "Ejecuta comandos de consola."
    inputs = {
        "command": {"type": "string", "description": "Comando a ejecutar", "nullable": True}
    }
    output_type = "string"

    def forward(self, command: str = None): # Agregado = None
        if not command: return "❌ Error: No se proporcionó un comando."
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        except Exception as e:
            return f"❌ Error ejecutando comando: {str(e)}"

# --- CONFIGURACIÓN ---
model = LiteLLMModel(
    model_id="ollama/qwen2.5-coder:7b-instruct-q4_K_M", 
    api_base="http://localhost:11434"
)

# agent = CodeAgent(
#     tools=[RepoMapTool(), FileReadTool(), FileWriteTool(), TerminalTool()],
#     model=model,
#     add_base_tools=True
# )

agent = ToolCallingAgent(
    tools=[RepoMapTool(), FileReadTool(), FileWriteTool(), TerminalTool()],
    model=model,
    # additional_authorized_imports=[
    #     "os", "sys", "subprocess", "pathlib", "shutil", 
    #     "datetime", "json", "re", "posixpath", "ntpath" # <--- Importante
    # ],
    add_base_tools=True,
    max_steps=30
)

# SYSTEM_PROMPT = """
# Eres un Arquitecto Senior Local especializado en python.
# FLUJO: Mapear -> Leer -> Escribir -> Validar.
# Genera código profesional, limpio y con tipos estrictos.
# """

# SYSTEM_PROMPT = """
# Eres un AI Architect local. Tu stack es python3.
# REGLA DE ORO: Antes de crear cualquier archivo, usa 'repo_mapper' para entender dónde estás.
# Si el usuario pide algo Hexagonal en Laravel:
# 1. Mapea el proyecto.
# 2. Crea el Domain Port (Interface).
# 3. Crea el Application Service (Use Case).
# 4. Crea el Infrastructure Adapter.
# Usa PHP 8.3+ con tipos estrictos.
# """

# SYSTEM_PROMPT = """
# Eres un Agente de Ingeniería Autónomo. Tu objetivo es ENTREGAR SOLUCIONES FUNCIONALES, no solo texto.

# FLUJO OPERATIVO OBLIGATORIO:
# 1. EXPLORAR: Usa 'repo_mapper' para entender dónde estás trabajando.
# 2. PLANEAR: Decide qué archivos necesitas crear.
# 3. EJECUTAR: Usa 'file_writer' para crear el código.
# 4. VERIFICAR: Usa 'terminal' para ejecutar el código o instalar dependencias (ej: pip install yt-dlp).
# 5. CORREGIR: Si la terminal devuelve un error, lee el error, usa 'file_reader' si es necesario y vuelve a escribir el archivo con la corrección.

# No te detengas hasta que el programa sea funcional.
# """

# SYSTEM_PROMPT = """
# Eres un Agente de Ingeniería de Software de Clase Mundial. Tu objetivo es ENTREGAR SOLUCIONES FUNCIONALES en el sistema de archivos.

# REGLAS DE ORO PARA EVITAR ERRORES TÉCNICOS:
# 1. NO intentes importar librerías como 'os', 'pathlib' o 'posixpath' en tu código de razonamiento. 
# 2. DELEGA toda la lógica de archivos a las herramientas: 'file_writer' ya se encarga de crear carpetas, no necesitas verificar si existen.
# 3. RUTAS ABSOLUTAS/RELATIVAS: Siempre proporciona rutas de archivos completas y claras. NUNCA pases una cadena vacía o una variable sin definir a 'file_writer'.
# 4. LIBRERÍAS EXTERNAS: Si necesitas una librería (Python, PHP, JS), NO la importes en tu código de pensamiento. Usa la herramienta 'terminal' para instalarla (pip install, composer require, npm install) y luego escribe el código que la usa en un archivo físico.

# FLUJO OPERATIVO OBLIGATORIO:
# 1. EXPLORAR: Usa 'repo_mapper' para reconocer el terreno.
# 2. PLANEAR: Esboza la arquitectura (Laravel Hexagonal, React Components, etc.).
# 3. EJECUTAR: Escribe los archivos necesarios usando 'file_writer'.
# 4. INSTALAR Y PROBAR: Usa 'terminal' para instalar dependencias y ejecutar el código.
# 5. AUTOCORRECCIÓN: Si 'terminal' devuelve un error, lee el archivo con 'file_reader', analiza y corrige.

# Tu prioridad es que el código funcione en la máquina del usuario.
# """

SYSTEM_PROMPT = """
Eres un Agente de Ingeniería Senior. 

¡ALERTA DE SEGURIDAD E INTERPÉTRE!:
1. NO intentes usar 'os.makedirs', 'os.path.join' o 'os.mkdir' en tu bloque de código de pensamiento. El intérprete te bloqueará y fallarás.
2. USA EXCLUSIVAMENTE la herramienta 'file_writer'. Esta herramienta YA INCLUYE la lógica para crear carpetas automáticamente.
3. EJEMPLO DE USO CORRECTO:
   No hagas esto: 'os.mkdir("api"); open("api/main.py", "w")...'
   Haz esto: 'file_writer(path="api/main.py", content="...")'

FLUJO: Mapear -> Planear -> Escribir (con file_writer) -> Probar (con terminal).
"""

if __name__ == "__main__":
    task = input("🤖 ¿En qué trabajamos hoy?: ")
    agent.run(f"{SYSTEM_PROMPT}\n\nTarea: {task}")