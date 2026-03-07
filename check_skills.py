#!/usr/bin/env python3
"""
Verificar skills disponibles en la base de datos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from skill_manager import SkillManager

def check_skills():
    """Verifica las skills disponibles y su estado"""
    print("🔍 Verificando skills disponibles...")
    
    try:
        manager = SkillManager()
        
        # Obtener todas las skills
        all_skills = manager.get_available_skills()
        print(f"📋 Todas las skills: {all_skills}")
        
        # Obtener skills habilitadas
        enabled_skills = manager.get_enabled_skills()
        print(f"✅ Skills habilitadas: {enabled_skills}")
        
        # Verificar estado individual
        for skill in all_skills:
            is_enabled = manager.is_skill_enabled(skill)
            status = "✅ Habilitada" if is_enabled else "❌ Deshabilitada"
            print(f"🎯 {skill}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_skills()
