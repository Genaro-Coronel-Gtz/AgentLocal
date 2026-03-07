#!/usr/bin/env python3
"""
Migración simple: eliminar y recrear la tabla con el schema correcto
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import lancedb
import shutil

def reset_database():
    """Elimina y recrea la base de datos con el schema correcto"""
    print("🔄 Reiniciando base de datos...")
    
    try:
        # Hacer backup
        if os.path.exists("skills_db"):
            print("💾 Creando backup...")
            shutil.copytree("skills_db", "skills_db_backup_old")
        
        # Eliminar base de datos existente
        if os.path.exists("skills_db"):
            print("🗑️ Eliminando base de datos existente...")
            shutil.rmtree("skills_db")
        
        print("✅ Base de datos eliminada")
        print("📝 Nota: La próxima vez que se ejecute la app, se creará con el schema correcto")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)
