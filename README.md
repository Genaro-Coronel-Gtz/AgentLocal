# Arquitecto Senior - Agente de Software Local

Un agente de IA basado en smolagents con interfaz TUI para automatizar tareas de desarrollo de software.

## 🚀 Características

- **Arquitectura Modular**: Código organizado en módulos separados (agent, tools, utils)
- **Selector de Modelos Dinámico**: Cambia modelos de Ollama en tiempo de ejecución (Ctrl+M)
- **Gestión de Herramientas**: Selector de herramientas habilitadas/deshabilitadas (Ctrl+T)
- **Sistema de Skills**: VectorDB con búsqueda vectorial y embeddings (Tecla A)
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
├── skill_manager.py      # Gestor de VectorDB y embeddings
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
├── tools_config.json     # Configuración de herramientas habilitadas
├── requirements.txt      # Dependencias Python
├── SKILLS_README.md      # Documentación del sistema de Skills
└── README.md            # Este archivo
```

### 📦 Módulos Principales

#### **agent.py** - Core del Agente
- Configuración desde variables de entorno (`.env`)
- Inicialización del agente smolagents
- Funciones de actualización de modelos
- Gestión de modelos disponibles de Ollama
- Integración con contexto de skills

#### **tui.py** - Interfaz de Usuario
- Interfaz TUI con Textual
- Selector de modelos dinámico (Ctrl+M)
- Selector de herramientas (Ctrl+T)
- Panel de Skills (Tecla A)
- Gestión de chat y logs
- Diseño responsive y moderno

#### **skill_manager.py** - Sistema de Skills
- VectorDB con LanceDB
- Embeddings con Ollama (nomic-embed-text)
- Ingesta de archivos markdown
- Búsqueda vectorial filtrada
- Procesamiento asíncrono

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
- Modelo de embeddings: `nomic-embed-text`

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

### 5. Iniciar Ollama

```bash
# Iniciar Ollama (si no está corriendo)
ollama serve

# Verificar que los modelos estén disponibles
ollama list

# Descargar modelos si es necesario
ollama pull qwen2.5-coder:7b-instruct-q4_K_M
ollama pull nomic-embed-text
```

## ⚙️ Configuración

### Configuración del Agente

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

### Configuración de Herramientas

Las herramientas se configuran mediante el archivo `tools_config.json`:

```json
{
  "tools": {
    "RepoMapTool": {
      "name": "Mapeador de Repositorio",
      "description": "Analiza y mapea la estructura del proyecto",
      "enabled": true,
      "file": "repo_map_tool.py"
    },
    "FileWriteTool": {
      "name": "Escritor de Archivos",
      "description": "Crea y modifica archivos del proyecto",
      "enabled": true,
      "file": "file_write_tool.py"
    },
    "FileReadTool": {
      "name": "Lector de Archivos",
      "description": "Lee archivos del proyecto",
      "enabled": true,
      "file": "file_read_tool.py"
    },
    "TerminalTool": {
      "name": "Terminal",
      "description": "Ejecuta comandos del sistema",
      "enabled": false,
      "file": "terminal_tool.py"
    }
  }
}
```

## 🏃‍♂️ Ejecución

### Iniciar la Aplicación

```bash
# Asegúrate de que el entorno virtual esté activado
python tui.py
```

## 📝 Uso de la Interfaz TUI

### Interfaz Principal

La aplicación muestra una interfaz TUI moderna con:

- **Header**: Muestra "AgentScripting", el modelo actual y accesos rápidos
- **Chat**: Área principal para interactuar con el agente
- **Panel de Skills**: Selector de habilidades activas (derecha, arriba)
- **Logs**: Panel derecho con logs de auditoría en tiempo real (derecha, abajo)
- **Input**: Campo de texto mejorado con scroll horizontal

### Comandos y Atajos

| Comando | Tecla | Función |
|---------|-------|---------|
| **Selector de Modelos** | `Ctrl+M` | Cambiar modelo de Ollama en tiempo real |
| **Selector de Herramientas** | `Ctrl+T` | Habilitar/deshabilitar herramientas |
| **Agregar Skill** | `A` | Abrir modal para agregar nueva skill |
| **Salir** | `Ctrl+Q` | Cerrar la aplicación |

### Selector de Modelos Dinámico (Ctrl+M)

Cambia modelos de Ollama en tiempo de ejecución:

1. **Presiona Ctrl+M**: Abre el menú de selección de modelos
2. **Navega**: Usa las flechas ↑↓ para moverte entre modelos
3. **Selecciona**: Presiona Enter para confirmar o Esc para cancelar
4. **Actualización**: El agente se actualiza inmediatamente

**Características**:
- **Lista automática**: Obtiene modelos disponibles con `ollama list`
- **Actualización en tiempo real**: El modelo cambia sin reiniciar
- **Interfaz centrada**: Modal perfectamente centrado
- **Confirmación visual**: Notificación y actualización del header

### Selector de Herramientas (Ctrl+T)

Gestiona qué herramientas están disponibles para el agente:

1. **Presiona Ctrl+T**: Abre el menú de herramientas
2. **Visualiza estado**: ✅ para habilitadas, ❌ para deshabilitadas
3. **Navega**: Usa flechas ↑↓ para moverte
4. ** Alterna**: Presiona Espacio para cambiar estado
5. **Guarda**: Presiona Enter para aplicar cambios

**Características**:
- **Preselección automática**: Muestra estado actual del JSON
- **Toggle controlado**: Enter solo cierra y guarda
- **Persistencia**: Cambios guardados en `tools_config.json`
- **Recarga automática**: El agente se recarga con nuevas herramientas
- **Interfaz centrada**: Modal perfectamente centrado

### Sistema de Skills (Tecla A)

Gestiona habilidades personalizadas con búsqueda vectorial:

#### Agregar Nueva Skill

1. **Presiona A**: Abre el modal para agregar skill
2. **Nombre**: Ingresa un identificador único (ej: "python_basics")
3. **Ruta**: Especifica la ruta al archivo .md (ej: "./docs/python_basics.md")
4. **Procesamiento**: El sistema genera embeddings automáticamente
5. **Confirmación**: Notificación cuando se completa la ingesta

#### Panel de Skills

- **Lista de skills**: Muestra todas las skills disponibles en la VectorDB
- **Selección**: Marca/desmarca skills como activas
- **Botón actualizar**: Recarga la lista de skills disponibles
- **Contexto automático**: Skills activas inyectan contexto relevante

#### Búsqueda Vectorial

Cuando envías un mensaje:
1. **Identifica skills activas** seleccionadas
2. **Genera embedding** de tu consulta
3. **Busca contenido relevante** en la VectorDB
4. **Inyecta contexto** en el prompt del agente

**Ejemplo de uso**:
```markdown
# Archivo: python_basics.md
## Variables
Las variables en Python se declaran sin tipo:
```python
nombre = "Juan"
edad = 25
```
```

Al enviar: "¿Cómo declaro una variable en Python?"
El sistema buscará en las skills activas e inyectará el contexto relevante.

### Uso del Agente

1. **Escribe tu tarea** en el campo de entrada (con scroll horizontal)
2. **Presiona Enter** para ejecutar
3. **Observa los resultados** en el área de chat
4. **Revisa los logs** de auditoría en el panel derecho

### Campo de Entrada Mejorado

- **Doble altura**: Más espacio para escribir cómodamente
- **Scroll horizontal**: Textos largos continúan hacia la derecha
- **Bordes visibles**: Diseño optimizado con ancho apropiado
- **Enter funcional**: Envía mensajes sin problemas

## 🔧 Herramientas del Agente

El agente incluye herramientas modulares configurables:

1. **RepoMapTool**: Mapea y analiza la estructura del repositorio
2. **FileWriteTool**: Crea y modifica archivos
3. **FileReadTool**: Lee archivos del proyecto
4. **TerminalTool**: Ejecuta comandos del sistema

### Configuración de Herramientas

Las herramientas se gestionan mediante `tools_config.json`:

- **enabled: true**: Herramienta disponible para el agente
- **enabled: false**: Herramienta deshabilitada
- **Cambios dinámicos**: Se aplican sin reiniciar la aplicación

## 🧠 Sistema de Skills

### VectorDB con LanceDB

- **Almacenamiento vectorial**: Eficiente y escalable
- **Embeddings**: Ollama API con nomic-embed-text
- **Búsqueda semántica**: Encuentra contenido relevante
- **Filtrado**: Por skills activas seleccionadas

### Flujo de Trabajo

1. **Ingesta**: Archivos .md → Chunks → Embeddings → LanceDB
2. **Búsqueda**: Query del usuario → Embedding → Búsqueda vectorial → Contexto
3. **Ejecución**: Contexto + Prompt → Agente → Respuesta

### Archivos de Skills

Los archivos deben estar en formato markdown:

```markdown
# Nombre de la Skill

## Contenido
Descripción detallada con ejemplos de código.

### Ejemplos
```python
# Código de ejemplo
def ejemplo():
    return "Hola"
```
```

## 🛡️ Seguridad

- El agente solo puede acceder a archivos dentro del directorio del proyecto
- Las rutas absolutas son automáticamente convertidas a relativas
- Se registran todas las acciones en `agent_audit.log`
- Las herramientas se pueden deshabilitar para mayor control

## 🐛 Solución de Problemas

### Problemas Comunes

1. **ModuleNotFoundError: No module named 'smolagents'**
   ```bash
   # Asegúrate de estar en el entorno virtual
   source agent-venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Error de conexión con Ollama**
   ```bash
   # Verifica que Ollama esté corriendo
   ollama serve
   
   # Verifica modelos disponibles
   ollama list
   
   # Descarga modelos necesarios
   ollama pull qwen2.5-coder:7b-instruct-q4_K_M
   ollama pull nomic-embed-text
   ```

3. **Error al agregar Skill**
   - Verifica que el archivo .md exista
   - Confirma que Ollama esté corriendo
   - Revisa la ruta del archivo

4. **Problemas con el Selector**
   - **Modelos**: Verifica que `ollama list` funcione
   - **Herramientas**: Revisa el formato de `tools_config.json`
   - **Skills**: Asegúrate que LanceDB esté instalado

### Logs de Auditoría

Todas las acciones del agente se registran en `agent_audit.log`:

```bash
# Ver los últimos logs
tail -f agent_audit.log
```

### Base de Datos de Skills

La VectorDB se almacena en la carpeta `skills_db/`:

```bash
# Estructura de la DB
skills_db/
├── skills/
│   ├── data/
│   └── _versions/
└── lancedb.log
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
2. Consulta `SKILLS_README.md` para detalles del sistema de Skills
3. Abre un issue en el repositorio
4. Revisa los logs en `agent_audit.log` para más detalles

## 📚 Documentación Adicional

- **SKILLS_README.md**: Documentación completa del sistema de Skills
- **tools_config.json**: Configuración de herramientas
- **.env.example**: Plantilla de configuración del agente
