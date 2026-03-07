#!/usr/bin/env python3
"""
Migración para agregar el campo 'enabled' a la base de datos existente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from skill_manager import SkillManager
import pandas as pd
import shutil

def migrate_database():
    """Agrega el campo 'enabled' a todos los registros existentes"""
    print("🔄 Iniciando migración de la base de datos...")
    
    try:
        # Inicializar el SkillManager
        manager = SkillManager()
        
        # Hacer backup de la base de datos
        if os.path.exists("skills_db"):
            print("💾 Creando backup...")
            shutil.copytree("skills_db", "skills_db_backup")
            print("✅ Backup creado en skills_db_backup")
        
        # Exportar datos existentes
        print("📤 Exportando datos existentes...")
        manager._init_db()
        
        if manager.table is None:
            print("❌ No se pudo conectar a la base de datos")
            return False
        
        df = manager.table.to_pandas()
        print(f"📊 Registros encontrados: {len(df)}")
        
        if len(df) == 0:
            print("✅ La base de datos está vacía, no se necesita migración")
            return True
        
        # Guardar datos temporalmente
        temp_data = []
        for _, row in df.iterrows():
            temp_data.append({
                "vector": row['vector'],
                "text": row['text'],
                "skill_id": row['skill_id'],
                "enabled": True,  # Por defecto habilitado
                "metadata": row['metadata']
            })
        
        print(f"� {len(temp_data)} registros preparados")
        
        # Eliminar la tabla existente
        print("🗑️ Eliminando tabla antigua...")
        manager.db.drop_table("skills")
        
        # Crear nueva tabla con el schema actualizado
        print("🔧 Creando nueva tabla con schema actualizado...")
        manager._init_db()  # Esto creará la tabla con el nuevo schema
        
        # Insertar los datos con el nuevo campo
        print("📥 Importando datos a la nueva tabla...")
        manager.table.add(temp_data)
        
        print("✅ Migración completada exitosamente")
        print(f"📈 {len(temp_data)} registros migrados con enabled=True")
        
        # Verificar la migración
        df_new = manager.table.to_pandas()
        print(f"🔍 Verificación: {len(df_new)} registros en la nueva tabla")
        print(f"📋 Columnas: {list(df_new.columns)}")
        
        if 'enabled' in df_new.columns:
            enabled_count = df_new['enabled'].sum()
            print(f"✅ {enabled_count} registros con enabled=True")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        
        # Restaurar backup si falló
        if os.path.exists("skills_db_backup"):
            print("🔄 Restaurando backup...")
            if os.path.exists("skills_db"):
                shutil.rmtree("skills_db")
            shutil.move("skills_db_backup", "skills_db")
            print("✅ Backup restaurado")
        
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
