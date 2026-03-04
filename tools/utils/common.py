import os
import datetime

PROJECT_BASE = os.getcwd()

def safe_path(path):
    """Función de seguridad para validar rutas dentro del proyecto"""
    if not path or path == "/": 
        return PROJECT_BASE
    # Eliminamos cualquier intento de ruta absoluta que envíe el modelo para forzar relativa
    clean_path = path.replace(PROJECT_BASE, "").lstrip("/")
    full_path = os.path.abspath(os.path.join(PROJECT_BASE, clean_path))
    
    if not full_path.startswith(PROJECT_BASE):
        return PROJECT_BASE
    return full_path

def write_log(tool_name, inputs, output):
    """Función para registrar auditoría de herramientas"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f" [{'='*10} {timestamp} {tool_name} {'='*10}]\n INPUTS: {inputs}\n OUTPUT: {output}\n\n"
    with open("agent_audit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)
