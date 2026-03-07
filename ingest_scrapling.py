#!/usr/bin/env python3
"""
Ingestar skill de Scrapling
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from skill_manager import SkillManager

def ingest_scrapling_skill():
    """Ingesta la skill de Scrapling"""
    print("🧪 Ingestando skill Scrapling...")
    
    try:
        manager = SkillManager()
        
        # Ingestar la skill de Scrapling
        result = manager.ingest_skill("skills/scrapling.md", "Scrapling")
        
        print(f"📊 Resultado: {result}")
        
        if result.get("success"):
            print(f"✅ Skill Scrapling ingestada exitosamente")
            print(f"📈 Chunks procesados: {result.get('chunks_processed', 0)}")
            
            # Verificar que está en la DB
            skills = manager.get_available_skills()
            print(f"🎯 Skills disponibles: {skills}")
            
            # Verificar estado enabled
            is_enabled = manager.is_skill_enabled("Scrapling")
            print(f"🔝 Skill Scrapling habilitada: {is_enabled}")
            
        else:
            print(f"❌ Error en ingesta: {result.get('error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = ingest_scrapling_skill()
    sys.exit(0 if success else 1)
