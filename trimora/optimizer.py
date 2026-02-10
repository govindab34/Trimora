"""
Iterative optimization loop for FASTQ quality improvement.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from .fastqc import run_fastqc
from .parser import parse_fastqc_data
from .fastp import run_fastp, validate_parameters, get_default_parameters
from .ai_model import generate_parameters


class OptimizationResult:
    """Container for optimization results."""
    
    def __init__(
        self,
        success: bool,
        output_file: Optional[Path] = None,
        iterations: int = 0,
        final_parameters: Optional[Dict[str, Any]] = None,
        metrics_raw: Optional[Dict[str, Any]] = None,
        metrics_final: Optional[Dict[str, Any]] = None,
        iteration_history: Optional[List[Dict[str, Any]]] = None
    ):
        self.success = success
        self.output_file = output_file
        self.iterations = iterations
        self.final_parameters = final_parameters
        self.metrics_raw = metrics_raw
        self.metrics_final = metrics_final
        self.iteration_history = iteration_history or []


def optimize_fastq(
    input_fastq: Path,
    output_dir: Path,
    model_name: str = "llama3:8b",
    max_iterations: int = 3,
    prompt_template: Optional[str] = None,
    threads: int = 4
) -> OptimizationResult:
    """
    Iteratively optimize FASTQ file quality through AI-guided trimming.
    
    Args:
        input_fastq: Input FASTQ file path
        output_dir: Directory for all outputs
        model_name: Ollama model to use
        max_iterations: Maximum optimization iterations
        prompt_template: Custom AI prompt template
        
    Returns:
        OptimizationResult object
    """
    print(f"\n🔬 Processing: {input_fastq.name}")
    
    # Setup directories
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_qc_dir = output_dir / "raw_fastqc"
    trimmed_qc_dir = output_dir / "trimmed_fastqc"
    fastp_dir = output_dir / "fastp_reports"
    
    iteration_history = []
    
    # Step 1: Run FastQC on raw file
    print("📊 Running FastQC on raw file...")
    success, fastqc_data_path = run_fastqc(input_fastq, raw_qc_dir, threads=threads)
    
    if not success or not fastqc_data_path:
        print("❌ Initial FastQC failed")
        return OptimizationResult(success=False)
    
    # Parse raw metrics
    metrics_raw = parse_fastqc_data(fastqc_data_path)
    print_module_status(metrics_raw.get("module_status", {}), "Raw")
    
    # Check if already high quality
    if is_high_quality(metrics_raw):
        print("✅ File is already high quality, no trimming needed")
        return OptimizationResult(
            success=True,
            output_file=input_fastq,
            iterations=0,
            final_parameters={},
            metrics_raw=metrics_raw,
            metrics_final=metrics_raw
        )
    
    # Iterative optimization loop
    current_fastq = input_fastq
    current_metrics = metrics_raw
    best_metrics = metrics_raw
    best_params = None
    best_fastq = None
    
    for iteration in range(1, max_iterations + 1):
        print(f"\n🔄 Iteration {iteration}/{max_iterations}")
        
        # Generate parameters using AI
        print("🤖 Generating parameters with AI...")
        previous_params = iteration_history[-1]["parameters"] if iteration > 1 else None
        
        ai_params = generate_parameters(
            current_metrics,
            model_name=model_name,
            prompt_template=prompt_template,
            iteration=iteration,
            previous_params=previous_params
        )
        
        if ai_params is None:
            print("⚠️  AI failed, using default parameters")
            ai_params = get_default_parameters()
        
        # Validate and sanitize parameters
        params = validate_parameters(ai_params)
        params['threads'] = threads  # Set user-specified thread count
        print(f"📝 Parameters: quality={params['quality']}, length={params['length']}, "
              f"trim_front={params['trim_front']}, trim_tail={params['trim_tail']}, threads={threads}")
        
        # Run fastp
        print("✂️  Running fastp...")
        output_fastq = output_dir / f"{input_fastq.stem}_trimmed_iter{iteration}.fastq"
        
        success, fastp_report = run_fastp(
            current_fastq,
            output_fastq,
            params,
            fastp_dir
        )
        
        if not success:
            print(f"❌ fastp failed at iteration {iteration}")
            break
        
        # Run FastQC on trimmed file
        print("📊 Running FastQC on trimmed file...")
        iter_qc_dir = output_dir / f"trimmed_fastqc_iter{iteration}"
        success, fastqc_data_path = run_fastqc(output_fastq, iter_qc_dir, threads=threads)
        
        if not success or not fastqc_data_path:
            print(f"❌ FastQC failed at iteration {iteration}")
            break
        
        # Parse trimmed metrics
        trimmed_metrics = parse_fastqc_data(fastqc_data_path)
        print_module_status(trimmed_metrics.get("module_status", {}), f"Iteration {iteration}")
        
        # Record iteration
        iteration_data = {
            "iteration": iteration,
            "parameters": params,
            "metrics": trimmed_metrics,
            "output_file": str(output_fastq)
        }
        iteration_history.append(iteration_data)
        
        # Compare results
        improvement = compare_metrics(current_metrics, trimmed_metrics)
        print(f"📈 Improvement score: {improvement:.2f}")
        
        # Update best result
        if improvement > 0 or is_better_quality(trimmed_metrics, best_metrics):
            best_metrics = trimmed_metrics
            best_params = params
            best_fastq = output_fastq
            current_metrics = trimmed_metrics
            current_fastq = output_fastq
        
        # Check if we should continue
        if not should_continue(trimmed_metrics, iteration, max_iterations, improvement):
            break
    
    # Create final output
    if best_fastq:
        final_output = output_dir / f"{input_fastq.stem}_trimmed.fastq"
        if best_fastq != final_output:
            best_fastq.rename(final_output)
        
        print(f"\n✅ Optimization complete: {iteration} iteration(s)")
        
        return OptimizationResult(
            success=True,
            output_file=final_output,
            iterations=len(iteration_history),
            final_parameters=best_params,
            metrics_raw=metrics_raw,
            metrics_final=best_metrics,
            iteration_history=iteration_history
        )
    else:
        print("\n❌ Optimization failed")
        return OptimizationResult(success=False, metrics_raw=metrics_raw)


def is_high_quality(metrics: Dict[str, Any]) -> bool:
    """
    Check if FASTQ is already high quality.
    
    Args:
        metrics: FastQC metrics
        
    Returns:
        True if quality is already good
    """
    module_status = metrics.get("module_status", {})
    
    # Count failures and warnings
    fails = sum(1 for status in module_status.values() if status == "FAIL")
    warns = sum(1 for status in module_status.values() if status == "WARN")
    
    # If no failures and minimal warnings, quality is good
    return fails == 0 and warns <= 1


def is_better_quality(metrics1: Dict[str, Any], metrics2: Dict[str, Any]) -> bool:
    """
    Compare two quality metrics to determine which is better.
    
    Args:
        metrics1: First metrics
        metrics2: Second metrics
        
    Returns:
        True if metrics1 is better than metrics2
    """
    status1 = metrics1.get("module_status", {})
    status2 = metrics2.get("module_status", {})
    
    fails1 = sum(1 for status in status1.values() if status == "FAIL")
    fails2 = sum(1 for status in status2.values() if status == "FAIL")
    
    warns1 = sum(1 for status in status1.values() if status == "WARN")
    warns2 = sum(1 for status in status2.values() if status == "WARN")
    
    # Fewer failures is better
    if fails1 < fails2:
        return True
    elif fails1 > fails2:
        return False
    
    # If same failures, fewer warnings is better
    return warns1 < warns2


def compare_metrics(before: Dict[str, Any], after: Dict[str, Any]) -> float:
    """
    Calculate improvement score between two metrics.
    
    Args:
        before: Metrics before trimming
        after: Metrics after trimming
        
    Returns:
        Improvement score (positive = improvement)
    """
    score = 0.0
    
    status_before = before.get("module_status", {})
    status_after = after.get("module_status", {})
    
    # Compare module statuses
    for module in status_before:
        if module not in status_after:
            continue
        
        before_status = status_before[module]
        after_status = status_after[module]
        
        # Status hierarchy: PASS > WARN > FAIL
        status_values = {"PASS": 2, "WARN": 1, "FAIL": 0}
        
        before_val = status_values.get(before_status, 0)
        after_val = status_values.get(after_status, 0)
        
        score += (after_val - before_val) * 10
    
    # Compare average quality
    before_qual = before.get("per_base_quality", {}).get("average_quality", 0)
    after_qual = after.get("per_base_quality", {}).get("average_quality", 0)
    score += (after_qual - before_qual)
    
    return score


def should_continue(
    metrics: Dict[str, Any],
    iteration: int,
    max_iterations: int,
    improvement: float
) -> bool:
    """
    Determine if optimization should continue.
    
    Args:
        metrics: Current metrics
        iteration: Current iteration number
        max_iterations: Maximum allowed iterations
        improvement: Improvement score from last iteration
        
    Returns:
        True if should continue iterating
    """
    # Stop if max iterations reached
    if iteration >= max_iterations:
        print("🛑 Maximum iterations reached")
        return False
    
    # Stop if quality is now good
    if is_high_quality(metrics):
        print("✅ Quality targets achieved")
        return False
    
    # Stop if no improvement
    if improvement <= 0:
        print("🛑 No further improvement detected")
        return False
    
    return True


def print_module_status(module_status: Dict[str, str], label: str) -> None:
    """
    Print FastQC module status summary.
    
    Args:
        module_status: Module status dictionary
        label: Label for this status (e.g., "Raw", "Iteration 1")
    """
    if not module_status:
        return
    
    fails = [m for m, s in module_status.items() if s == "FAIL"]
    warns = [m for m, s in module_status.items() if s == "WARN"]
    passes = [m for m, s in module_status.items() if s == "PASS"]
    
    print(f"\n📋 {label} Quality Status:")
    print(f"  ✅ PASS: {len(passes)}")
    print(f"  ⚠️  WARN: {len(warns)}")
    print(f"  ❌ FAIL: {len(fails)}")
    
    if fails:
        print(f"  Failed modules: {', '.join(fails)}")
    if warns:
        print(f"  Warning modules: {', '.join(warns)}")
