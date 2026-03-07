#!/usr/bin/env python3
"""
Script de depuración para verificar el estado de la base de datos de skills
"""

import os
import sys
import json

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from skill_manager import SkillManager
    import pandas as pd
    
    def debug_skills_db():
        """Depura la base de datos de skills"""
        print("🔍 Depurando Base de Datos de Skills")
        print("=" * 50)
        
        # Inicializar SkillManager
        skill_manager = SkillManager()
        
        try:
            # Inicializar DB
            skill_manager._init_db()
            
            if skill_manager.table is None:
                print("❌ La tabla de skills no existe")
                return
            
            # Obtener todos los datos
            print("📊 Obteniendo datos de la tabla...")
            df = skill_manager.table.to_pandas()
            
            print(f"📈 Total de registros: {len(df)}")
            
            if len(df) == 0:
                print("❌ No hay registros en la base de datos")
                return
            
            # Mostrar información básica
            print("\n📋 Información de la tabla:")
            print(f"   Columnas: {list(df.columns)}")
            print(f"   Tipos de datos:\n{df.dtypes}")
            
            # Mostrar skills únicos
            if 'skill_id' in df.columns:
                unique_skills = df['skill_id'].unique()
                print(f"\n🎯 Skills únicas encontradas: {len(unique_skills)}")
                for skill in sorted(unique_skills):
                    count = len(df[df['skill_id'] == skill])
                    print(f"   - {skill}: {count} chunks")
            
            # Mostrar primeros registros
            print(f"\n📄 Primeros 3 registros:")
            for i, row in df.head(3).iterrows():
                print(f"\n   Registro {i+1}:")
                print(f"   - Skill ID: {row.get('skill_id', 'N/A')}")
                print(f"   - Texto: {row.get('text', 'N/A')[:100]}...")
                if 'metadata' in row and row['metadata']:
                    try:
                        metadata = json.loads(row['metadata'])
                        print(f"   - Archivo: {metadata.get('file_path', 'N/A')}")
                        print(f"   - Chunk: {metadata.get('chunk_index', 'N/A')}/{metadata.get('total_chunks', 'N/A')}")
                    except:
                        print(f"   - Metadata: {row['metadata'][:50]}...")
            
            # Probar método get_available_skills
            print(f"\n🔧 Probando get_available_skills():")
            try:
                skills = skill_manager.get_available_skills()
                print(f"   Skills encontradas: {skills}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # Verificar estructura de la carpeta skills_db
            print(f"\n📁 Estructura de skills_db:")
            if os.path.exists("skills_db"):
                for root, dirs, files in os.walk("skills_db"):
                    level = root.replace("skills_db", "").count(os.sep)
                    indent = " " * 2 * level
                    print(f"{indent}{os.path.basename(root)}/")
                    subindent = " " * 2 * (level + 1)
                    for file in files:
                        print(f"{subindent}{file}")
            else:
                print("   ❌ La carpeta skills_db no existe")
            
        except Exception as e:
            print(f"❌ Error durante la depuración: {e}")
            import traceback
            traceback.print_exc()
    
    if __name__ == "__main__":
        debug_skills_db()
        
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de tener instaladas las dependencias:")
    print("pip install -r requirements.txt")
