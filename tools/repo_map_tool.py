import os
from smolagents import Tool
from .utils import write_log, safe_path

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
