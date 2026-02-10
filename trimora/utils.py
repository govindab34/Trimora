"""
Utility functions for dependency checking and system operations.
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, List


def check_command(command: str) -> bool:
    """
    Check if a command exists in the system PATH.
    
    Args:
        command: Command name to check
        
    Returns:
        True if command exists, False otherwise
    """
    return shutil.which(command) is not None


def check_dependencies() -> Dict[str, bool]:
    """
    Check if all required external dependencies are installed.
    
    Returns:
        Dictionary with tool names as keys and availability as values
    """
    deps = {
        "fastqc": check_command("fastqc"),
        "fastp": check_command("fastp"),
        "ollama": check_command("ollama"),
    }
    return deps


def print_dependency_instructions(missing: List[str]) -> None:
    """
    Print installation instructions for missing dependencies.
    
    Args:
        missing: List of missing dependency names
    """
    print("\n⚠️  Missing dependencies detected:\n")
    
    instructions = {
        "fastqc": """
FastQC:
  Ubuntu/Debian: sudo apt-get install fastqc
  macOS: brew install fastqc
  Manual: https://www.bioinformatics.babraham.ac.uk/projects/fastqc/
""",
        "fastp": """
fastp:
  Ubuntu/Debian: sudo apt-get install fastp
  macOS: brew install fastp
  Manual: https://github.com/OpenGene/fastp
""",
        "ollama": """
Ollama:
  Linux: curl -fsSL https://ollama.com/install.sh | sh
  macOS: brew install ollama
  Manual: https://ollama.com/download
  
  After installation, start Ollama:
    ollama serve
"""
    }
    
    for dep in missing:
        if dep in instructions:
            print(instructions[dep])


def check_ollama_running() -> bool:
    """
    Check if Ollama service is running.
    
    Returns:
        True if Ollama is running, False otherwise
    """
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def install_ollama() -> bool:
    """
    Automatically install Ollama.
    
    Returns:
        True if installation successful, False otherwise
    """
    import platform
    
    system = platform.system().lower()
    
    print("📥 Ollama not found. Installing automatically...")
    
    try:
        if system == "linux":
            # Linux installation
            print("  Downloading Ollama for Linux...")
            result = subprocess.run(
                ["curl", "-fsSL", "https://ollama.com/install.sh"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Run the install script
                install_process = subprocess.run(
                    ["sh", "-c", result.stdout],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if install_process.returncode == 0:
                    print("  ✅ Ollama installed successfully!")
                    return True
                else:
                    print(f"  ⚠️ Installation failed: {install_process.stderr}")
                    return False
        
        elif system == "darwin":  # macOS
            print("  Please install Ollama using: brew install ollama")
            print("  Or download from: https://ollama.com/download")
            return False
        
        else:  # Windows
            print("  Please download Ollama from: https://ollama.com/download")
            return False
            
    except Exception as e:
        print(f"  ❌ Auto-installation failed: {e}")
        print("  Please install manually from: https://ollama.com/download")
        return False


def start_ollama_service() -> bool:
    """
    Start Ollama service in the background.
    
    Returns:
        True if started successfully, False otherwise
    """
    import time
    
    # Check if already running
    if check_ollama_running():
        return True
    
    print("🚀 Starting Ollama service...")
    
    try:
        # Start Ollama in background
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Wait for it to start (up to 10 seconds)
        for i in range(10):
            time.sleep(1)
            if check_ollama_running():
                print("  ✅ Ollama service started!")
                return True
        
        print("  ⚠️ Ollama started but not responding yet. Please wait a moment.")
        return False
        
    except Exception as e:
        print(f"  ❌ Failed to start Ollama: {e}")
        return False


def check_ollama_model(model_name: str = "llama3:8b") -> bool:
    """
    Check if a specific Ollama model is available.
    
    Args:
        model_name: Name of the model to check
        
    Returns:
        True if model is available, False otherwise
    """
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return any(model_name in m for m in models)
        return False
    except Exception:
        return False


def install_ollama_model(model_name: str = "llama3:8b") -> bool:
    """
    Attempt to pull/install an Ollama model.
    
    Args:
        model_name: Name of the model to install
        
    Returns:
        True if installation successful, False otherwise
    """
    try:
        print(f"📥 Downloading {model_name} model (this may take a few minutes)...")
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to install model: {e}")
        return False


def ensure_directory(path: Path) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        path: Directory path to create
    """
    path.mkdir(parents=True, exist_ok=True)


def get_file_size(filepath: Path) -> str:
    """
    Get human-readable file size.
    
    Args:
        filepath: Path to file
        
    Returns:
        File size as human-readable string
    """
    size = filepath.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def validate_fastq(filepath: Path) -> bool:
    """
    Basic validation of FASTQ file format.
    
    Args:
        filepath: Path to FASTQ file
        
    Returns:
        True if file appears to be valid FASTQ format
    """
    try:
        with open(filepath, 'r') as f:
            # Check first line starts with @
            first_line = f.readline()
            if not first_line.startswith('@'):
                return False
            # Check we can read at least 4 lines (one complete record)
            for _ in range(3):
                if not f.readline():
                    return False
        return True
    except Exception:
        return False
