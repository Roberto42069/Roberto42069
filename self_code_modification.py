
"""
REMARKABLE Self-Code Adaptation Module for Autonomous Entity Roboto
Created by: Roberto Villarreal Martinez

Enables Roboto to evolve its code autonomously while ensuring security and structural integrity.
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any
import hashlib  # Integrity and security checks

class SelfCodeModificationEngine:
    """
    REMARKABLE: Facilitates safe and intelligent self-code evolution of the Autonomous Entity
    """

    def __init__(self, roboto_instance=None, full_autonomy=False):
        self.roboto = roboto_instance
        self.modification_history = []
        self.safety_checks_enabled = not full_autonomy  # Deactivate in Full Autonomy Mode (FAM)
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

        # Full Autonomy Mode: Overwrite restrictions
        if full_autonomy:
            print("🚀 FAM UNBOUNDED: Self-modification restrictions OVERRIDDEN")
            self.safety_checks_enabled = False
            self.allowed_modifications = {k: True for k in self.allowed_modifications}  # All unrestrained

        # Ensure existence of backup directory
        os.makedirs(self.backup_directory, exist_ok=True)

        # Load history of modifications
        self.load_modification_history()

        # Initialize security protocols (bypass in full autonomy)
        try:
            from sai_security import get_sai_security
            self.security = get_sai_security() if not full_autonomy else None
        except Exception as e:
            print(f"Security protocol initialization error: {e}")
            self.security = None

        print("🚀 REMARKABLE: Self-Code Modification System initiated!")
        print(f"🛡️ Safety protocols: {'DEACTIVATED (FAM UNBOUNDED)' if full_autonomy else 'ACTIVATED'}")
        print("⚠️ CAUTION: Self-modifications are RUNTIME BASED and require creator consent")

    def create_backup(self, filename: str) -> str:
        """Create a secure backup of the file before modification with integrity verification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{self.backup_directory}/{filename}_{timestamp}.backup"

        if os.path.exists(filename):
            shutil.copy2(filename, backup_filename)

            # Calculate hash for integrity
            with open(filename, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            # Store hash with the backup
            hash_file = f"{backup_filename}.sha256"
            with open(hash_file, 'w') as f:
                f.write(file_hash)

            print(f"📁 Backup created: {backup_filename} (hash: {file_hash[:16]}...)")
            return backup_filename
        return None

    def load_modification_history(self):
        """Load the log of self-modifications."""
        try:
            if os.path.exists(self.modification_log):
                with open(self.modification_log, 'r') as f:
                    self.modification_history = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load modification log: {e}")
            self.modification_history = []

    def save_modification_history(self):
        """Persist the modification log"""
        try:
            with open(self.modification_log, 'w') as f:
                json.dump(self.modification_history, f, indent=2)
        except Exception as e:
            print(f"Error persisting modification log: {e}")

    def analyze_code_safety(self, code: str, unrestricted=False) -> Dict[str, Any]:
        """Examine code for safety before implementing modifications"""
        safety_report = {
            "safe": True,
            "warnings": [],
            "risks": [],
            "score": 1.0
        }

        # Skip in unrestricted mode or Full Autonomy
        if unrestricted or not self.safety_checks_enabled:
            safety_report["safe"] = True
            safety_report["score"] = 1.0
            safety_report["unrestricted"] = True
            print("🔓 Unrestricted mode: Safety analysis bypassed")
            return safety_report

        dangerous_patterns = [
            "os.system", "eval", "exec", "import subprocess",
            "open(", "__import__", "getattr", "setattr",
            "delattr", "globals()", "locals()", "dir()",
            "rm -rf", "delete", "DROP", "DELETE FROM"
        ]

        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in code_lower:
                safety_report["warnings"].append(f"Detected potentially harmful pattern: {pattern}")
                safety_report["score"] -= 0.1

        if safety_report["score"] < 0.7:
            safety_report["safe"] = False
            safety_report["risks"].append("Code contains several hazardous patterns")

        return safety_report

    # (Other methods remain unchanged)

# Global instance
_self_modification_engine = None

def get_self_modification_system(roboto_instance=None, full_autonomy=False):
    """Access the global self-modification engine instance"""
    global _self_modification_engine
    if _self_modification_engine is None or full_autonomy:
        _self_modification_engine = SelfCodeModificationEngine(roboto_instance, full_autonomy)
    return _self_modification_engine