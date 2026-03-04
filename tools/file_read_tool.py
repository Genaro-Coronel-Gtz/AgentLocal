import os
from smolagents import Tool
from .utils import write_log, safe_path

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
