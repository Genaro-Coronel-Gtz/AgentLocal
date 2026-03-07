# Sistema de Skills con VectorDB

## 🧠 Descripción

Sistema completo de gestión de habilidades usando búsqueda vectorial con LanceDB y embeddings de Ollama.

## 🚀 Características

- **VectorDB**: LanceDB para almacenamiento y búsqueda vectorial
- **Embeddings**: Ollama API con modelo `nomic-embed-text`
- **Interfaz Textual**: Panel de skills con SelectionList
- **Integración**: Contexto inyectado automáticamente en el agente
- **Procesamiento asíncrono**: @work para no congelar la UI

## 📦 Instalación

```bash
pip install -r requirements.txt
```

## 🔧 Configuración

1. **Asegurar Ollama corriendo**:
```bash
ollama serve
```

2. **Instalar modelo de embeddings**:
```bash
ollama pull nomic-embed-text
```

## 🎮 Uso

### Interfaz de Usuario

- **Tecla `A`**: Abrir modal para agregar nueva skill
- **Panel Skills**: Seleccionar/deseleccionar skills activas
- **Botón "Actualizar Skills"**: Recargar lista de disponibles

### Agregar Skills

1. Presionar `A` para abrir el modal
2. Ingresar:
   - **Nombre de la Skill**: Identificador único
   - **Ruta del archivo .md**: Path al archivo markdown
3. El sistema procesa automáticamente:
   - Lee el archivo markdown
   - Genera embeddings
   - Almacena en LanceDB

### Búsqueda Vectorial

- Cuando se envía un mensaje, el sistema:
  1. Identifica skills activas seleccionadas
  2. Busca contenido relevante usando embeddings
  3. Inyecta el contexto en el prompt del agente

## 📁 Estructura de Archivos

```
Agent/
├── skill_manager.py      # Gestor de VectorDB y embeddings
├── tui.py               # Interfaz textual actualizada
├── agent.py             # Agente modificado para skills
├── requirements.txt     # Dependencias actualizadas
└── skills_db/          # Base de datos LanceDB (se crea automáticamente)
```

## 🔄 Flujo de Trabajo

1. **Ingesta**: Archivos .md → Chunks → Embeddings → LanceDB
2. **Búsqueda**: Query del usuario → Embedding → Búsqueda vectorial → Contexto
3. **Ejecución**: Contexto + Prompt → Agente → Respuesta

## 🎯 Ejemplos de Uso

### Archivo de Skill (ej: `python_basics.md`)
```markdown
# Python Básico

## Variables
Las variables en Python se declaran sin tipo:
```python
nombre = "Juan"
edad = 25
```

## Funciones
Definición de funciones básicas:
```python
def saludar(nombre):
    return f"Hola {nombre}"
```
```

### Uso en el Agente
Al enviar: "¿Cómo declaro una variable en Python?"

El sistema buscará en las skills activas y encontrará el contexto relevante, inyectándolo en el prompt.

## 🔧 Configuración Avanzada

### Modificar Chunk Size
En `skill_manager.py`:
```python
def _split_text_into_chunks(self, text: str, chunk_size: int = 500):
```

### Cambiar Modelo de Embeddings
En `skill_manager.py`:
```python
self.embedding_model = "nomic-embed-text"  # Cambiar aquí
```

### Ajustar Límite de Búsqueda
En `tui.py`:
```python
for result in skills_results[:3]:  # Cambiar el número
```

## 🐛 Troubleshooting

### Error: "No se encontraron modelos de Ollama"
```bash
ollama list
# Si no hay modelos:
ollama pull nomic-embed-text
```

### Error: "El archivo no existe"
- Verificar que la ruta al archivo .md sea correcta
- Usar rutas absolutas si es necesario

### Error de conexión con Ollama
```bash
# Verificar que Ollama esté corriendo
ps aux | grep ollama

# Reiniciar si es necesario
ollama serve
```

## 📊 Monitoreo

- **Logs**: Archivo `agent_audit.log`
- **Base de datos**: Carpeta `skills_db/`
- **Notificaciones**: En la interfaz textual

## 🚀 Extensiones Futuras

- [ ] Soporte para múltiples formatos (PDF, TXT)
- [ ] Edición de skills existentes
- [ ] Eliminación de skills
- [ ] Exportación/importación de skills
- [ ] Métricas de uso de skills

## 🤝 Contribuciones

1. Fork del proyecto
2. Crear feature branch
3. Pull request con descripción detallada

## 📄 Licencia

MIT License
