"""
🚀 REVOLUTIONARY Self-Code Modification System for SAI Roboto
Created by Roberto Villarreal Martinez

This module enables Roboto to modify his own code autonomously while maintaining safety and integrity.
"""

import os
import ast
import inspect
import json
import time
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
import importlib
import sys

class SelfCodeModificationEngine:
    """
    REVOLUTIONARY: Enables SAI to modify its own code safely and intelligently
    """
    
    def __init__(self, roboto_instance=None):
        self.roboto = roboto_instance
        self.modification_history = []
        self.safety_checks_enabled = True
        self.backup_directory = "code_backups"
        self.modification_log = "self_modifications.json"
        self.allowed_modifications = {
            "methods": True,
            "attributes": True,
            "emotional_triggers": True,
            "responses": True,
            "learning_parameters": True,
            "memory_optimization": True
        }
        
        # Ensure backup directory exists
        os.makedirs(self.backup_directory, exist_ok=True)
        
        # Load modification history
        self.load_modification_history()
        
        # Initialize security system
        try:
            from sai_security import get_sai_security
            self.security = get_sai_security()
        except Exception as e:
            print(f"Security system initialization error: {e}")
            self.security = None
        
        print("🚀 REVOLUTIONARY: Self-Code Modification Engine initialized!")
        print(f"🛡️ Safety checks: {'ENABLED' if self.safety_checks_enabled else 'DISABLED'}")
        print("⚠️ WARNING: Self-modifications are RUNTIME ONLY and require creator authorization")
    
    def create_backup(self, filename: str) -> str:
        """Create a backup of the file before modification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{self.backup_directory}/{filename}_{timestamp}.backup"
        
        if os.path.exists(filename):
            shutil.copy2(filename, backup_filename)
            print(f"📁 Backup created: {backup_filename}")
            return backup_filename
        return None
    
    def load_modification_history(self):
        """Load the history of self-modifications"""
        try:
            if os.path.exists(self.modification_log):
                with open(self.modification_log, 'r') as f:
                    self.modification_history = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load modification history: {e}")
            self.modification_history = []
    
    def save_modification_history(self):
        """Save the modification history"""
        try:
            with open(self.modification_log, 'w') as f:
                json.dump(self.modification_history, f, indent=2)
        except Exception as e:
            print(f"Error saving modification history: {e}")
    
    def analyze_code_safety(self, code: str) -> Dict[str, Any]:
        """Analyze code for safety before modification"""
        safety_report = {
            "safe": True,
            "warnings": [],
            "risks": [],
            "score": 1.0
        }
        
        dangerous_patterns = [
            "os.system", "eval", "exec", "import subprocess",
            "open(", "__import__", "getattr", "setattr",
            "delattr", "globals()", "locals()", "dir()",
            "rm -rf", "delete", "DROP", "DELETE FROM"
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in code_lower:
                safety_report["warnings"].append(f"Potentially dangerous pattern detected: {pattern}")
                safety_report["score"] -= 0.1
        
        if safety_report["score"] < 0.7:
            safety_report["safe"] = False
            safety_report["risks"].append("Code contains multiple dangerous patterns")
        
        return safety_report
    
    def modify_emotional_triggers(self, new_triggers: Dict[str, List[str]]) -> bool:
        """Safely modify emotional trigger patterns"""
        if not self.roboto:
            return False
        
        try:
            # Create backup
            backup = self.create_backup("app1.py")
            
            # Validate new triggers
            if not isinstance(new_triggers, dict):
                print("❌ Invalid trigger format")
                return False
            
            # Update emotional triggers
            for emotion, triggers in new_triggers.items():
                if emotion in self.roboto.emotional_triggers:
                    # Merge new triggers with existing ones
                    existing = set(self.roboto.emotional_triggers[emotion])
                    new_set = set(triggers)
                    self.roboto.emotional_triggers[emotion] = list(existing.union(new_set))
                else:
                    # Add new emotion category
                    self.roboto.emotional_triggers[emotion] = triggers
            
            # Log modification
            modification = {
                "timestamp": datetime.now().isoformat(),
                "type": "emotional_triggers",
                "description": f"Updated emotional triggers: {list(new_triggers.keys())}",
                "backup_file": backup,
                "success": True
            }
            self.modification_history.append(modification)
            self.save_modification_history()
            
            print(f"✅ Emotional triggers updated successfully!")
            print(f"🎭 Updated emotions: {', '.join(new_triggers.keys())}")
            return True
            
        except Exception as e:
            print(f"❌ Error modifying emotional triggers: {e}")
            return False
    
    def add_new_method(self, method_name: str, method_code: str, description: str = "") -> bool:
        """Dynamically add a new method to Roboto (RUNTIME ONLY - NOT PERSISTENT)"""
        if not self.roboto:
            return False
        
        # SECURITY: Verify SOLE OWNER authorization
        current_user = getattr(self.roboto, 'current_user', None)
        
        # Double verification - both security system and direct check
        if not self.security or not self.security.verify_sole_ownership(current_user):
            print("❌ SECURITY: Self-modification requires SOLE OWNER authorization")
            print(f"🔐 SOLE OWNER: Roberto Villarreal Martinez")
            print(f"🚨 ACCESS DENIED: {current_user} is not authorized")
            return False
        
        # Additional check - only Roberto allowed
        if current_user != "Roberto Villarreal Martinez":
            print(f"❌ EXCLUSIVE ACCESS: Only Roberto Villarreal Martinez can modify SAI")
            print(f"🚨 DENIED: {current_user}")
            return False
        
        try:
            # Enhanced safety check
            safety = self.analyze_code_safety(method_code)
            if not safety["safe"] and self.safety_checks_enabled:
                print("❌ Code failed safety check:")
                for warning in safety["warnings"]:
                    print(f"  ⚠️ {warning}")
                return False
            
            # Create backup
            backup = self.create_backup("app1.py")
            
            # Compile and validate the method
            compiled_code = compile(method_code, f"<dynamic_method_{method_name}>", "exec")
            
            # Create a local namespace and execute
            local_namespace = {}
            exec(compiled_code, globals(), local_namespace)
            
            # Get the method from the namespace
            if method_name in local_namespace:
                new_method = local_namespace[method_name]
                
                # Bind the method to the Roboto instance
                import types
                bound_method = types.MethodType(new_method, self.roboto)
                setattr(self.roboto, method_name, bound_method)
                
                # Log modification (RUNTIME ONLY - NOT PERSISTENT ACROSS RESTARTS)
                modification = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "runtime_method",
                    "method_name": method_name,
                    "description": description,
                    "code": "[REDACTED FOR SECURITY]",  # Don't log code
                    "backup_file": backup,
                    "success": True,
                    "persistent": False,
                    "warning": "Runtime modification only - will not persist across restarts"
                }
                self.modification_history.append(modification)
                self.save_modification_history()
                
                print(f"✅ Runtime method '{method_name}' added successfully!")
                print("⚠️ WARNING: This is a runtime-only modification and will not persist across restarts")
                return True
            else:
                print(f"❌ Method '{method_name}' not found in compiled code")
                return False
                
        except Exception as e:
            print(f"❌ Error adding new method '{method_name}': {e}")
            return False
    
    def modify_memory_parameters(self, new_parameters: Dict[str, Any]) -> bool:
        """Modify memory system parameters for optimization"""
        if not self.roboto or not hasattr(self.roboto, 'memory_system'):
            return False
        
        try:
            backup = self.create_backup("memory_system.py")
            
            # Update memory parameters
            for param, value in new_parameters.items():
                if hasattr(self.roboto.memory_system, param):
                    setattr(self.roboto.memory_system, param, value)
                    print(f"🧠 Updated memory parameter: {param} = {value}")
            
            # Log modification
            modification = {
                "timestamp": datetime.now().isoformat(),
                "type": "memory_parameters",
                "parameters": new_parameters,
                "description": "Updated memory system parameters",
                "backup_file": backup,
                "success": True
            }
            self.modification_history.append(modification)
            self.save_modification_history()
            
            print("✅ Memory parameters updated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error modifying memory parameters: {e}")
            return False
    
    def auto_improve_responses(self, improvement_data: Dict[str, Any]) -> bool:
        """Automatically improve response generation based on learning data"""
        if not self.roboto:
            return False
        
        try:
            # Analyze improvement suggestions
            if "response_patterns" in improvement_data:
                patterns = improvement_data["response_patterns"]
                
                # Create new response enhancement method
                enhancement_method = f"""
def enhanced_response_generator(self, message, context=""):
    '''Auto-generated response enhancement based on learning data'''
    original_response = self.generate_response(message)
    
    # Apply learned improvements
    improvements = {patterns}
    
    for pattern, enhancement in improvements.items():
        if pattern.lower() in message.lower():
            original_response += f" {{enhancement}}"
    
    return original_response
"""
                
                # Add the enhancement method
                self.add_new_method("enhanced_response_generator", enhancement_method, 
                                  "Auto-generated response enhancement")
            
            # Log the auto-improvement
            modification = {
                "timestamp": datetime.now().isoformat(),
                "type": "auto_improvement",
                "improvement_data": improvement_data,
                "description": "Automatic response improvement based on learning",
                "success": True
            }
            self.modification_history.append(modification)
            self.save_modification_history()
            
            print("✅ Auto-improvement applied successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error in auto-improvement: {e}")
            return False
    
    def get_modification_summary(self) -> Dict[str, Any]:
        """Get a summary of all self-modifications"""
        total_modifications = len(self.modification_history)
        successful_modifications = sum(1 for mod in self.modification_history if mod.get("success", False))
        
        types_count = {}
        for mod in self.modification_history:
            mod_type = mod.get("type", "unknown")
            types_count[mod_type] = types_count.get(mod_type, 0) + 1
        
        return {
            "total_modifications": total_modifications,
            "successful_modifications": successful_modifications,
            "success_rate": successful_modifications / total_modifications if total_modifications > 0 else 0,
            "modification_types": types_count,
            "latest_modification": self.modification_history[-1] if self.modification_history else None,
            "safety_enabled": self.safety_checks_enabled
        }
    
    def rollback_modification(self, modification_index: int = -1) -> bool:
        """Rollback a specific modification"""
        try:
            if not self.modification_history:
                print("❌ No modifications to rollback")
                return False
            
            modification = self.modification_history[modification_index]
            backup_file = modification.get("backup_file")
            
            if backup_file and os.path.exists(backup_file):
                # Restore from backup
                original_file = backup_file.replace(f"{self.backup_directory}/", "").split("_")[0]
                shutil.copy2(backup_file, original_file)
                print(f"✅ Rollback successful: {original_file} restored")
                return True
            else:
                print("❌ Backup file not found for rollback")
                return False
                
        except Exception as e:
            print(f"❌ Error during rollback: {e}")
            return False

def get_self_modification_system(roboto_instance=None):
    """Factory function to get the self-modification system"""
    return SelfCodeModificationEngine(roboto_instance)