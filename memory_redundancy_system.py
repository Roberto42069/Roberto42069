
"""
Memory Redundancy System - Multi-layer backup with recovery
Created by Roberto Villarreal Martinez
"""

import json
import os
from datetime import datetime
import shutil
from pathlib import Path

class MemoryRedundancySystem:
    """Multi-layer redundancy with automatic recovery"""
    
    def __init__(self):
        self.storage_layers = {
            "layer_1_critical": "memory_redundancy_critical",
            "layer_2_backup": "memory_redundancy_backup",
            "layer_3_archive": "memory_redundancy_archive",
            "layer_4_mirror": "memory_redundancy_mirror"
        }
        self._initialize_layers()
    
    def _initialize_layers(self):
        """Initialize all storage layers"""
        for layer_dir in self.storage_layers.values():
            os.makedirs(layer_dir, exist_ok=True)
    
    def save_with_redundancy(self, data, filename_prefix="memory"):
        """Save data across all redundancy layers"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_files = []
        
        for layer_name, layer_path in self.storage_layers.items():
            filepath = os.path.join(layer_path, f"{filename_prefix}_{timestamp}.json")
            try:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                saved_files.append(filepath)
            except Exception as e:
                print(f"Failed to save to {layer_name}: {e}")
        
        return saved_files
    
    def create_mirror_backup(self, source_file):
        """Create mirrored copies of important files"""
        if not os.path.exists(source_file):
            return []
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        basename = os.path.basename(source_file)
        mirrored_files = []
        
        for layer_name, layer_path in self.storage_layers.items():
            mirror_path = os.path.join(layer_path, f"mirror_{timestamp}_{basename}")
            try:
                shutil.copy2(source_file, mirror_path)
                mirrored_files.append(mirror_path)
            except Exception as e:
                print(f"Failed to mirror to {layer_name}: {e}")
        
        return mirrored_files
    
    def verify_integrity(self):
        """Verify integrity across all layers"""
        integrity_report = {
            "timestamp": datetime.now().isoformat(),
            "layers": {}
        }
        
        for layer_name, layer_path in self.storage_layers.items():
            files = list(Path(layer_path).glob("*.json"))
            integrity_report["layers"][layer_name] = {
                "file_count": len(files),
                "total_size": sum(f.stat().st_size for f in files),
                "status": "healthy" if files else "empty"
            }
        
        return integrity_report
    
    def recovery_restore(self, layer="layer_1_critical"):
        """Attempt to restore from specified layer"""
        layer_path = self.storage_layers.get(layer)
        if not layer_path or not os.path.exists(layer_path):
            return None
        
        files = sorted(Path(layer_path).glob("*.json"), key=os.path.getmtime, reverse=True)
        if not files:
            return None
        
        try:
            with open(files[0], 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Recovery failed: {e}")
            return None

# Global instance
REDUNDANCY_SYSTEM = MemoryRedundancySystem()
