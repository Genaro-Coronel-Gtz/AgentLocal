import subprocess
from smolagents import Tool
from .utils import write_log, PROJECT_BASE

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
