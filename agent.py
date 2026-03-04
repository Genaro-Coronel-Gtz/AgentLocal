import os
from dotenv import load_dotenv
from smolagents import LiteLLMModel, ToolCallingAgent

# Importar herramientas desde la carpeta tools
from tools import RepoMapTool, FileWriteTool, FileReadTool, TerminalTool

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

# --- AGENTE ---
agent = ToolCallingAgent(
    tools=[RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool()],
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
            tools=[RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool()],
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
