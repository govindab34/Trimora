"""
FastQC report parser - converts FastQC data to structured JSON.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional


def parse_fastqc_data(fastqc_data_path: Path) -> Dict[str, Any]:
    """
    Parse FastQC data file into structured dictionary.
    
    Args:
        fastqc_data_path: Path to fastqc_data.txt
        
    Returns:
        Dictionary containing parsed FastQC metrics
    """
    metrics = {
        "basic_statistics": {},
        "per_base_quality": {},
        "per_sequence_quality": {},
        "per_base_content": {},
        "gc_content": {},
        "n_content": {},
        "sequence_length": {},
        "duplication": {},
        "overrepresented": [],
        "adapter_content": {},
        "module_status": {}
    }
    
    try:
        with open(fastqc_data_path, 'r') as f:
            content = f.read()
        
        # Extract module statuses
        metrics["module_status"] = extract_module_status(content)
        
        # Extract basic statistics
        metrics["basic_statistics"] = extract_basic_statistics(content)
        
        # Extract per-base quality scores
        metrics["per_base_quality"] = extract_per_base_quality(content)
        
        # Extract per-sequence quality
        metrics["per_sequence_quality"] = extract_per_sequence_quality(content)
        
        # Extract sequence content
        metrics["per_base_content"] = extract_sequence_content(content)
        
        # Extract GC content
        metrics["gc_content"] = extract_gc_content(content)
        
        # Extract N content
        metrics["n_content"] = extract_n_content(content)
        
        # Extract sequence length distribution
        metrics["sequence_length"] = extract_sequence_length(content)
        
        # Extract duplication levels
        metrics["duplication"] = extract_duplication(content)
        
        # Extract overrepresented sequences
        metrics["overrepresented"] = extract_overrepresented(content)
        
        # Extract adapter content
        metrics["adapter_content"] = extract_adapter_content(content)
        
    except Exception as e:
        print(f"⚠️  Error parsing FastQC data: {e}")
    
    return metrics


def extract_module_status(content: str) -> Dict[str, str]:
    """Extract pass/warn/fail status for each module."""
    status = {}
    pattern = r'>>(.*?)\t(pass|warn|fail)'
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for module_name, module_status in matches:
        status[module_name.strip()] = module_status.upper()
    
    return status


def extract_basic_statistics(content: str) -> Dict[str, Any]:
    """Extract basic statistics section."""
    stats = {}
    
    section = extract_section(content, "Basic Statistics")
    if not section:
        return stats
    
    lines = section.strip().split('\n')[1:]  # Skip header
    for line in lines:
        if line.startswith('>>END_MODULE'):
            break
        parts = line.split('\t')
        if len(parts) >= 2:
            key = parts[0].strip()
            value = parts[1].strip()
            
            # Convert numeric values
            if key in ["Total Sequences", "Sequence length"]:
                try:
                    stats[key] = int(value.split('-')[0])  # Handle ranges
                except ValueError:
                    stats[key] = value
            elif key == "%GC":
                try:
                    stats[key] = float(value)
                except ValueError:
                    stats[key] = value
            else:
                stats[key] = value
    
    return stats


def extract_per_base_quality(content: str) -> Dict[str, Any]:
    """Extract per-base quality scores."""
    quality_data = {"mean_scores": [], "positions": []}
    
    section = extract_section(content, "Per base sequence quality")
    if not section:
        return quality_data
    
    lines = section.strip().split('\n')[1:]  # Skip header
    mean_scores = []
    
    for line in lines:
        if line.startswith('>>END_MODULE'):
            break
        parts = line.split('\t')
        if len(parts) >= 2:
            try:
                position = parts[0].strip()
                mean_quality = float(parts[1])
                quality_data["positions"].append(position)
                mean_scores.append(mean_quality)
            except (ValueError, IndexError):
                continue
    
    if mean_scores:
        quality_data["mean_scores"] = mean_scores
        quality_data["average_quality"] = sum(mean_scores) / len(mean_scores)
        quality_data["min_quality"] = min(mean_scores)
        quality_data["max_quality"] = max(mean_scores)
    
    return quality_data


def extract_per_sequence_quality(content: str) -> Dict[str, Any]:
    """Extract per-sequence quality scores."""
    quality_data = {}
    
    section = extract_section(content, "Per sequence quality scores")
    if not section:
        return quality_data
    
    lines = section.strip().split('\n')[1:]
    qualities = []
    counts = []
    
    for line in lines:
        if line.startswith('>>END_MODULE'):
            break
        parts = line.split('\t')
        if len(parts) >= 2:
            try:
                quality = float(parts[0])
                count = float(parts[1])
                qualities.append(quality)
                counts.append(count)
            except (ValueError, IndexError):
                continue
    
    if qualities and counts:
        total_count = sum(counts)
        weighted_avg = sum(q * c for q, c in zip(qualities, counts)) / total_count
        quality_data["average_sequence_quality"] = weighted_avg
        quality_data["peak_quality"] = qualities[counts.index(max(counts))]
    
    return quality_data


def extract_sequence_content(content: str) -> Dict[str, Any]:
    """Extract per-base sequence content."""
    base_content = {"positions": [], "G": [], "A": [], "T": [], "C": []}
    
    section = extract_section(content, "Per base sequence content")
    if not section:
        return base_content
    
    lines = section.strip().split('\n')[1:]
    
    for line in lines:
        if line.startswith('>>END_MODULE'):
            break
        parts = line.split('\t')
        if len(parts) >= 5:
            try:
                base_content["positions"].append(parts[0].strip())
                base_content["G"].append(float(parts[1]))
                base_content["A"].append(float(parts[2]))
                base_content["T"].append(float(parts[3]))
                base_content["C"].append(float(parts[4]))
            except (ValueError, IndexError):
                continue
    
    return base_content


def extract_gc_content(content: str) -> Dict[str, Any]:
    """Extract GC content distribution."""
    gc_data = {}
    
    section = extract_section(content, "Per sequence GC content")
    if not section:
        return gc_data
    
    lines = section.strip().split('\n')[1:]
    gc_values = []
    counts = []
    
    for line in lines:
        if line.startswith('>>END_MODULE'):
            break
        parts = line.split('\t')
        if len(parts) >= 2:
            try:
                gc_values.append(float(parts[0]))
                counts.append(float(parts[1]))
            except (ValueError, IndexError):
                continue
    
    if gc_values and counts:
        total = sum(counts)
        gc_data["mean_gc"] = sum(g * c for g, c in zip(gc_values, counts)) / total
    
    return gc_data


def extract_n_content(content: str) -> Dict[str, Any]:
    """Extract N content per position."""
    n_data = {"positions": [], "n_percent": []}
    
    section = extract_section(content, "Per base N content")
    if not section:
        return n_data
    
    lines = section.strip().split('\n')[1:]
    
    for line in lines:
        if line.startswith('>>END_MODULE'):
            break
        parts = line.split('\t')
        if len(parts) >= 2:
            try:
                n_data["positions"].append(parts[0].strip())
                n_data["n_percent"].append(float(parts[1]))
            except (ValueError, IndexError):
                continue
    
    if n_data["n_percent"]:
        n_data["max_n_percent"] = max(n_data["n_percent"])
    
    return n_data


def extract_sequence_length(content: str) -> Dict[str, Any]:
    """Extract sequence length distribution."""
    length_data = {}
    
    section = extract_section(content, "Sequence Length Distribution")
    if not section:
        return length_data
    
    lines = section.strip().split('\n')[1:]
    
    for line in lines:
        if line.startswith('>>END_MODULE'):
            break
        parts = line.split('\t')
        if len(parts) >= 2:
            try:
                length = parts[0].strip()
                count = float(parts[1])
                length_data[length] = count
            except (ValueError, IndexError):
                continue
    
    return length_data


def extract_duplication(content: str) -> Dict[str, Any]:
    """Extract sequence duplication levels."""
    dup_data = {}
    
    section = extract_section(content, "Sequence Duplication Levels")
    if not section:
        return dup_data
    
    # Look for total deduplicated percentage
    match = re.search(r'#Total Deduplicated Percentage\s+([\d.]+)', section)
    if match:
        dup_data["total_deduplicated_percentage"] = float(match.group(1))
    
    return dup_data


def extract_overrepresented(content: str) -> List[Dict[str, str]]:
    """Extract overrepresented sequences."""
    overrep = []
    
    section = extract_section(content, "Overrepresented sequences")
    if not section:
        return overrep
    
    lines = section.strip().split('\n')[1:]
    
    for line in lines:
        if line.startswith('>>END_MODULE') or line.startswith('#'):
            break
        parts = line.split('\t')
        if len(parts) >= 4:
            overrep.append({
                "sequence": parts[0].strip(),
                "count": parts[1].strip(),
                "percentage": parts[2].strip(),
                "source": parts[3].strip()
            })
    
    return overrep


def extract_adapter_content(content: str) -> Dict[str, Any]:
    """Extract adapter content information."""
    adapter_data = {"positions": [], "max_percentage": 0.0}
    
    section = extract_section(content, "Adapter Content")
    if not section:
        return adapter_data
    
    lines = section.strip().split('\n')[1:]
    max_pct = 0.0
    
    for line in lines:
        if line.startswith('>>END_MODULE'):
            break
        parts = line.split('\t')
        if len(parts) >= 2:
            try:
                position = parts[0].strip()
                # Get max value across all adapter columns
                percentages = [float(p) for p in parts[1:] if p.strip()]
                if percentages:
                    max_pct = max(max_pct, max(percentages))
            except (ValueError, IndexError):
                continue
    
    adapter_data["max_percentage"] = max_pct
    
    return adapter_data


def extract_section(content: str, section_name: str) -> Optional[str]:
    """
    Extract a specific section from FastQC data.
    
    Args:
        content: Full FastQC data content
        section_name: Name of the section to extract
        
    Returns:
        Section content or None if not found
    """
    pattern = rf'>>{section_name}\s+.*?\n(.*?)(?=>>|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1)
    
    return None
