#!/usr/bin/env python3
"""
Migrate LM Studio Models to Ollama Format
Convert LM Studio models to Ollama-compatible format
"""

import os
import shutil
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

class LMStudioToOllamaMigrator:
    """Migrate LM Studio models to Ollama format"""
    
    def __init__(self):
        self.lmstudio_models = [
            {
                "name": "Qwen3-30B-A3B-Instruct-2507-MLX-4bit",
                "path": "~/.lmstudio/models/lmstudio-community/Qwen3-30B-A3B-Instruct-2507-MLX-4bit",
                "ollama_name": "qwen3-30b-mlx-4bit",
                "size_gb": 16.0,
                "description": "30B parameter Qwen model optimized for MLX with 4-bit quantization"
            },
            {
                "name": "Dia-1.6B",
                "path": "~/.lmstudio/models/mlx-community/Dia-1.6B",
                "ollama_name": "dia-1.6b-mlx",
                "size_gb": 6.0,
                "description": "1.6B parameter Dia model for MLX"
            }
        ]
        
        self.migration_results = {}
    
    def expand_path(self, path: str) -> str:
        """Expand tilde in path"""
        return os.path.expanduser(path)
    
    def check_model_exists(self, model_info: Dict[str, Any]) -> bool:
        """Check if LM Studio model exists"""
        expanded_path = self.expand_path(model_info["path"])
        model_path = Path(expanded_path)
        
        if not model_path.exists():
            print(f"❌ {model_info['name']}: Not found at {expanded_path}")
            return False
        
        # Check for required files
        required_files = ["config.json"]
        missing_files = []
        
        for file in required_files:
            if not (model_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ {model_info['name']}: Missing required files: {missing_files}")
            return False
        
        print(f"✅ {model_info['name']}: Found at {expanded_path}")
        return True
    
    def create_ollama_modelfile(self, model_info: Dict[str, Any], source_path: Path) -> str:
        """Create Ollama Modelfile for the model"""
        
        # Read the config.json to get model information
        config_path = source_path / "config.json"
        config = {}
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"⚠️  Could not read config.json: {e}")
        
        # Create Modelfile content
        modelfile_content = f"""# Modelfile for {model_info['ollama_name']}
# Migrated from LM Studio: {model_info['name']}
# Description: {model_info['description']}

FROM {source_path}

# Model configuration
TEMPLATE \"\"\"{self.get_chat_template(config)}\"\"\"

# System prompt
SYSTEM \"\"\"You are {model_info['ollama_name']}, a helpful AI assistant migrated from LM Studio. You maintain all the capabilities of the original model while being optimized for Ollama usage.\"\"\"

# Parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1

# Model metadata
PARAMETER num_ctx 4096
PARAMETER num_predict 2048
"""
        
        return modelfile_content
    
    def get_chat_template(self, config: Dict[str, Any]) -> str:
        """Extract chat template from config"""
        
        # Default template
        default_template = """{% for message in messages %}{% if message['role'] == 'user' %}{{ message['content'] }}{% elif message['role'] == 'assistant' %}{{ message['content'] }}{% endif %}{% endfor %}"""
        
        # Try to get template from config
        if 'chat_template' in config:
            return config['chat_template']
        elif 'chat_template_file' in config:
            return default_template
        else:
            return default_template
    
    def copy_model_files(self, source_path: Path, target_path: Path) -> bool:
        """Copy model files to target directory"""
        
        try:
            # Create target directory
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all model files
            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(source_path)
                    target_file = target_path / relative_path
                    
                    # Create parent directories if needed
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(file_path, target_file)
            
            print(f"✅ Copied model files to {target_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error copying files: {e}")
            return False
    
    def create_ollama_model(self, model_info: Dict[str, Any]) -> bool:
        """Create Ollama model from LM Studio model"""
        
        print(f"\n🔄 Migrating {model_info['name']} to Ollama...")
        
        # Check if source model exists
        if not self.check_model_exists(model_info):
            return False
        
        # Set up paths
        source_path = Path(self.expand_path(model_info["path"]))
        target_path = Path(f"./ollama_models/{model_info['ollama_name']}")
        
        # Copy model files
        if not self.copy_model_files(source_path, target_path):
            return False
        
        # Create Modelfile
        modelfile_content = self.create_ollama_modelfile(model_info, target_path)
        modelfile_path = target_path / "Modelfile"
        
        try:
            with open(modelfile_path, 'w') as f:
                f.write(modelfile_content)
            print(f"✅ Created Modelfile at {modelfile_path}")
        except Exception as e:
            print(f"❌ Error creating Modelfile: {e}")
            return False
        
        # Create Ollama model
        try:
            print(f"🔄 Creating Ollama model: {model_info['ollama_name']}")
            
            # Change to target directory and create model
            result = subprocess.run([
                "ollama", "create", "-f", "Modelfile", model_info['ollama_name']
            ], cwd=target_path, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Successfully created Ollama model: {model_info['ollama_name']}")
                return True
            else:
                print(f"❌ Error creating Ollama model: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  Timeout creating Ollama model: {model_info['ollama_name']}")
            return False
        except Exception as e:
            print(f"❌ Exception creating Ollama model: {e}")
            return False
    
    def migrate_all_models(self):
        """Migrate all LM Studio models to Ollama"""
        
        print("🚀 Starting LM Studio to Ollama Migration")
        print("=" * 50)
        
        # Create ollama_models directory
        Path("./ollama_models").mkdir(exist_ok=True)
        
        successful_migrations = 0
        
        for model_info in self.lmstudio_models:
            print(f"\n📋 Processing: {model_info['name']}")
            print("-" * 40)
            
            success = self.create_ollama_model(model_info)
            self.migration_results[model_info['name']] = success
            
            if success:
                successful_migrations += 1
        
        # Generate summary
        self.generate_migration_summary(successful_migrations)
    
    def generate_migration_summary(self, successful_migrations: int):
        """Generate migration summary"""
        
        print("\n📊 Migration Summary:")
        print("=" * 30)
        print(f"✅ Successful migrations: {successful_migrations}/{len(self.lmstudio_models)}")
        
        print("\n📋 Migration Results:")
        for model_name, success in self.migration_results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {status}: {model_name}")
        
        if successful_migrations > 0:
            print("\n🎯 Next Steps:")
            print("1. Test the migrated models:")
            for model_info in self.lmstudio_models:
                if self.migration_results.get(model_info['name'], False):
                    print(f"   ollama run {model_info['ollama_name']} 'Hello, how are you?'")
            
            print("\n2. List all your Ollama models:")
            print("   ollama list")
            
            print("\n3. Integrate with your existing system:")
            print("   - Add to your FastAPI server")
            print("   - Update model selection logic")
            print("   - Test with your existing workflows")
        
        # Save migration report
        report = {
            "timestamp": "2025-01-25T20:30:00Z",
            "migration_results": self.migration_results,
            "models_migrated": self.lmstudio_models,
            "successful_migrations": successful_migrations,
            "total_models": len(self.lmstudio_models)
        }
        
        with open("lmstudio_migration_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Migration report saved to: lmstudio_migration_report.json")

def main():
    """Main function"""
    migrator = LMStudioToOllamaMigrator()
    migrator.migrate_all_models()

if __name__ == "__main__":
    main()
