"""
Command-line interface for trimora.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from . import __version__
from .utils import (
    check_dependencies,
    print_dependency_instructions,
    check_ollama_running,
    check_ollama_model,
    install_ollama_model,
    validate_fastq,
    get_file_size
)
from .optimizer import optimize_fastq
from .ai_model import load_prompt_template


console = Console()


def print_banner():
    """Print colorful ASCII banner."""
    console.print()
    console.print("[bold cyan]" + "═" * 70 + "[/bold cyan]")
    console.print("[bold magenta]" + r"""
  ████████╗██████╗ ██╗███╗   ███╗ ██████╗ ██████╗  █████╗ 
  ╚══██╔══╝██╔══██╗██║████╗ ████║██╔═══██╗██╔══██╗██╔══██╗
     ██║   ██████╔╝██║██╔████╔██║██║   ██║██████╔╝███████║
     ██║   ██╔══██╗██║██║╚██╔╝██║██║   ██║██╔══██╗██╔══██║
     ██║   ██║  ██║██║██║ ╚═╝ ██║╚██████╔╝██║  ██║██║  ██║
     ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
""" + "[/bold magenta]")
    console.print("[bold cyan]" + "═" * 70 + "[/bold cyan]")
    console.print("  [bold white]AI-Powered FASTQ Quality Control & Trimming[/bold white]")
    console.print("  [green]Version:[/green] [white]{}[/white]".format(__version__))
    console.print("  [yellow]Author:[/yellow]  [bold white]Govind Mangropa[/bold white]")
    console.print("  [blue]Lab:[/blue]     [bold cyan]Molynex Lab[/bold cyan]")
    console.print("[bold cyan]" + "═" * 70 + "[/bold cyan]")
    console.print()


def main():
    """Main entry point for trimora CLI."""
    parser = argparse.ArgumentParser(
        description="trimora - AI-powered FASTQ quality control and trimming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  trimora sample.fastq
  trimora sample_R1.fastq sample_R2.fastq
  trimora *.fastq -o output_directory
  trimora sample.fastq --threads 8 --max-iterations 5
  trimora input/*.fastq -o results/ --model llama3:8b

Author: Govind Mangropa, Molynex Lab
"""
    )
    
    parser.add_argument(
        'fastq_files',
        nargs='+',
        type=str,
        help='FASTQ file(s) to process (supports wildcards)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='./trimora_output',
        help='Output directory (default: ./trimora_output)'
    )
    
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=4,
        help='Number of threads/cores to use (default: 4)'
    )
    
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=3,
        help='Maximum optimization iterations (default: 3)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='llama3:8b',
        help='Ollama model to use (default: llama3:8b)'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        help='Path to custom prompt template file'
    )
    
    parser.add_argument(
        '--keep-intermediate',
        action='store_true',
        help='Keep intermediate iteration files (default: cleanup)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'trimora {__version__}'
    )
    
    args = parser.parse_args()
    
    # Print beautiful banner
    print_banner()
    
    # Show configuration
    console.print("[bold]⚙️  Configuration:[/bold]")
    console.print(f"  Threads: [cyan]{args.threads}[/cyan]")
    console.print(f"  Max iterations: [cyan]{args.max_iterations}[/cyan]")
    console.print(f"  AI model: [cyan]{args.model}[/cyan]")
    console.print(f"  Output directory: [cyan]{args.output}[/cyan]")
    console.print()
    
    # Check dependencies
    console.print("[bold]🔍 Checking dependencies...[/bold]")
    deps = check_dependencies()
    
    missing = [name for name, available in deps.items() if not available]
    
    if missing:
        console.print("[bold red]❌ Missing dependencies detected[/bold red]\n")
        print_dependency_instructions(missing)
        sys.exit(1)
    
    console.print("[green]✅ All dependencies found[/green]\n")
    
    # Check Ollama service
    console.print("[bold]🤖 Checking Ollama service...[/bold]")
    if not check_ollama_running():
        console.print("[bold red]❌ Ollama is not running[/bold red]")
        console.print("\nPlease start Ollama:")
        console.print("  [cyan]ollama serve[/cyan]\n")
        sys.exit(1)
    
    console.print("[green]✅ Ollama is running[/green]\n")
    
    # Check/install model
    console.print(f"[bold]📦 Checking for model: {args.model}...[/bold]")
    if not check_ollama_model(args.model):
        console.print(f"[yellow]⚠️  Model {args.model} not found[/yellow]")
        
        if console.input(f"Would you like to download {args.model}? (y/n): ").lower() == 'y':
            if not install_ollama_model(args.model):
                console.print("[bold red]❌ Failed to install model[/bold red]")
                sys.exit(1)
        else:
            console.print("[bold red]❌ Model required to proceed[/bold red]")
            sys.exit(1)
    
    console.print(f"[green]✅ Model {args.model} available[/green]\n")
    
    # Load custom prompt if specified
    prompt_template = None
    if args.prompt:
        prompt_path = Path(args.prompt)
        if prompt_path.exists():
            prompt_template = load_prompt_template(prompt_path)
            console.print(f"[green]✅ Loaded custom prompt from {args.prompt}[/green]\n")
        else:
            console.print(f"[yellow]⚠️  Prompt file not found: {args.prompt}[/yellow]")
            console.print("[yellow]Using default prompt[/yellow]\n")
    
    # Validate input files
    fastq_paths = []
    for fastq_file in args.fastq_files:
        path = Path(fastq_file)
        if not path.exists():
            console.print(f"[bold red]❌ File not found: {fastq_file}[/bold red]")
            sys.exit(1)
        
        if not validate_fastq(path):
            console.print(f"[bold red]❌ Invalid FASTQ format: {fastq_file}[/bold red]")
            sys.exit(1)
        
        fastq_paths.append(path)
    
    console.print(f"[bold]📁 Processing {len(fastq_paths)} file(s)[/bold]\n")
    
    # Setup output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each file
    results = []
    
    for i, fastq_path in enumerate(fastq_paths, 1):
        console.print(f"\n[bold cyan]━━━ File {i}/{len(fastq_paths)}: {fastq_path.name} ({get_file_size(fastq_path)}) ━━━[/bold cyan]")
        
        # Create file-specific output directory
        file_output_dir = output_dir / fastq_path.stem
        
        # Run optimization
        result = optimize_fastq(
            input_fastq=fastq_path,
            output_dir=file_output_dir,
            model_name=args.model,
            max_iterations=args.max_iterations,
            prompt_template=prompt_template,
            threads=args.threads
        )
        
        results.append({
            "input_file": str(fastq_path),
            "success": result.success,
            "output_file": str(result.output_file) if result.output_file else None,
            "iterations": result.iterations,
            "final_parameters": result.final_parameters,
        })
        
        # Save detailed results
        if result.success:
            summary_file = file_output_dir / "summary.json"
            with open(summary_file, 'w') as f:
                json.dump({
                    "input_file": str(fastq_path),
                    "output_file": str(result.output_file),
                    "iterations": result.iterations,
                    "final_parameters": result.final_parameters,
                    "metrics_raw": result.metrics_raw,
                    "metrics_final": result.metrics_final,
                    "iteration_history": result.iteration_history
                }, f, indent=2)
            
            console.print(f"\n[green]✅ Success! Output: {result.output_file}[/green]")
            console.print(f"[green]📄 Summary saved: {summary_file}[/green]")
    
    # Final summary
    console.print("\n[bold cyan]╔════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║[/bold cyan]          [bold white]Processing Complete[/bold white]          [bold cyan]║[/bold cyan]")
    console.print("[bold cyan]╚════════════════════════════════════════╝[/bold cyan]\n")
    
    successful = sum(1 for r in results if r["success"])
    console.print(f"[bold]Total files: {len(results)}[/bold]")
    console.print(f"[green]Successful: {successful}[/green]")
    console.print(f"[red]Failed: {len(results) - successful}[/red]")
    console.print(f"\n[bold]Output directory:[/bold] {output_dir}\n")
    
    # Save overall summary
    summary_path = output_dir / "trimora_summary.json"
    with open(summary_path, 'w') as f:
        json.dump({
            "total_files": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "model_used": args.model,
            "max_iterations": args.max_iterations,
            "results": results
        }, f, indent=2)
    
    console.print(f"[bold]📊 Overall summary:[/bold] {summary_path}\n")
    
    sys.exit(0 if successful == len(results) else 1)


if __name__ == "__main__":
    main()
