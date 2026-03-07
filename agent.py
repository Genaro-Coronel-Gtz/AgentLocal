import os
import json
from dotenv import load_dotenv
from smolagents import LiteLLMModel, ToolCallingAgent

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración desde variables de entorno
PROJECT_BASE = os.getcwd()
MODEL_ID = os.getenv("MODEL_ID", "qwen2.5-coder:7b-instruct-q4_K_M")
PROVIDER = os.getenv("PROVIDER", "Ollama")
API_BASE = os.getenv("API_BASE", "http://localhost:11434")
MAX_STEPS = int(os.getenv("MAX_STEPS", "30"))
SYSTEM_PROMPT_TEMPLATE = os.getenv("SYSTEM_PROMPT", "")

# Formatear el system prompt con el PROJECT_BASE
SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.format(PROJECT_BASE=PROJECT_BASE) if SYSTEM_PROMPT_TEMPLATE else ""

def load_enabled_tools():
    """Carga solo las herramientas habilitadas desde tools_config.json"""
    try:
        with open("tools_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        tools_config = config.get("tools", {})
        enabled_tools = []
        
        # Importar todas las herramientas disponibles
        from tools import RepoMapTool, FileWriteTool, FileReadTool, TerminalTool
        
        # Mapeo de herramientas a clases
        tool_classes = {
            "RepoMapTool": RepoMapTool,
            "FileWriteTool": FileWriteTool,
            "FileReadTool": FileReadTool,
            "TerminalTool": TerminalTool
        }
        
        # Cargar solo las herramientas habilitadas
        for tool_id, tool_info in tools_config.items():
            if tool_info.get("enabled", True) and tool_id in tool_classes:
                enabled_tools.append(tool_classes[tool_id]())
        
        return enabled_tools
        
    except FileNotFoundError:
        # Si no existe el archivo, cargar todas las herramientas por defecto
        from tools import RepoMapTool, FileWriteTool, FileReadTool, TerminalTool
        return [RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool()]
    except Exception as e:
        print(f"Error cargando herramientas: {e}")
        # En caso de error, cargar todas las herramientas
        from tools import RepoMapTool, FileWriteTool, FileReadTool, TerminalTool
        return [RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool()]

# --- AGENTE ---
agent = ToolCallingAgent(
    tools=load_enabled_tools(),
    model=LiteLLMModel(model_id=f"ollama/{MODEL_ID}", api_base=API_BASE),
    add_base_tools=True,
    max_steps=MAX_STEPS
)

def update_agent_model(new_model_id: str) -> bool:
    """
    Actualiza el modelo del agente en tiempo de ejecución.
    
    Args:
        new_model_id (str): ID del nuevo modelo
        
    Returns:
        bool: True si se actualizó correctamente, False si hubo error
    """
    global agent, MODEL_ID
    try:
        MODEL_ID = new_model_id
        agent = ToolCallingAgent(
            tools=load_enabled_tools(),
            model=LiteLLMModel(model_id=f"ollama/{MODEL_ID}", api_base=API_BASE),
            add_base_tools=True,
            max_steps=MAX_STEPS
        )
        return True
    except Exception as e:
        print(f"Error actualizando modelo: {e}")
        return False

def get_available_models() -> list:
    """
    Obtiene la lista de modelos disponibles en Ollama.
    
    Returns:
        list: Lista de modelos disponibles
    """
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    # Extraer el nombre del modelo (primera columna)
                    model_name = line.split()[0]
                    models.append(model_name)
            return models
        else:
            return []
    except Exception as e:
        print(f"Error obteniendo modelos: {e}")
        return []

def reload_agent_tools() -> bool:
    """
    Recarga las herramientas del agente con la configuración actual.
    
    Returns:
        bool: True si se recargaron correctamente, False si hubo error
    """
    global agent
    try:
        agent = ToolCallingAgent(
            tools=load_enabled_tools(),
            model=LiteLLMModel(model_id=f"ollama/{MODEL_ID}", api_base=API_BASE),
            add_base_tools=True,
            max_steps=MAX_STEPS
        )
        return True
    except Exception as e:
        print(f"Error recargando herramientas: {e}")
        return False


def run_agent_task(user_text: str, skills_context: str = "") -> str:
    """
    Ejecuta una tarea del agente con el texto proporcionado por el usuario.
    
    Args:
        user_text (str): La tarea o instrucción para el agente
        skills_context (str): Contexto relevante de skills activas
        
    Returns:
        str: La respuesta del agente
    """
    try:
        # Construir el prompt con contexto de skills si está disponible
        full_prompt = f"{SYSTEM_PROMPT}"
        if skills_context:
            full_prompt += f"\n\n{skills_context}"
        full_prompt += f"\n\nTarea: {user_text}"
        
        response = agent.run(full_prompt)
        return response
    except Exception as e:
        return f"❌ ERROR: {str(e)}"
