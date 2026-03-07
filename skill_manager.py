import os
import json
import asyncio
from typing import List, Dict, Any, Optional
import lancedb
import numpy as np
import requests

class SkillManager:
    """Gestor de habilidades usando LanceDB para búsqueda vectorial"""
    
    def __init__(self, db_path: str = "skills_db"):
        self.db_path = db_path
        self.db = None
        self.table = None
        self.embeddings_url = "http://localhost:11434/api/embeddings"
        self.embedding_model = "nomic-embed-text"
        
    def _init_db(self):
        """Inicializa la base de datos si no existe"""
        try:
            print("🔍 _init_db: Iniciando inicialización...")
            
            if self.db is None:
                print("📊 _init_db: Conectando a LanceDB...")
                self.db = lancedb.connect(self.db_path)
                print(f"✅ _init_db: Conectado a {self.db_path}")
            else:
                print("✅ _init_db: DB ya estaba inicializada")
            
            # Verificar tablas existentes
            table_names = self.db.table_names()
            print(f"📋 _init_db: Tablas existentes: {table_names}")
            
            # Crear tabla si no existe
            if "skills" not in self.db.table_names():
                print("🔧 _init_db: Creando tabla 'skills'...")
                import pyarrow as pa
                schema = pa.schema([
                    pa.field("vector", pa.list_(pa.float32(), 768)),
                    pa.field("text", pa.string()),
                    pa.field("skill_id", pa.string()),
                    pa.field("enabled", pa.bool_()),
                    pa.field("metadata", pa.string())
                ])
                print("✅ _init_db: Schema creado con PyArrow")
                
                self.table = self.db.create_table("skills", schema=schema)
                print("✅ _init_db: Tabla 'skills' creada exitosamente")
            else:
                print("📊 _init_db: Abriendo tabla 'skills' existente...")
                self.table = self.db.open_table("skills")
                print("✅ _init_db: Tabla 'skills' abierta")
                
                # Verificar cuántos registros hay
                try:
                    count = len(self.table.to_pandas())
                    print(f"📈 _init_db: La tabla tiene {count} registros")
                except Exception as e:
                    print(f"⚠️ _init_db: No se pudo contar registros: {e}")
            
        except Exception as e:
            print(f"❌ _init_db: Error en inicialización: {e}")
            import traceback
            traceback.print_exc()
            self.table = None
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Genera embedding usando Ollama API"""
        try:
            response = requests.post(
                self.embeddings_url,
                json={
                    "model": self.embedding_model,
                    "prompt": text
                }
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"Error generando embedding: {e}")
            return []
    
    def _read_markdown_file(self, file_path: str) -> str:
        """Lee el contenido de un archivo markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error leyendo archivo {file_path}: {e}")
            return ""
    
    def ingest_skill(self, file_path: str, skill_name: str):
        """Ingesta una skill desde un archivo markdown"""
        try:
            self._init_db()
            
            # Leer archivo markdown
            content = self._read_markdown_file(file_path)
            if not content:
                return {"success": False, "error": "No se pudo leer el archivo"}
            
            # Dividir contenido en chunks para embeddings
            chunks = self._split_text_into_chunks(content)
            
            # Generar embeddings para cada chunk
            embeddings_data = []
            for i, chunk in enumerate(chunks):
                embedding = self._generate_embedding(chunk)
                if embedding:
                    embeddings_data.append({
                        "vector": embedding,
                        "text": chunk,
                        "skill_id": skill_name,
                        "enabled": True,  # Por defecto activada al ingestar
                        "metadata": json.dumps({
                            "file_path": file_path,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        })
                    })
            
            # Insertar en la base de datos
            if embeddings_data:
                self.table.add(embeddings_data)
                return {"success": True, "chunks_processed": len(embeddings_data)}
            else:
                return {"success": False, "error": "No se generaron embeddings"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 500) -> List[str]:
        """Divide el texto en chunks para procesamiento"""
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def search_skills(self, query: str, active_skills_ids: List[str]) -> List[Dict[str, Any]]:
        """Busca skills relevantes basadas en la query y skills activas"""
        try:
            self._init_db()
            
            # Generar embedding de la query
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                return []
            
            # Realizar búsqueda vectorial
            results = self.table.search(query_embedding).limit(10).to_pandas()
            
            # Filtrar por skills activas
            filtered_results = []
            for _, row in results.iterrows():
                if row['skill_id'] in active_skills_ids:
                    filtered_results.append({
                        "text": row['text'],
                        "skill_id": row['skill_id'],
                        "metadata": json.loads(row['metadata']),
                        "score": row.get('_distance', 0)
                    })
            
            return filtered_results
            
        except Exception as e:
            print(f"Error en búsqueda de skills: {e}")
            return []
    
    def get_available_skills(self) -> List[str]:
        """Obtiene lista de skills disponibles en la DB"""
        try:
            self._init_db()
            if self.table is None:
                print("❌ get_available_skills: La tabla es None")
                return []
            
            # Obtener skill_ids únicos
            print("🔍 get_available_skills: Obteniendo datos de la tabla...")
            results = self.table.to_pandas()
            print(f"📊 get_available_skills: {len(results)} registros encontrados")
            
            if len(results) == 0:
                print("❌ get_available_skills: No hay registros en la tabla")
                return []
            
            print(f"📋 get_available_skills: Columnas: {list(results.columns)}")
            
            if 'skill_id' not in results.columns:
                print("❌ get_available_skills: No existe la columna 'skill_id'")
                return []
            
            skills = list(results['skill_id'].unique())
            print(f"🎯 get_available_skills: Skills únicas: {skills}")
            
            return sorted(skills)
        except Exception as e:
            print(f"❌ Error obteniendo skills: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_enabled_skills(self) -> List[str]:
        """Obtiene lista de skills habilitadas (activas)"""
        try:
            self._init_db()
            if self.table is None:
                return []
            
            results = self.table.to_pandas()
            if len(results) == 0 or 'enabled' not in results.columns:
                return []
            
            # Filtrar skills habilitadas y obtener únicas
            enabled_skills = results[results['enabled'] == True]['skill_id'].unique().tolist()
            return sorted(enabled_skills)
            
        except Exception as e:
            print(f"❌ Error obteniendo skills habilitadas: {e}")
            return []
    
    def set_skill_enabled(self, skill_id: str, enabled: bool) -> bool:
        """Actualiza el estado enabled de una skill"""
        try:
            self._init_db()
            if self.table is None:
                return False
            
            # Actualizar todos los registros de esta skill
            df = self.table.to_pandas()
            mask = df['skill_id'] == skill_id
            if not mask.any():
                print(f"❌ No se encontró la skill '{skill_id}'")
                return False
            
            # Actualizar el campo enabled
            df.loc[mask, 'enabled'] = enabled
            
            # Reemplazar la tabla con los datos actualizados
            self.table.delete(where="true")  # Eliminar todos los registros
            self.table.add(df.to_dict('records'))  # Insertar los actualizados
            
            print(f"✅ Skill '{skill_id}' {'habilitada' if enabled else 'deshabilitada'}")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando estado de skill '{skill_id}': {e}")
            return False
    
    def is_skill_enabled(self, skill_id: str) -> bool:
        """Verifica si una skill está habilitada"""
        try:
            self._init_db()
            if self.table is None:
                return False
            
            df = self.table.to_pandas()
            skill_records = df[df['skill_id'] == skill_id]
            
            if skill_records.empty:
                return False
            
            # Si algún registro de esta skill está habilitado, considerarla habilitada
            return skill_records['enabled'].any()
            
        except Exception as e:
            print(f"❌ Error verificando estado de skill '{skill_id}': {e}")
            return False
