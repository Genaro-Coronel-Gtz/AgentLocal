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
