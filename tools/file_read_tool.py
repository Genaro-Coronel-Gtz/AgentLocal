import os
from smolagents import Tool

PROJECT_BASE = os.getcwd()

def safe_path(path):
    if not path or path == "/": return PROJECT_BASE
    # Eliminamos cualquier intento de ruta absoluta que envíe el modelo para forzar relativa
    clean_path = path.replace(PROJECT_BASE, "").lstrip("/")
    full_path = os.path.abspath(os.path.join(PROJECT_BASE, clean_path))
    
    if not full_path.startswith(PROJECT_BASE):
        return PROJECT_BASE
    return full_path

def write_log(tool_name, inputs, output):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f" [{'='*10} {timestamp} {tool_name} {'='*10}]\n INPUTS: {inputs}\n OUTPUT: {output}\n\n"
    with open("agent_audit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

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
