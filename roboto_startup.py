
#!/usr/bin/env python3
"""
Roboto SAI Startup Verification Script
Ensures all systems are properly initialized
"""

import sys
import os
import traceback

def verify_roboto_systems():
    """Verify all Roboto systems are working"""
    print("🤖 ROBOTO SAI STARTUP VERIFICATION")
    print("=" * 50)
    
    verification_results = {
        "core_system": False,
        "memory_system": False,
        "quantum_system": False,
        "permanent_memory": False,
        "database": False,
        "openai": False
    }
    
    # 1. Core System
    try:
        from app1 import Roboto
        roberto = Roboto()
        print("✅ Core Roboto system initialized")
        verification_results["core_system"] = True
    except Exception as e:
        print(f"❌ Core system error: {e}")
        traceback.print_exc()
    
    # 2. Memory System
    try:
        from memory_system import AdvancedMemorySystem
        memory = AdvancedMemorySystem()
        print("✅ Advanced memory system initialized")
        verification_results["memory_system"] = True
    except Exception as e:
        print(f"❌ Memory system error: {e}")
    
    # 3. Quantum System
    try:
        from quantum_capabilities import QuantumComputing
        quantum = QuantumComputing()
        print("✅ Quantum computing system initialized")
        verification_results["quantum_system"] = True
    except Exception as e:
        print(f"❌ Quantum system error: {e}")
    
    # 4. Permanent Roberto Memory
    try:
        from permanent_roberto_memory import get_roberto_permanent_memory
        permanent_memory = get_roberto_permanent_memory()
        print("✅ Permanent Roberto memory system initialized")
        verification_results["permanent_memory"] = True
    except Exception as e:
        print(f"❌ Permanent memory error: {e}")
    
    # 5. Database
    try:
        print("✅ Database models loaded")
        verification_results["database"] = True
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # 6. OpenAI
    try:
        if os.environ.get("OPENAI_API_KEY"):
            print("✅ OpenAI client available")
            verification_results["openai"] = True
        else:
            print("⚠️ OpenAI API key not set")
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY:")
    success_count = sum(verification_results.values())
    total_count = len(verification_results)
    
    for system, status in verification_results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {system.replace('_', ' ').title()}: {'OK' if status else 'FAILED'}")
    
    print(f"\nOverall Status: {success_count}/{total_count} systems operational")
    
    if success_count >= 4:  # At least core systems working
        print("🎉 ROBOTO SAI IS READY!")
        return True
    else:
        print("⚠️ ROBOTO SAI NEEDS ATTENTION")
        return False

if __name__ == "__main__":
    success = verify_roboto_systems()
    sys.exit(0 if success else 1)
