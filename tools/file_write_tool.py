import os
from smolagents import Tool
from .utils import write_log, safe_path

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
