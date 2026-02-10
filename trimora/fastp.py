"""
fastp wrapper for read trimming and quality filtering.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


def run_fastp(
    input_fastq: Path,
    output_fastq: Path,
    parameters: Dict[str, Any],
    output_dir: Optional[Path] = None
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Run fastp with specified parameters.
    
    Args:
        input_fastq: Input FASTQ file path
        output_fastq: Output FASTQ file path
        parameters: Dictionary of fastp parameters from AI
        output_dir: Directory for JSON/HTML reports (optional)
        
    Returns:
        Tuple of (success: bool, fastp_report: Optional[Dict])
    """
    try:
        # Build fastp command
        cmd = build_fastp_command(input_fastq, output_fastq, parameters, output_dir)
        
        # Run fastp
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        if result.returncode != 0:
            print(f"❌ fastp failed: {result.stderr}")
            return False, None
        
        # Parse fastp JSON report if available
        report = None
        if output_dir:
            json_path = output_dir / f"{output_fastq.stem}_fastp.json"
            if json_path.exists():
                with open(json_path, 'r') as f:
                    report = json.load(f)
        
        return True, report
        
    except subprocess.TimeoutExpired:
        print(f"❌ fastp timed out after 10 minutes")
        return False, None
    except Exception as e:
        print(f"❌ fastp error: {e}")
        return False, None


def build_fastp_command(
    input_fastq: Path,
    output_fastq: Path,
    parameters: Dict[str, Any],
    output_dir: Optional[Path] = None
) -> list:
    """
    Build fastp command from parameters dictionary.
    
    Args:
        input_fastq: Input file path
        output_fastq: Output file path
        parameters: Parameter dictionary from AI
        output_dir: Optional directory for reports
        
    Returns:
        Command as list of strings
    """
    cmd = [
        "fastp",
        "-i", str(input_fastq),
        "-o", str(output_fastq),
    ]
    
    # Quality filtering
    if "quality" in parameters:
        cmd.extend(["--qualified_quality_phred", str(parameters["quality"])])
    
    # Length filtering
    if "length" in parameters:
        cmd.extend(["--length_required", str(parameters["length"])])
    
    # Trim from front (5' end)
    if "trim_front" in parameters and parameters["trim_front"] > 0:
        cmd.extend(["--trim_front1", str(parameters["trim_front"])])
    
    # Trim from tail (3' end)
    if "trim_tail" in parameters and parameters["trim_tail"] > 0:
        cmd.extend(["--trim_tail1", str(parameters["trim_tail"])])
    
    # Adapter trimming
    if parameters.get("adapter_trim", True):
        cmd.append("--detect_adapter_for_pe")
    
    # PolyG trimming (for NextSeq/NovaSeq)
    if parameters.get("poly_g_trim", False):
        cmd.append("--trim_poly_g")
    
    # PolyX trimming
    if parameters.get("poly_x_trim", False):
        cmd.append("--trim_poly_x")
    
    # Deduplication
    if parameters.get("dedup", False):
        cmd.append("--dedup")
    
    # Complexity filtering
    if "complexity_threshold" in parameters:
        cmd.extend(["--complexity_threshold", str(parameters["complexity_threshold"])])
    
    # Output reports
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        json_file = output_dir / f"{output_fastq.stem}_fastp.json"
        html_file = output_dir / f"{output_fastq.stem}_fastp.html"
        cmd.extend([
            "--json", str(json_file),
            "--html", str(html_file)
        ])
    
    # Thread count
    threads = parameters.get("threads", 4)
    cmd.extend(["--thread", str(threads)])
    
    return cmd


def get_default_parameters() -> Dict[str, Any]:
    """
    Get conservative default parameters.
    
    Returns:
        Default parameter dictionary
    """
    return {
        "quality": 20,
        "length": 35,
        "trim_front": 0,
        "trim_tail": 0,
        "adapter_trim": True,
        "poly_g_trim": False,
        "poly_x_trim": False,
        "dedup": False,
        "threads": 4
    }


def validate_parameters(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize parameters from AI.
    
    Args:
        parameters: Raw parameters from AI
        
    Returns:
        Validated and sanitized parameters
    """
    defaults = get_default_parameters()
    validated = defaults.copy()
    
    # Quality threshold (0-40)
    if "quality" in parameters:
        try:
            q = int(parameters["quality"])
            validated["quality"] = max(0, min(40, q))
        except (ValueError, TypeError):
            pass
    
    # Length threshold (1-300)
    if "length" in parameters:
        try:
            l = int(parameters["length"])
            validated["length"] = max(1, min(300, l))
        except (ValueError, TypeError):
            pass
    
    # Trim front (0-50)
    if "trim_front" in parameters:
        try:
            tf = int(parameters["trim_front"])
            validated["trim_front"] = max(0, min(50, tf))
        except (ValueError, TypeError):
            pass
    
    # Trim tail (0-50)
    if "trim_tail" in parameters:
        try:
            tt = int(parameters["trim_tail"])
            validated["trim_tail"] = max(0, min(50, tt))
        except (ValueError, TypeError):
            pass
    
    # Boolean parameters
    for bool_param in ["adapter_trim", "poly_g_trim", "poly_x_trim", "dedup"]:
        if bool_param in parameters:
            validated[bool_param] = bool(parameters[bool_param])
    
    # Threads (1-32)
    if "threads" in parameters:
        try:
            t = int(parameters["threads"])
            validated["threads"] = max(1, min(32, t))
        except (ValueError, TypeError):
            pass
    
    return validated
