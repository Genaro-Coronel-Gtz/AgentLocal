import os
import json
from typing import List, Dict, Any, Optional
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, RichLog, Label, LoadingIndicator, Select, SelectionList, TextArea, Button
from textual.widgets._selection_list import Selection
from textual.containers import Container, VerticalScroll, Vertical, Horizontal
from textual import work
from textual.binding import Binding
from textual.screen import ModalScreen

# Importar el agente desde agent.py
from agent import agent, SYSTEM_PROMPT, PROJECT_BASE, MODEL_ID, PROVIDER, run_agent_task, update_agent_model, get_available_models, reload_agent_tools
# Importar el SkillManager
from skill_manager import SkillManager

def load_tools_config():
    """Carga la configuración de herramientas desde el archivo JSON"""
    try:
        with open("tools_config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Configuración por defecto si no existe el archivo
        return {
            "tools": {
                "RepoMapTool": {
                    "name": "Mapeador de Repositorio",
                    "description": "Analiza y mapea la estructura del proyecto",
                    "enabled": True,
                    "file": "repo_map_tool.py"
                },
                "FileWriteTool": {
                    "name": "Escritor de Archivos", 
                    "description": "Crea y modifica archivos del proyecto",
                    "enabled": True,
                    "file": "file_write_tool.py"
                },
                "FileReadTool": {
                    "name": "Lector de Archivos",
                    "description": "Lee archivos del proyecto", 
                    "enabled": True,
                    "file": "file_read_tool.py"
                },
                "TerminalTool": {
                    "name": "Terminal",
                    "description": "Ejecuta comandos del sistema",
                    "enabled": True,
                    "file": "terminal_tool.py"
                }
            }
        }

def save_tools_config(config):
    """Guarda la configuración de herramientas al archivo JSON"""
    try:
        with open("tools_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        return False

class ArquitectoApp(App):
    """
    Aplicación TUI para el Arquitecto Senior con selector de modelos
    """
    
    BINDINGS = [
        Binding("ctrl+m", "show_model_menu", "Modelos"),
        Binding("ctrl+t", "show_tools_menu", "Herramientas"),
        Binding("a", "add_skill", "Agregar Skill"),
        Binding("ctrl+q", "quit", "Salir"),
    ]
    
    CSS = """
    Screen { background: #1a1b26; }
    
    #main_container { layout: horizontal; height: 1fr; }
    
    /* Contenedor de la izquierda (Chat + Loader) */
    #left_pane {
        width: 65%;
        height: 1fr;
        layout: vertical;
    }

    /* Contenedor de la derecha (Skills + Log) */
    #right_pane {
        width: 35%;
        height: 1fr;
        layout: vertical;
    }

    #chat_area { 
        height: 1fr; /* Ocupa todo el espacio disponible */
        border: tall #414868; 
        background: #1a1b26; 
        padding: 1; 
    }
    #chat_area.working { border: tall #bb9af7; }

    /* Panel de Skills */
    #skills-panel {
        height: 40%;
        border: tall #414868;
        background: #1f2335;
        padding: 1;
        margin-bottom: 1;
    }

    #skills-title {
        text-align: center;
        color: #7aa2f7;
        text-style: bold;
        margin-bottom: 1;
    }

    #skills-selection-list {
        height: 1fr;
        margin: 1 0;
        border: solid #414868;
    }

    #skills-selection-list > .selection-list--option {
        padding: 1;
        margin: 0 0;
        background: #1f2335;
        color: #9ece6a;
    }

    #skills-selection-list > .selection-list--option:hover {
        background: #24283b;
        color: #e0af68;
    }

    #skills-selection-list > .selection-list--option.selected {
        background: #7aa2f7;
        color: #1a1b26;
    }

    #refresh-skills-btn {
        margin-top: 1;
        background: #414868;
        color: #7aa2f7;
    }

    #refresh-skills-btn:hover {
        background: #7aa2f7;
        color: #1a1b26;
    }

    #log_area { 
        height: 60%;
        border: tall #414868; 
        background: #16161e; 
        color: #7aa2f7; 
    }
    
    .user-msg { color: #9ece6a; margin: 1 0; text-style: bold; border-bottom: dashed #2e3c64; }
    .agent-msg { color: #7dcfff; margin: 1 0; background: #24283b; padding: 1; border-left: solid #7dcfff; }
    
    #loader-container {
        height: auto;
        min-height: 3;
        background: #1f2335;
        border-top: solid #414868;
        display: none;
        padding: 0 1;
    }
    #loader-container.visible { display: block; layout: horizontal; }
    #loader-text { 
        margin-left: 2; 
        color: #e0af68; 
        content-align: left middle; /* Antes decía middle left, ahora está corregido */
        height: 3; 
    }

    /* Estilo para el TextArea de entrada mejorado */
    #user-input {
        dock: bottom;
        height: 5; 
        margin-top: 0;
        margin-bottom: 1;
        border: solid #bb9af7;
        background: #1a1b26;
        color: white;
    }
    
    /* Selector de modelos en el header */
    #model-selector {
        width: 50;
        margin: 0;
        height: 2;
    }
    
    #current-model {
        margin-right: 1;
    }
    #model-selector > .select {
        background: #1f2335;
        border: solid #7aa2f7;
        color: #7aa2f7;
    }
    
    #model-selector > .select:focus {
        border: thick #bb9af7;
        background: #24283b;
        color: #e0af68;
    }
    
    #model-selector > .select--open {
        background: #24283b;
        border: thick #bb9af7;
    }
    
    #model-selector > .select--option {
        background: #1f2335;
        color: #7aa2f7;
    }
    
    #model-selector > .select--option:hover {
        background: #24283b;
        color: #e0af68;
    }
    
    #model-selector > .select--option:focus {
        background: #7aa2f7;
        color: #1a1b26;
    }
    
    /* Header personalizado */
    Header {
        background: #24283b;
        color: #7aa2f7;
        text-align: center;
        height: 3;
    }
    
    #model-info {
        color: #e0af68;
        text-style: bold;
    }
    
    #header-content {
        height: 100%;
        layout: horizontal;
        align: center middle;
        padding: 0 1;
    }
    
    #title-section {
        width: 1fr;
        text-align: center;
    }
    
    #controls-section {
        width: auto;
        layout: horizontal;
        align: center middle;
    }
    
    /* Estilos para el modal de selección de modelo */
    #modal-content {
        width: 50;
        height: auto;
        background: #24283b;
        border: thick #7aa2f7;
        padding: 2;
        margin: 1 1;
    }
    
    #modal-title {
        text-align: center;
        color: #7aa2f7;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #modal-model-select {
        width: 100%;
        margin: 1 0;
    }
    
    #modal-help {
        color: #565f89;
        text-style: italic;
        text-align: center;
        margin-top: 1;
    }
    
    /* Estilos para el menú de modelos tipo palette */
    #menu-content {
        width: 60;
        height: auto;
        background: #24283b;
        border: thick #7aa2f7;
        padding: 2;
        margin: 1 1;
    }
    
    #menu-title {
        text-align: center;
        color: #7aa2f7;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #model-select {
        width: 100%;
        margin: 1 0;
    }
    
    #menu-help {
        color: #565f89;
        text-style: italic;
        text-align: center;
        margin-top: 1;
    }
    
    /* Estilos para el menú de herramientas */
    #tools-menu-content {
        width: 80;
        height: auto;
        background: #24283b;
        border: solid #414868;
        padding: 2;
        margin: 1 1;
    }
    
    #tools-menu-title {
        text-align: center;
        color: #7aa2f7;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #tools-selection-list {
        width: 100%;
        height: auto;
        margin: 1 0;
        border: solid #414868;
    }
    
    #tools-selection-list > .selection-list--option {
        padding: 1;
        margin: 0 0;
        background: #1f2335;
        color: #9ece6a;
    }
    
    #tools-selection-list > .selection-list--option:hover {
        background: #24283b;
        color: #e0af68;
    }
    
    #tools-selection-list > .selection-list--option.selected {
        background: #7aa2f7;
        color: #1a1b26;
    }
    
    #tools-menu-help {
        color: #565f89;
        text-style: italic;
        text-align: center;
        margin-top: 1;
    }
    
    /* Estilos para centrar el modal */
    ToolsMenu {
        align: center middle;
    }
    
    /* Estilos para centrar el modal de modelos */
    ModelMenu {
        align: center middle;
    }
    
    /* Estilos para centrar el modal de agregar skill */
    AddSkillModal {
        align: center middle;
    }
    
    #add-skill-content {
        width: 60;
        height: auto;
        background: #24283b;
        border: solid #414868;
        padding: 2;
        margin: 1 1;
    }
    
    #add-skill-title {
        text-align: center;
        color: #7aa2f7;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #skill-name-input, #skill-path-input {
        margin: 1 0;
        border: solid #414868;
        background: #1f2335;
        color: white;
    }
    
    #save-skill-btn {
        margin: 1 0;
        background: #7aa2f7;
        color: #1a1b26;
        text-style: bold;
    }
    
    #save-skill-btn:hover {
        background: #bb9af7;
        color: #1a1b26;
    }
    
    #add-skill-help {
        color: #565f89;
        text-style: italic;
        text-align: center;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        # Obtener modelos disponibles
        models = get_available_models()
        
        # Crear header personalizado simple
        with Header(show_clock=True):
            with Horizontal(id="header-content"):
                with Vertical(id="title-section"):
                    yield Label("AgentScripting", id="app-title")
                    yield Label(f"Modelo: {MODEL_ID} | Ctrl+M: Modelos | Ctrl+T: Herramientas | A: Agregar Skill", id="current-model")
        
        with Container(id="main_container"):
            with Vertical(id="chat_vertical"):
                with VerticalScroll(id="chat_area"):
                    yield Label("✨ Arquitecto Online. Esperando instrucciones...", id="welcome-text")
                with Static(id="loader-container"):
                    yield LoadingIndicator()
                    yield Label(" El Arquitecto está operando...", variant="title")
            with Vertical(id="right_pane"):
                # Panel de Skills
                with Vertical(id="skills-panel"):
                    yield Label("🧠 Skills Activas", id="skills-title")
                    yield SelectionList(id="skills-selection-list")
                    yield Button("Actualizar Skills", id="refresh-skills-btn")
                # RichLog
                yield RichLog(id="log_area", highlight=True, markup=True)
        yield TextArea(placeholder="> Describe la tarea...", id="user-input")
        yield Footer()

    def on_mount(self) -> None:
        self.current_model = MODEL_ID
        self.title = f"Arquitecto Senior M4 [{PROVIDER}]"
        self.sub_title = f"Modelo: {self.current_model} | 📂 {PROJECT_BASE} | 🔧 Ctrl+T: Herramientas"
        self.set_interval(0.5, self.update_logs)
        
        # Inicializar SkillManager
        self.skill_manager = SkillManager()
        self.active_skills = []
        
        self.notify("🚀 Aplicación iniciada", severity="information")
        self.notify("🔧 Inicializando SkillManager...", severity="information")
        
        # Cargar skills disponibles inicialmente
        self.set_timer(1.0, self.refresh_skills_list)
        self.notify("⏰ Timer configurado para actualizar skills en 1 segundo", severity="information")
    
    def action_show_model_menu(self) -> None:
        """Muestra el menú de selección de modelos tipo palette"""
        models = get_available_models()
        if not models:
            self.notify("No se encontraron modelos de Ollama", severity="error")
            return
        
        def on_model_selected(selected_model: str | None) -> None:
            if selected_model and selected_model != self.current_model:
                if update_agent_model(selected_model):
                    self.current_model = selected_model
                    self.sub_title = f"Modelo: {self.current_model} | 📂 {PROJECT_BASE} | 🔧 Ctrl+T: Herramientas"
                    # Actualizar etiqueta del modelo en el header
                    try:
                        model_label = self.query_one("#current-model")
                        model_label.update(f"Modelo: {self.current_model} | Ctrl+M: Cambiar")
                    except:
                        pass
                    self.notify(f"Modelo cambiado a: {selected_model}", severity="information")
                else:
                    self.notify(f"Error al cambiar al modelo: {selected_model}", severity="error")
        
        class ModelMenu(ModalScreen):
            BINDINGS = [
                Binding("escape", "dismiss", "Cancelar"),
            ]
            
            def __init__(self, current_model: str, models: list, callback):
                super().__init__()
                self.current_model = current_model
                self.models = models
                self._callback = callback
                self._initialized = False
                self._last_value = current_model
            
            def compose(self) -> ComposeResult:
                with Vertical(id="menu-content"):
                    yield Label("🔄 Seleccionar Modelo", id="menu-title")
                    yield Select(
                        [(f"🤖 {model}", model) for model in self.models],
                        value=self.current_model,
                        id="model-select"
                    )
                    yield Label("↑↓: Navegar | Enter: Seleccionar | Esc: Cancelar", id="menu-help")
            
            def on_mount(self) -> None:
                """Enfocar el selector al montar"""
                self.query_one("#model-select").focus()
                self._initialized = True
            
            def on_select_changed(self, event: Select.Changed) -> None:
                """Maneja el cambio de selección"""
                if not self._initialized:
                    # Ignorar el evento de inicialización
                    return
                
                if event.select.id == "model-select":
                    new_value = event.value
                    
                    # Solo cerrar si el valor realmente cambió
                    if new_value != self._last_value:
                        self._last_value = new_value
                        # Pequeño delay para asegurar que el usuario vea la selección
                        self.set_timer(0.2, lambda: self._close_and_callback(new_value))
            
            def _close_and_callback(self, selected_model: str) -> None:
                """Cierra el modal y ejecuta el callback"""
                try:
                    self.app.pop_screen()
                    if self._callback:
                        self._callback(selected_model)
                except Exception as e:
                    self.dismiss(None)
        
        self.push_screen(ModelMenu(self.current_model, models, on_model_selected))

    def update_logs(self):
        if os.path.exists("agent_audit.log"):
            with open("agent_audit.log", "r") as f:
                lines = f.readlines()
                self.query_one("#log_area").clear()
                self.query_one("#log_area").write("".join(lines[-30:]))

    def action_show_tools_menu(self) -> None:
        """Muestra el menú de configuración de herramientas"""
        config = load_tools_config()
        tools_config = config.get("tools", {})
        
        def on_tools_selected(selected_tools: list[str]) -> None:
            """Callback cuando se seleccionan herramientas"""
            # Actualizar el estado de las herramientas
            for tool_id, tool_info in tools_config.items():
                tool_info["enabled"] = tool_id in selected_tools
            
            # Guardar la configuración
            if save_tools_config(config):
                # Contar cuántas herramientas están habilitadas
                enabled_count = len(selected_tools)
                total_count = len(tools_config)
                
                # Recargar las herramientas del agente
                if reload_agent_tools():
                    self.notify(f"Herramientas actualizadas: {enabled_count}/{total_count} habilitadas", severity="information")
                else:
                    self.notify("Error al recargar las herramientas del agente", severity="error")
            else:
                self.notify("Error al guardar configuración de herramientas", severity="error")
        
        class ToolsMenu(ModalScreen):
            BINDINGS = [
                Binding("escape", "dismiss", "Cancelar"),
            ]
            
            def __init__(self, tools_config: dict, callback):
                super().__init__()
                self.tools_config = tools_config
                self._callback = callback
                self._initialized = False
                self._last_selection = None
            
            def compose(self) -> ComposeResult:
                with Vertical(id="tools-menu-content"):
                    yield Label("🔧 Configuración de Herramientas", id="tools-menu-title")
                    
                    # Crear lista de opciones usando objetos Selection
                    options = [
                        Selection(f"🔧 {info['name']} - {info['description']}", tool_id)
                        for tool_id, info in self.tools_config.items()
                    ]
                    
                    # Crear SelectionList simple sin preselección
                    yield SelectionList(*options, id="tools-selection-list")
                    
                    yield Label("Espacio: Seleccionar/Deseleccionar | Enter: Guardar | Esc: Cancelar", id="tools-menu-help")
            
            def on_mount(self) -> None:
                """Enfocar la lista y preseleccionar herramientas habilitadas"""
                selection_list = self.query_one("#tools-selection-list")
                selection_list.focus()
                
                # Identificar herramientas habilitadas
                enabled_tool_ids = [
                    tool_id for tool_id, info in self.tools_config.items() 
                    if info.get("enabled", True)
                ]
                
                # Guardar la selección inicial
                self._last_selection = set(enabled_tool_ids)
                
                # Preseleccionar las herramientas habilitadas
                for tool_id in enabled_tool_ids:
                    try:
                        selection_list.select(tool_id)
                    except:
                        pass  # Ignorar errores si ya está seleccionada
                
                self._initialized = True
            
            def on_key(self, event) -> None:
                """Maneja eventos de teclado para capturar Enter"""
                if not self._initialized:
                    return
                
                if event.key == "enter":
                    # Prevenir el comportamiento por defecto del SelectionList
                    event.stop()
                    
                    # Capturar Enter y procesar la selección
                    try:
                        selection_list = self.query_one("#tools-selection-list")
                        selected_tools = list(selection_list.selected)
                        
                        # Procesar siempre que se presione Enter
                        current_selection = set(selected_tools)
                        self._last_selection = current_selection
                        
                        # Pequeño delay para asegurar que el usuario vea la selección
                        self.set_timer(0.2, lambda: self._close_and_callback(selected_tools))
                    except Exception as e:
                        self.notify(f"Error al guardar selección: {e}", severity="error")
                        self.dismiss(None)
                elif event.key == "escape":
                    event.stop()
                    self.dismiss(None)
            
            def _close_and_callback(self, selected_tools: list[str]) -> None:
                """Cierra el modal y ejecuta el callback"""
                try:
                    self.app.pop_screen()
                    if self._callback:
                        self._callback(selected_tools)
                except Exception as e:
                    self.dismiss(None)
        
        self.push_screen(ToolsMenu(tools_config, on_tools_selected))

    @work(exclusive=True, thread=True)
    def process_task(self, user_text: str) -> None:
        chat_area = self.query_one("#chat_area")
        loader = self.query_one("#loader-container")
        
        # UI: Activar Loader y cambiar bordes
        self.call_from_thread(chat_area.add_class, "working")
        self.call_from_thread(loader.add_class, "visible")
        self.call_from_thread(chat_area.mount, Label(f"➜ USUARIO: {user_text}", classes="user-msg"))
        self.call_from_thread(chat_area.scroll_end)

        try:
            # Obtener skills activas y contexto relevante
            active_skills_ids = self.get_active_skills_ids()
            skills_context = ""
            
            # Obtener skills habilitadas desde la base de datos
            enabled_skills = self.skill_manager.get_enabled_skills()
            
            if enabled_skills:
                skills_results = self.skill_manager.search_skills(user_text, enabled_skills)
                if skills_results:
                    skills_context = "\n[CONTEXTO DE SKILLS ACTIVAS]\n"
                    for result in skills_results[:3]:  # Limitar a los 3 más relevantes
                        skills_context += f"\nSkill: {result['skill_id']}\n{result['text']}\n"
                    skills_context += "\n"
            
            # Ejecutar el agente con contexto de skills
            response = run_agent_task(user_text, skills_context)
            self.call_from_thread(chat_area.mount, Label(f"🤖 ARQUITECTO:\n{response}", classes="agent-msg"))
        except Exception as e:
            self.call_from_thread(chat_area.mount, Label(f"❌ ERROR: {str(e)}", classes="agent-msg"))
        
        # UI: Desactivar Loader
        self.call_from_thread(chat_area.remove_class, "working")
        self.call_from_thread(loader.remove_class, "visible")
        self.call_from_thread(chat_area.scroll_end)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Maneja el cambio en el TextArea y detecta Enter para enviar"""
        # Si el evento contiene Enter y no está vacío, enviar el mensaje
        if "\n" in event.text_area.text and event.text_area.text.strip().replace("\n", "").strip():
            # Obtener el texto sin el Enter final
            user_text = event.text_area.text.strip().replace("\n", "").strip()
            if user_text:
                self.process_task(user_text)
                event.text_area.text = ""
    
    def action_add_skill(self) -> None:
        """Abre el modal para agregar una nueva skill"""
        class AddSkillModal(ModalScreen):
            BINDINGS = [
                Binding("escape", "dismiss", "Cancelar"),
            ]
            
            def compose(self) -> ComposeResult:
                with Vertical(id="add-skill-content"):
                    yield Label("🧠 Agregar Nueva Skill", id="add-skill-title")
                    yield Input(placeholder="Nombre de la Skill", id="skill-name-input")
                    yield Input(placeholder="Ruta del archivo .md", id="skill-path-input")
                    yield Button("Guardar Skill", id="save-skill-btn")
                    yield Label("Enter: Guardar | Esc: Cancelar", id="add-skill-help")
            
            def on_mount(self) -> None:
                self.query_one("#skill-name-input").focus()
                self._initialized = True
            
            def on_key(self, event) -> None:
                """Maneja eventos de teclado para capturar Enter"""
                if not self._initialized:
                    return
                
                if event.key == "enter":
                    event.stop()
                    self._save_skill()
                elif event.key == "escape":
                    event.stop()
                    self.dismiss(None)
            
            def on_button_pressed(self, event: Button.Pressed) -> None:
                """Maneja el botón de guardar"""
                if event.button.id == "save-skill-btn":
                    self._save_skill()
            
            def _save_skill(self) -> None:
                skill_name = self.query_one("#skill-name-input").value.strip()
                skill_path = self.query_one("#skill-path-input").value.strip()
                
                if not skill_name or not skill_path:
                    self.notify("Debe completar ambos campos", severity="error")
                    return
                
                # Convertir ruta relativa a absoluta
                if skill_path.startswith('/'):
                    # Ruta absoluta desde el proyecto
                    skill_path = os.path.join(os.getcwd(), skill_path.lstrip('/'))
                elif not skill_path.startswith('./'):
                    # Agregar ./ si no está presente
                    skill_path = os.path.join(os.getcwd(), skill_path)
                
                # Validar que el archivo existe
                if not os.path.exists(skill_path):
                    self.notify(f"El archivo {skill_path} no existe", severity="error")
                    return
                
                # Iniciar proceso de ingesta asíncrono desde el modal
                self._ingest_skill_async(skill_path, skill_name)
                self.notify(f"Procesando skill: {skill_name}", severity="information")
                self.dismiss(None)
            
            @work(exclusive=True, thread=True)
            def _ingest_skill_async(self, skill_path: str, skill_name: str) -> None:
                """Proceso asíncrono de ingesta de skill"""
                try:
                    result = self.app.skill_manager.ingest_skill(skill_path, skill_name)
                    if result.get("success"):
                        self.app.call_from_thread(
                            lambda: self.app.notify(
                                f"Skill '{skill_name}' procesada correctamente: {result.get('chunks_processed', 0)} chunks", 
                                severity="success"
                            )
                        )
                        # Actualizar lista de skills
                        self.app.call_from_thread(self.app.refresh_skills_list)
                    else:
                        self.app.call_from_thread(
                            lambda: self.app.notify(
                                f"Error procesando skill: {result.get('error', 'Error desconocido')}", 
                                severity="error"
                            )
                        )
                except Exception as e:
                    self.app.call_from_thread(
                        lambda: self.app.notify(
                            f"Error en ingesta de skill: {str(e)}", 
                            severity="error"
                        )
                    )
        
        self.push_screen(AddSkillModal())
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja eventos de botones"""
        if event.button.id == "refresh-skills-btn":
            self.refresh_skills_list()
    
    def refresh_skills_list(self) -> None:
        """Actualiza la lista de skills disponibles"""
        try:
            self.notify("🔄 Actualizando skills...", severity="information")
            
            skills = self.skill_manager.get_available_skills()
            self.notify(f"📊 Skills obtenidas: {skills}", severity="information")
            
            if not skills:
                self.notify("❌ No se encontraron skills", severity="warning")
                return
            
            # Crear nuevas opciones con indicador de estado
            options = []
            for skill in skills:
                is_enabled = self.skill_manager.is_skill_enabled(skill)
                icon = "✅" if is_enabled else "☑️"
                options.append(Selection(f"{icon} {skill}", skill))
            
            self.notify(f"🎯 Opciones creadas: {len(options)}", severity="information")
            
            # Obtener el SelectionList existente
            skills_list = self.query_one("#skills-selection-list")
            
            # Limpiar todas las opciones existentes
            skills_list.clear_options()
            self.notify("✅ Opciones existentes eliminadas", severity="information")
            
            # Agregar las nuevas opciones
            added_count = 0
            for option in options:
                try:
                    skills_list.add_option(option)
                    added_count += 1
                    self.notify(f"✅ Opción agregada: {option.prompt}", severity="information")
                except Exception as e:
                    self.notify(f"❌ Error agregando opción {option.prompt}: {e}", severity="error")
            
            self.notify(f"✅ {added_count} opciones agregadas", severity="success")
            self.notify("🔄 SelectionList actualizado", severity="success")
            
            # Restaurar selección de skills habilitadas (desde la DB)
            enabled_skills = self.skill_manager.get_enabled_skills()
            restored_count = 0
            for skill_id in enabled_skills:
                if skill_id in skills:
                    try:
                        skills_list.select(skill_id)
                        restored_count += 1
                        self.notify(f"✅ Skill habilitada restaurada: {skill_id}", severity="information")
                    except Exception as e:
                        self.notify(f"❌ Error restaurando skill {skill_id}: {e}", severity="error")
            
            self.notify(f"🎉 Skills actualizadas: {len(skills)} disponibles, {len(enabled_skills)} habilitadas", severity="success")
            
        except Exception as e:
            self.notify(f"❌ Error actualizando skills: {e}", severity="error")
            import traceback
            traceback.print_exc()
    
    def get_active_skills_ids(self) -> List[str]:
        """Obtiene los IDs de las skills activas seleccionadas"""
        try:
            skills_list = self.query_one("#skills-selection-list")
            return list(skills_list.selected)
        except:
            return []
    
    def on_selection_list_selected_changed(self, event: SelectionList.SelectedChanged) -> None:
        """Maneja cambios en la selección de skills"""
        try:
            skill_id = str(event.selection.value)
            is_selected = event.selection in event.selection_list.selected
            
            # Actualizar estado en la base de datos
            success = self.skill_manager.set_skill_enabled(skill_id, is_selected)
            
            if success:
                status = "habilitada" if is_selected else "deshabilitada"
                self.notify(f"✅ Skill '{skill_id}' {status}", severity="success")
                
                # Actualizar el icono en la lista
                self.refresh_skills_list()
            else:
                self.notify(f"❌ Error actualizando skill '{skill_id}'", severity="error")
                
        except Exception as e:
            self.notify(f"❌ Error manejando selección: {e}", severity="error")

if __name__ == "__main__":
    if os.path.exists("agent_audit.log"): open("agent_audit.log", "w").close()
    ArquitectoApp().run()