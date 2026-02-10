"""
AI model interface using Ollama for parameter optimization.
"""

import json
import requests
from typing import Dict, Any, Optional
from pathlib import Path


def check_ollama_running() -> bool:
    """
    Check if Ollama service is running.
    
    Returns:
        True if Ollama is accessible, False otherwise
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def generate_parameters(
    fastqc_metrics: Dict[str, Any],
    model_name: str = "llama3:8b",
    prompt_template: Optional[str] = None,
    iteration: int = 1,
    previous_params: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Generate fastp parameters using local AI model.
    
    Args:
        fastqc_metrics: Parsed FastQC metrics
        model_name: Ollama model to use
        prompt_template: Custom prompt template (optional)
        iteration: Current iteration number
        previous_params: Parameters from previous iteration (if any)
        
    Returns:
        Dictionary of fastp parameters or None on failure
    """
    try:
        # Load prompt template
        if prompt_template is None:
            prompt_template = get_default_prompt()
        
        # Build the prompt
        prompt = build_prompt(
            prompt_template,
            fastqc_metrics,
            iteration,
            previous_params
        )
        
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistency
                    "top_p": 0.9,
                }
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Ollama API error: {response.status_code}")
            return None
        
        result = response.json()
        ai_response = result.get("response", "")
        
        # Parse JSON from response
        parameters = extract_json_from_response(ai_response)
        
        if parameters:
            return parameters
        else:
            print(f"⚠️  Failed to parse AI response, using defaults")
            return None
            
    except requests.exceptions.Timeout:
        print(f"❌ Ollama request timed out")
        return None
    except Exception as e:
        print(f"❌ AI generation error: {e}")
        return None


def build_prompt(
    template: str,
    metrics: Dict[str, Any],
    iteration: int,
    previous_params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build the complete prompt for the AI model.
    
    Args:
        template: Prompt template string
        metrics: FastQC metrics
        iteration: Current iteration number
        previous_params: Previous parameters if this is a retry
        
    Returns:
        Complete prompt string
    """
    # Summarize key metrics
    summary = summarize_metrics(metrics)
    
    prompt = template + "\n\n"
    prompt += "FASTQ Quality Metrics:\n"
    prompt += json.dumps(summary, indent=2)
    prompt += "\n\n"
    
    if iteration > 1 and previous_params:
        prompt += f"This is iteration {iteration}. Previous parameters did not fully resolve quality issues.\n"
        prompt += "Previous parameters:\n"
        prompt += json.dumps(previous_params, indent=2)
        prompt += "\n\nAdjust parameters to be more aggressive while minimizing data loss.\n\n"
    
    prompt += "Respond with ONLY a valid JSON object containing fastp parameters. No explanations."
    
    return prompt


def summarize_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a concise summary of FastQC metrics for the AI.
    
    Args:
        metrics: Full FastQC metrics dictionary
        
    Returns:
        Summarized metrics
    """
    summary = {
        "module_status": metrics.get("module_status", {}),
        "basic_statistics": metrics.get("basic_statistics", {}),
    }
    
    # Add key quality metrics
    per_base_qual = metrics.get("per_base_quality", {})
    if per_base_qual:
        summary["quality_summary"] = {
            "average_quality": per_base_qual.get("average_quality"),
            "min_quality": per_base_qual.get("min_quality"),
            "mean_scores": per_base_qual.get("mean_scores", [])[:10]  # First 10 positions
        }
    
    # Adapter content
    adapter = metrics.get("adapter_content", {})
    if adapter:
        summary["adapter_contamination"] = adapter.get("max_percentage", 0.0)
    
    # N content
    n_content = metrics.get("n_content", {})
    if n_content:
        summary["max_n_content"] = n_content.get("max_n_percent", 0.0)
    
    # Duplication
    dup = metrics.get("duplication", {})
    if dup:
        summary["duplication_level"] = dup.get("total_deduplicated_percentage", 0.0)
    
    # Overrepresented sequences
    overrep = metrics.get("overrepresented", [])
    if overrep:
        summary["overrepresented_count"] = len(overrep)
    
    return summary


def extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from AI response.
    
    Args:
        response: Raw AI response text
        
    Returns:
        Parsed JSON dictionary or None
    """
    # Try to find JSON in the response
    response = response.strip()
    
    # Look for JSON block markers
    if "```json" in response:
        start = response.find("```json") + 7
        end = response.find("```", start)
        if end != -1:
            response = response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        if end != -1:
            response = response[start:end].strip()
    
    # Try to find JSON object boundaries
    if '{' in response and '}' in response:
        start = response.find('{')
        end = response.rfind('}') + 1
        response = response[start:end]
    
    # Parse JSON
    try:
        data = json.loads(response)
        
        # Validate required fields
        if isinstance(data, dict):
            # Check that we have at least some trimming parameters
            expected_keys = {"quality", "length", "trim_front", "trim_tail", "adapter_trim"}
            if any(key in data for key in expected_keys):
                return data
        
        return None
        
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error: {e}")
        return None


def get_default_prompt() -> str:
    """
    Get the default system prompt template.
    
    Returns:
        Default prompt string
    """
    return """You are a bioinformatics quality control parameter optimizer for FASTQ sequencing data.

Your role: Analyze FastQC metrics and determine optimal fastp trimming parameters.

Input: JSON object containing FastQC quality metrics
Output: ONLY a valid JSON object with fastp parameters (no explanations)

Output format:
{
  "quality": <int>,
  "length": <int>,
  "trim_front": <int>,
  "trim_tail": <int>,
  "adapter_trim": <bool>,
  "poly_g_trim": <bool>
}

Guidelines:
1. Minimize data loss - be conservative
2. If average_quality >30: use quality=20, minimal trimming
3. If average_quality 25-30: use quality=22, light trimming
4. If average_quality <25: use quality=25, moderate trimming
5. If adapter_contamination >5%: enable adapter_trim=true
6. If adapter_contamination >15%: enable adapter_trim=true and trim_tail=10
7. If quality degrades at read ends: use trim_front/trim_tail appropriately
8. If max_n_content >5%: increase quality threshold
9. Default length threshold: 40bp minimum
10. For NextSeq data (polyG artifacts): enable poly_g_trim=true

Module Status Priority:
- FAIL in "Per base sequence quality" → Increase quality threshold or trim ends
- FAIL in "Adapter Content" → Enable adapter trimming and trim tail
- FAIL in "Per base N content" → Increase quality threshold
- WARN statuses → Apply moderate corrections

Respond ONLY with the JSON object, nothing else."""


def load_prompt_template(prompt_file: Path) -> str:
    """
    Load custom prompt template from file.
    
    Args:
        prompt_file: Path to prompt template file
        
    Returns:
        Prompt template string
    """
    try:
        with open(prompt_file, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  Failed to load prompt template: {e}")
        return get_default_prompt()
