import os
from smolagents import LiteLLMModel, ToolCallingAgent

# Importar herramientas desde la carpeta tools
from tools import RepoMapTool, FileWriteTool, FileReadTool, TerminalTool

PROJECT_BASE = os.getcwd()
MODEL_ID = "qwen2.5-coder:7b-instruct-q4_K_M"
PROVIDER = "Ollama"

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

def run_agent_task(user_text: str) -> str:
    """
    Ejecuta una tarea del agente con el texto proporcionado por el usuario.
    
    Args:
        user_text (str): La tarea o instrucción para el agente
        
    Returns:
        str: La respuesta del agente
    """
    try:
        response = agent.run(f"{SYSTEM_PROMPT}\n\nTarea: {user_text}")
        return response
    except Exception as e:
        return f"❌ ERROR: {str(e)}"
