import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, RichLog, Label, LoadingIndicator, Select
from textual.containers import Container, VerticalScroll, Vertical, Horizontal
from textual import work
from textual.binding import Binding
from textual.screen import ModalScreen

# Importar el agente desde agent.py
from agent import agent, SYSTEM_PROMPT, PROJECT_BASE, MODEL_ID, PROVIDER, run_agent_task, update_agent_model, get_available_models

class ArquitectoApp(App):
    """
    Aplicación TUI para el Arquitecto Senior con selector de modelos
    """
    
    BINDINGS = [
        Binding("ctrl+m", "show_model_menu", "Modelos"),
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

    #chat_area { 
        height: 1fr; /* Ocupa todo el espacio disponible */
        border: tall #414868; 
        background: #1a1b26; 
        padding: 1; 
    }
    #chat_area.working { border: tall #bb9af7; }

    #log_area { 
        width: 35%; 
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
        margin: 1;
        border: double #bb9af7;
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
    """

    def compose(self) -> ComposeResult:
        # Obtener modelos disponibles
        models = get_available_models()
        
        # Crear header personalizado simple
        with Header(show_clock=True):
            with Horizontal(id="header-content"):
                with Vertical(id="title-section"):
                    yield Label("AgentScripting", id="app-title")
                    yield Label(f"Modelo: {MODEL_ID} | Ctrl+M: Cambiar", id="current-model")
        
        with Container(id="main_container"):
            with Vertical(id="chat_vertical"):
                with VerticalScroll(id="chat_area"):
                    yield Label("✨ Arquitecto Online. Esperando instrucciones...", id="welcome-text")
                with Static(id="loader-container"):
                    yield LoadingIndicator()
                    yield Label(" El Arquitecto está operando...", variant="title")
            yield RichLog(id="log_area", highlight=True, markup=True)
        yield Input(placeholder="> Describe la tarea...", id="user-input")
        yield Footer()

    def on_mount(self) -> None:
        self.current_model = MODEL_ID
        self.title = f"Arquitecto Senior M4 [{PROVIDER}]"
        self.sub_title = f"Modelo: {self.current_model} | 📂 {PROJECT_BASE}"
        self.set_interval(0.5, self.update_logs)
    
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
                    self.sub_title = f"Modelo: {self.current_model} | 📂 {PROJECT_BASE}"
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
            response = run_agent_task(user_text)
            self.call_from_thread(chat_area.mount, Label(f"🤖 ARQUITECTO:\n{response}", classes="agent-msg"))
        except Exception as e:
            self.call_from_thread(chat_area.mount, Label(f"❌ ERROR: {str(e)}", classes="agent-msg"))
        
        # UI: Desactivar Loader
        self.call_from_thread(chat_area.remove_class, "working")
        self.call_from_thread(loader.remove_class, "visible")
        self.call_from_thread(chat_area.scroll_end)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.process_task(event.value)
            event.input.value = ""

if __name__ == "__main__":
    if os.path.exists("agent_audit.log"): open("agent_audit.log", "w").close()
    ArquitectoApp().run()