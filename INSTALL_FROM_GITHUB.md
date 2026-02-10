# Installing Trimora from GitHub

**Install and run trimora directly from GitHub without PyPI**

---

## 🚀 Method 1: Direct Install from GitHub (Easiest)

Install directly using pip:

```bash
pip install git+https://github.com/govindab34/Trimora.git
```

Then run:

```bash
trimora --version
trimora --help
trimora sample.fastq
```

---

## 🛠️ Method 2: Clone and Install (For Development)

### Step 1: Clone the Repository

```bash
git clone https://github.com/govindab34/Trimora.git
cd Trimora
```

### Step 2: Install in Development Mode

```bash
pip install -e .
```

**Or in a virtual environment (recommended):**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install trimora
pip install -e .
```

### Step 3: Run Trimora

```bash
trimora --version
trimora sample.fastq
trimora *.fastq -o results/ --threads 8
```

---

## 🔄 Update to Latest Version

### If installed via Method 1:

```bash
pip install --upgrade git+https://github.com/govindab34/Trimora.git
```

### If installed via Method 2:

```bash
cd Trimora
git pull origin main
pip install -e . --force-reinstall
```

---

## 📦 Install Specific Version/Branch

### Install specific release tag:

```bash
pip install git+https://github.com/govindab34/Trimora.git@v1.0.0
```

### Install specific branch:

```bash
pip install git+https://github.com/govindab34/Trimora.git@main
```

---

## 🧪 Run Without Installing (Quick Test)

```bash
# Clone first
git clone https://github.com/govindab34/Trimora.git
cd Trimora

# Install dependencies only
pip install requests rich

# Run directly
python -m trimora.cli sample.fastq
```

---

## ✅ Verify Installation

```bash
# Check version
trimora --version

# Check dependencies
python -c "from trimora.utils import check_dependencies; print(check_dependencies())"

# Run help
trimora --help
```

---

## 🔧 Troubleshooting

### "command not found: trimora"

Make sure pip's bin directory is in your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Then reload
source ~/.bashrc
```

### "ModuleNotFoundError"

Install dependencies:

```bash
pip install requests rich
```

### Using system Python (externally managed)

Use virtual environment:

```bash
python3 -m venv trimora_env
source trimora_env/bin/activate
pip install git+https://github.com/govindab34/Trimora.git
```

---

## 🌐 Full Example Workflow

```bash
# 1. Install from GitHub
pip install git+https://github.com/govindab34/Trimora.git

# 2. Verify installation
trimora --version

# 3. Process FASTQ files
trimora my_sample.fastq -o results/ --threads 8

# 4. Check results
ls -lh results/
```

---

## 📚 Compare: PyPI vs GitHub

| Method              | Command                         | Use Case                 |
| ------------------- | ------------------------------- | ------------------------ |
| **PyPI**            | `pip install trimora`           | Stable releases          |
| **GitHub**          | `pip install git+https://...`   | Latest code, development |
| **Clone + Develop** | `git clone && pip install -e .` | Contributing, testing    |

---

**Ready to use!** Install directly from GitHub and start processing FASTQ files! 🧬

_Govind Mangropa | Molynex Lab_
