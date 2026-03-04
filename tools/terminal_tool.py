import subprocess
import os
from smolagents import Tool

PROJECT_BASE = os.getcwd()

def write_log(tool_name, inputs, output):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f" [{'='*10} {timestamp} {tool_name} {'='*10}]\n INPUTS: {inputs}\n OUTPUT: {output}\n\n"
    with open("agent_audit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

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
