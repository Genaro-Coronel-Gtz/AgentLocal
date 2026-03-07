#!/usr/bin/env python3
"""
Verificación directa de la base de datos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import lancedb

def check_db_direct():
    """Verifica la base de datos directamente"""
    print("🔍 Verificando base de datos directamente...")
    
    try:
        # Conectar a la base de datos
        db = lancedb.connect("skills_db")
        print(f"✅ Conectado a skills_db")
        
        # Listar tablas
        tables = db.table_names()
        print(f"📋 Tablas: {tables}")
        
        if "skills" in tables:
            table = db.open_table("skills")
            
            # Obtener schema
            schema = table.schema
            print(f"🏗️ Schema: {schema}")
            
            # Obtener datos
            df = table.to_pandas()
            print(f"📊 Registros: {len(df)}")
            
            if len(df) > 0:
                print(f"📋 Columnas: {list(df.columns)}")
                print(f"📄 Primeros 3 registros:")
                print(df.head(3))
            else:
                print("❌ No hay registros")
        else:
            print("❌ No existe la tabla 'skills'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_db_direct()
