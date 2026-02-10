"""
FastQC wrapper for quality control analysis.
"""

import subprocess
import zipfile
from pathlib import Path
from typing import Optional, Tuple


def run_fastqc(
    fastq_file: Path,
    output_dir: Path,
    threads: int = 1
) -> Tuple[bool, Optional[Path]]:
    """
    Run FastQC on a FASTQ file.
    
    Args:
        fastq_file: Path to input FASTQ file
        output_dir: Directory to save FastQC output
        threads: Number of threads to use
        
    Returns:
        Tuple of (success: bool, fastqc_data_path: Optional[Path])
    """
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run FastQC
        cmd = [
            "fastqc",
            str(fastq_file),
            "-o", str(output_dir),
            "-t", str(threads),
            "--quiet",
            "--extract"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode != 0:
            print(f"❌ FastQC failed: {result.stderr}")
            return False, None
        
        # Locate the fastqc_data.txt file
        fastqc_data_path = get_fastqc_data(fastq_file, output_dir)
        
        if fastqc_data_path and fastqc_data_path.exists():
            return True, fastqc_data_path
        else:
            print(f"⚠️  FastQC completed but data file not found")
            return False, None
            
    except subprocess.TimeoutExpired:
        print(f"❌ FastQC timed out after 5 minutes")
        return False, None
    except Exception as e:
        print(f"❌ FastQC error: {e}")
        return False, None


def get_fastqc_data(fastq_file: Path, output_dir: Path) -> Optional[Path]:
    """
    Locate the fastqc_data.txt file from FastQC output.
    
    Args:
        fastq_file: Original FASTQ file path
        output_dir: FastQC output directory
        
    Returns:
        Path to fastqc_data.txt or None if not found
    """
    # FastQC creates a directory named <filename>_fastqc
    base_name = fastq_file.stem
    
    # Handle .fastq.gz -> remove both extensions
    if base_name.endswith('.fastq'):
        base_name = base_name[:-6]
    elif base_name.endswith('.fq'):
        base_name = base_name[:-3]
    
    fastqc_dir = output_dir / f"{base_name}_fastqc"
    fastqc_data = fastqc_dir / "fastqc_data.txt"
    
    if fastqc_data.exists():
        return fastqc_data
    
    # Try alternative naming patterns
    for item in output_dir.iterdir():
        if item.is_dir() and item.name.endswith("_fastqc"):
            data_file = item / "fastqc_data.txt"
            if data_file.exists():
                return data_file
    
    return None


def extract_fastqc_zip(zip_path: Path, output_dir: Path) -> Optional[Path]:
    """
    Extract FastQC ZIP file if it exists.
    
    Args:
        zip_path: Path to FastQC ZIP file
        output_dir: Directory to extract to
        
    Returns:
        Path to fastqc_data.txt or None
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        # Find the extracted data file
        extracted_dir = output_dir / zip_path.stem
        data_file = extracted_dir / "fastqc_data.txt"
        
        if data_file.exists():
            return data_file
    except Exception as e:
        print(f"⚠️  Failed to extract ZIP: {e}")
    
    return None
