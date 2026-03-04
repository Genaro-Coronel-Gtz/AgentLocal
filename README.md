# Arquitecto Senior - Agente de Software Local

Un agente de IA basado en smolagents con interfaz TUI para automatizar tareas de desarrollo de software.

## 🚀 Características

- **Arquitectura Modular**: Código organizado en módulos separados (agent, tools, utils)
- **Selector de Modelos Dinámico**: Cambia modelos de Ollama en tiempo de ejecución (Ctrl+M)
- **Herramientas Integradas**: Mapeo de repositorio, lectura/escritura de archivos, ejecución de terminal
- **Interfaz TUI Moderna**: Terminal interactiva con Textual y diseño optimizado
- **Configuración por .env**: Variables de entorno externas para fácil configuración
- **Seguridad**: Restricciones de acceso solo al directorio del proyecto
- **Actualización en Tiempo Real**: El agente se actualiza inmediatamente al cambiar modelo

## 🏗️ Arquitectura del Proyecto

```
Agent/
├── agent.py              # Core del agente y configuración
├── tui.py                # Interfaz de usuario TUI
├── tools/                # Herramientas del agente
│   ├── __init__.py       # Exportaciones de herramientas
│   ├── repo_map_tool.py  # Mapeo de repositorio
│   ├── file_write_tool.py # Escritura de archivos
│   ├── file_read_tool.py  # Lectura de archivos
│   ├── terminal_tool.py   # Ejecución en terminal
│   └── utils/             # Utilidades compartidas
│       ├── __init__.py    # Exportaciones de utilidades
│       └── common.py      # Funciones comunes
├── .env                  # Variables de entorno (no versionado)
├── .env.example          # Ejemplo de configuración
├── requirements.txt      # Dependencias Python
└── README.md            # Este archivo
```

### 📦 Módulos Principales

#### **agent.py** - Core del Agente
- Configuración desde variables de entorno (`.env`)
- Inicialización del agente smolagents
- Funciones de actualización de modelos
- Gestión de modelos disponibles de Ollama

#### **tui.py** - Interfaz de Usuario
- Interfaz TUI con Textual
- Selector de modelos dinámico (Ctrl+M)
- Gestión de chat y logs
- Diseño responsive y moderno

#### **tools/** - Herramientas del Agente
- **repo_map_tool.py**: Mapeo y análisis de repositorios
- **file_write_tool.py**: Escritura y creación de archivos
- **file_read_tool.py**: Lectura de archivos
- **terminal_tool.py**: Ejecución de comandos

#### **tools/utils/** - Utilidades Compartidas
- Funciones reutilizables entre herramientas
- Gestión de logs y paths seguros
- Evita duplicación de código

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

El proyecto utiliza un sistema de configuración basado en variables de entorno para máxima flexibilidad:

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env según tus necesidades
nano .env  # o tu editor preferido
```

#### Variables de Configuración (.env)

```bash
# Configuración del Agente
MODEL_ID=qwen2.5-coder:7b-instruct-q4_K_M
PROVIDER=Ollama
API_BASE=http://localhost:11434
MAX_STEPS=30

# System Prompt del Agente (formato de una sola línea)
SYSTEM_PROMPT="ERES UN AGENTE DE ACCIÓN LOCAL, Arquitecto de Software Senior.\n\nTRABAJO LOCAL: Estás limitado exclusivamente a la carpeta: {PROJECT_BASE}\n..."
```

#### 🔧 Configuración Modular

- **agent.py**: Lee todas las configuraciones desde `.env` usando `python-dotenv`
- **Separación de responsabilidades**: La lógica del agente está separada de la interfaz
- **Configuración externa**: No hay valores hardcodeados en el código
- **Cambios en tiempo real**: El selector de modelos cambia la configuración durante la ejecución

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

### Iniciar la Aplicación

```bash
# Asegúrate de que el entorno virtual esté activado
python tui.py
```

### Interfaz Principal

La aplicación muestra una interfaz TUI moderna con:

- **Header**: Muestra "AgentScripting", el modelo actual y acceso rápido al selector
- **Chat**: Área principal para interactuar con el agente
- **Logs**: Panel derecho con logs de auditoría en tiempo real
- **Input**: Campo para escribir tareas

### Selector de Modelos Dinámico

Cambia modelos de Ollama en tiempo de ejecución:

1. **Presiona Ctrl+M**: Abre el menú de selección de modelos
2. **Navega**: Usa las flechas ↑↓ para moverte entre modelos
3. **Selecciona**: Presiona Enter para confirmar o Esc para cancelar
4. **Actualización**: El agente se actualiza inmediatamente

**Características**:
- **Lista automática**: Obtiene modelos disponibles con `ollama list`
- **Actualización en tiempo real**: El modelo cambia sin reiniciar
- **Interfaz integrada**: Selector nativo de Textual
- **Confirmación visual**: Notificación y actualización del header

### Uso del Agente

1. **Escribe tu tarea** en el campo de entrada
2. **Presiona Enter** para ejecutar
3. **Observa los resultados** en el área de chat
4. **Revisa los logs** de auditoría en el panel derecho

### O Usar el Agente Directamente

```python
from agent import run_agent_task

# Ejecutar una tarea
result = run_agent_task("Crea un archivo README.md para este proyecto")
print(result)
```

## 🔧 Herramientas del Agente

El agente incluye herramientas modulares:

1. **repo_mapper**: Mapea y analiza la estructura del repositorio
2. **file_writer**: Crea y modifica archivos
3. **file_reader**: Lee archivos del proyecto
4. **terminal**: Ejecuta comandos del sistema

### Arquitectura Modular

- **Separación de responsabilidades**: Cada herramienta en su propio archivo
- **Utilidades compartidas**: Funciones comunes en `tools/utils/`
- **Configuración externa**: Todas las variables en `.env`
- **Core independiente**: Lógica del agente separada de la interfaz

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
