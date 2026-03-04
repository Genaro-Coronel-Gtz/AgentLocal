# Arquitecto Senior - Agente de Software Local

Un agente de IA basado en smolagents con interfaz TUI para automatizar tareas de desarrollo de software.

## 🚀 Características

- **Agente Inteligente**: Basado en modelos de lenguaje locales (Ollama)
- **Herramientas Integradas**: Mapeo de repositorio, lectura/escritura de archivos, ejecución de terminal
- **Interfaz TUI**: Terminal interactiva con Textual
- **Configuración Flexible**: Variables de entorno mediante `.env`
- **Seguridad**: Restricciones de acceso solo al directorio del proyecto

## 📋 Requisitos Previos

- Python 3.8+
- Ollama instalado y corriendo
- Modelo descargado: `qwen2.5-coder:7b-instruct-q4_K_M`

## 🛠️ Instalación

### 1. Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Agent
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv agent-venv

# Activar entorno virtual
# En macOS/Linux:
source agent-venv/bin/activate
# En Windows:
agent-venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env según tus necesidades
nano .env  # o tu editor preferido
```

**Importante**: El archivo `.env` usa formato de una sola línea para el `SYSTEM_PROMPT` para ser compatible con `python-dotenv`. No uses comillas triples o múltiples líneas.

### 5. Iniciar Ollama

```bash
# Iniciar Ollama (si no está corriendo)
ollama serve

# Verificar que el modelo esté disponible
ollama list
```

## ⚙️ Configuración

El archivo `.env` contiene las siguientes variables:

```bash
# Configuración del Agente
MODEL_ID=qwen2.5-coder:7b-instruct-q4_K_M
PROVIDER=Ollama
API_BASE=http://localhost:11434
MAX_STEPS=30

# System Prompt del Agente (puedes personalizarlo)
SYSTEM_PROMPT="..."
```

## 🏃‍♂️ Ejecución

### Iniciar la Aplicación

```bash
# Asegúrate de que el entorno virtual esté activado
python tui.py
```

### O Usar el Agente Directamente

```python
from agent import run_agent_task

# Ejecutar una tarea
result = run_agent_task("Crea un archivo README.md para este proyecto")
print(result)
```

## 📁 Estructura del Proyecto

```
Agent/
├── agent.py              # Lógica principal del agente
├── tui.py                # Interfaz de terminal
├── .env                  # Configuración local (ignorado por Git)
├── .env.example          # Plantilla de configuración
├── requirements.txt      # Dependencias de Python
├── README.md            # Este archivo
└── tools/               # Herramientas del agente
    ├── __init__.py
    ├── repo_map_tool.py
    ├── file_write_tool.py
    ├── file_read_tool.py
    ├── terminal_tool.py
    └── utils/
        ├── __init__.py
        └── common.py
```

## 🔧 Herramientas Disponibles

El agente cuenta con las siguientes herramientas:

1. **repo_mapper**: Muestra la estructura del proyecto
2. **file_reader**: Lee contenido de archivos
3. **file_writer**: Escribe o crea archivos
4. **terminal**: Ejecuta comandos en la terminal

## 📝 Uso de la Interfaz TUI

1. **Inicia la aplicación** con `python tui.py`
2. **Escribe tu tarea** en el campo de entrada
3. **Presiona Enter** para ejecutar la tarea
4. **Observa los resultados** en el área de chat
5. **Revisa los logs** en el panel derecho

## 🛡️ Seguridad

- El agente solo puede acceder a archivos dentro del directorio del proyecto
- Las rutas absolutas son automáticamente convertidas a relativas
- Se registran todas las acciones en `agent_audit.log`

## 🐛 Solución de Problemas

### Problemas Comunes

1. **ModuleNotFoundError: No module named 'smolagents'**
   ```bash
   # Asegúrate de estar en el entorno virtual
   source agent-venv/bin/activate
   pip install -r requirements.txt
   ```

2. **python-dotenv could not parse statement**
   ```bash
   # El archivo .env tiene un formato incorrecto
   # Asegúrate de que el SYSTEM_PROMPT esté en una sola línea
   # Si tienes problemas, copia nuevamente el archivo:
   cp .env.example .env
   ```

3. **Connection refused to Ollama**
   ```bash
   # Verifica que Ollama esté corriendo
   ollama serve
   ```

4. **Model not found**
   ```bash
   # Descarga el modelo
   ollama pull qwen2.5-coder:7b-instruct-q4_K_M
   ```

### Logs de Auditoría

Todas las acciones del agente se registran en `agent_audit.log`:

```bash
# Ver los últimos logs
tail -f agent_audit.log
```

## 🤝 Contribución

1. Fork del proyecto
2. Crear una rama: `git checkout -b feature/nueva-funcionalidad`
3. Realizar cambios y commits
4. Push a la rama
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 🆘 Soporte

Si encuentras algún problema o tienes sugerencias:

1. Revisa la sección de solución de problemas
2. Abre un issue en el repositorio
3. Revisa los logs en `agent_audit.log` para más detalles
