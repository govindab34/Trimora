# Testing Trimora - Quick Start Guide

**Author:** Govind Mangropa | Molynex Lab

---

## ✅ Prerequisites Check

### 1. Check Ollama is Running

```bash
curl http://localhost:11434/api/tags
```

Should return JSON with models list. If you get "Connection refused", start Ollama:

```bash
ollama serve &
```

### 2. Check AI Model is Installed

```bash
ollama list
```

Should show `llama3:8b`. If not, install it:

```bash
ollama pull llama3:8b
```

### 3. Check FastQC

```bash
which fastqc
fastqc --version
```

### 4. Check fastp

```bash
which fastp
fastp --version
```

---

## 🧪 Test Installation

### Install Trimora

```bash
# From GitHub
pip install git+https://github.com/govindab34/Trimora.git

# OR from local directory
cd /home/gnmx/Desktop/wes_scripts\ /wgs/WGS\ _NEW/refastq/trimora
pip install -e .
```

### Verify Installation

```bash
trimora --version
# Should output: trimora 1.0.0

trimora --help
# Should show usage information
```

---

## 🚀 Run Test

### Create a Test FASTQ File

```bash
# Create a small test FASTQ
cat > test_sample.fastq << 'EOF'
@SEQ_ID_1
GATTTGGGGTTCAAAGCAGTATCGATCAAATAGTAAATCCATTTGTTCAACTCACAGTTT
+
!''*((((***+))%%%++)(%%%%).1***-+*''))**55CCF>>>>>>CCCCCCC65
@SEQ_ID_2
GATTTGGGGTTCAAAGCAGTATCGATCAAATAGTAAATCCATTTGTTCAACTCACAGTTT
+
!''*((((***+))%%%++)(%%%%).1***-+*''))**55CCF>>>>>>CCCCCCC65
@SEQ_ID_3
GATTTGGGGTTCAAAGCAGTATCGATCAAATAGTAAATCCATTTGTTCAACTCACAGTTT
+
!''*((((***+))%%%++)(%%%%).1***-+*''))**55CCF>>>>>>CCCCCCC65
@SEQ_ID_4
GATTTGGGGTTCAAAGCAGTATCGATCAAATAGTAAATCCATTTGTTCAACTCACAGTTT
+
!''*((((***+))%%%++)(%%%%).1***-+*''))**55CCF>>>>>>CCCCCCC65
@SEQ_ID_5
GATTTGGGGTTCAAAGCAGTATCGATCAAATAGTAAATCCATTTGTTCAACTCACAGTTT
+
!''*((((***+))%%%++)(%%%%).1***-+*''))**55CCF>>>>>>CCCCCCC65
EOF
```

### Run Trimora

```bash
trimora test_sample.fastq -o test_output --threads 4
```

### Expected Output

You should see:

```
═══════════════════════════════════════════════════════════════════
  ████████╗██████╗ ██╗███╗   ███╗ ██████╗ ██████╗  █████╗
  ╚══██╔══╝██╔══██╗██║████╗ ████║██╔═══██╗██╔══██╗██╔══██╗
     ██║   ██████╔╝██║██╔████╔██║██║   ██║██████╔╝███████║
     ██║   ██╔══██╗██║██║╚██╔╝██║██║   ██║██╔══██╗██╔══██║
     ██║   ██║  ██║██║██║ ╚═╝ ██║╚██████╔╝██║  ██║██║  ██║
     ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

  AI-Powered FASTQ Quality Control & Trimming
  Version: 1.0.0
  Author:  Govind Mangropa
  Lab:     Molynex Lab
═══════════════════════════════════════════════════════════════════

⚙️  Configuration:
  Threads: 4
  Max iterations: 3
  AI model: llama3:8b
  Output directory: test_output

🔍 Checking dependencies...
✅ All dependencies found

🤖 Checking Ollama service...
✅ Ollama is running

📦 Checking for model: llama3:8b...
✅ Model llama3:8b available

📁 Processing 1 file(s)

━━━ File 1/1: test_sample.fastq (360 B) ━━━

🔬 Processing: test_sample.fastq
📊 Running FastQC on raw file...
🤖 Generating parameters with AI...
✂️  Running fastp...
📊 Running FastQC on trimmed file...
✅ Optimization complete: 1 iteration(s)

✅ Success! Output: test_output/test_sample/test_sample_trimmed.fastq
📄 Summary saved: test_output/test_sample/summary.json
```

### Check Results

```bash
ls -lh test_output/test_sample/
cat test_output/test_sample/summary.json
```

---

## 📊 Test with Real Data

If you have real FASTQ files:

```bash
# Single file
trimora /path/to/sample.fastq -o results/

# Multiple files with more threads
trimora /path/to/data/*.fastq -o results/ --threads 16

# Maximum iterations for difficult samples
trimora sample.fastq --max-iterations 5 --threads 8
```

---

## 🛠️ Troubleshooting

### "Ollama is not running"

```bash
# Check if running
ps aux | grep ollama

# If not, start it
ollama serve &

# Wait a few seconds, then try trimora again
```

### "Model llama3:8b not found"

```bash
ollama pull llama3:8b
```

This downloads ~4.7GB, takes 5-10 minutes depending on connection.

### "FastQC not found" or "fastp not found"

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install fastqc fastp
```

**Or install via conda:**

```bash
conda install -c bioconda fastqc fastp
```

### Python module errors

```bash
pip install requests rich
```

---

## ✅ Success Indicators

After running trimora, you should have:

```
test_output/
└── test_sample/
    ├── test_sample_trimmed.fastq      # Your optimized FASTQ
    ├── raw_fastqc/                    # Quality before
    │   ├── fastqc_data.txt
    │   └── fastqc_report.html
    ├── trimmed_fastqc/                # Quality after
    │   ├── fastqc_data.txt
    │   └── fastqc_report.html
    ├── fastp_reports/                 # Trimming details
    │   ├── test_sample_trimmed_fastp.json
    │   └── test_sample_trimmed_fastp.html
    └── summary.json                   # Complete history
```

Open the HTML reports in a browser to see quality improvements!

---

## 🎓 Next Steps

1. ✅ Test with small file (done above)
2. ✅ Verify output files are generated
3. ✅ Review FastQC HTML reports
4. 🚀 Run on real sequencing data
5. 📊 Compare before/after quality metrics

---

**Trimora is ready to optimize your FASTQ files!** 🧬

_Govind Mangropa | Molynex Lab | 2026_
