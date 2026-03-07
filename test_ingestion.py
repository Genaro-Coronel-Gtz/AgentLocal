#!/usr/bin/env python3
"""
Prueba directa de ingesta de skill
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from skill_manager import SkillManager

def test_skill_ingestion():
    """Prueba la ingesta de la skill de Rails"""
    print("🧪 Probando ingesta de skill Rails...")
    
    try:
        manager = SkillManager()
        
        # Ingestar la skill de Rails
        result = manager.ingest_skill("skills/rails.md", "Rails")
        
        print(f"📊 Resultado: {result}")
        
        if result.get("success"):
            print(f"✅ Skill ingestada exitosamente")
            print(f"📈 Chunks procesados: {result.get('chunks_processed', 0)}")
            
            # Verificar que está en la DB
            skills = manager.get_available_skills()
            print(f"🎯 Skills disponibles: {skills}")
            
            # Verificar estado enabled
            is_enabled = manager.is_skill_enabled("Rails")
            print(f"🔝 Skill Rails habilitada: {is_enabled}")
            
        else:
            print(f"❌ Error en ingesta: {result.get('error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_skill_ingestion()
    sys.exit(0 if success else 1)
