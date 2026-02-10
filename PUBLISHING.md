# Publishing Trimora to PyPI

**Complete Guide to Publishing on the Python Package Index**

Author: Govind Mangropa | Molynex Lab

---

## 📋 Prerequisites

Before publishing, ensure:

1. ✅ Package is complete and tested
2. ✅ `pyproject.toml` is properly configured
3. ✅ README.md is comprehensive
4. ✅ LICENSE file is included
5. ✅ Version number is set correctly

---

## 🔑 Step 1: Create PyPI Accounts

### Register on PyPI

1. **Production PyPI** (real package index):
   - Go to: https://pypi.org/account/register/
   - Create account and verify email

2. **Test PyPI** (for testing uploads):
   - Go to: https://test.pypi.org/account/register/
   - Create separate account and verify email

### Generate API Tokens (Recommended)

**For PyPI:**

1. Log in to https://pypi.org
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Name: `trimora-upload`
5. Scope: "Entire account" (or specific to trimora later)
6. Copy the token (starts with `pypi-...`)

**For Test PyPI:**

1. Log in to https://test.pypi.org
2. Repeat the same steps
3. Copy this token too

**⚠️ IMPORTANT:** Save these tokens securely! They won't be shown again.

---

## 🛠️ Step 2: Install Publishing Tools

```bash
# Install build tools
pip install --upgrade pip
pip install --upgrade build twine
```

**What these do:**

- `build`: Creates distribution packages (wheel + source)
- `twine`: Securely uploads packages to PyPI

---

## 📦 Step 3: Build Distribution Packages

Navigate to the trimora directory:

```bash
cd /home/gnmx/Desktop/wes_scripts\ /wgs/WGS\ _NEW/refastq/trimora
```

Build the package:

```bash
python3 -m build
```

**This creates:**

```
dist/
├── trimora-1.0.0-py3-none-any.whl    # Wheel distribution
└── trimora-1.0.0.tar.gz              # Source distribution
```

---

## 🧪 Step 4: Test Upload to Test PyPI (Recommended)

**Why Test PyPI?**

- Safe environment to test the upload process
- Won't pollute the real PyPI if something goes wrong
- Can verify installation works correctly

### Upload to Test PyPI

```bash
python3 -m twine upload --repository testpypi dist/*
```

**You'll be prompted for:**

- Username: `__token__`
- Password: Your Test PyPI API token (paste the `pypi-...` token)

### Verify on Test PyPI

1. Visit: https://test.pypi.org/project/trimora/
2. Check that all information looks correct
3. Review the README rendering

### Test Installation from Test PyPI

```bash
# Create a test environment
python3 -m venv test_env
source test_env/bin/activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    trimora

# Test it works
trimora --version
trimora --help

# Clean up
deactivate
rm -rf test_env
```

**Note:** The `--extra-index-url` is needed because Test PyPI doesn't have all dependencies (requests, rich), so it falls back to regular PyPI for those.

---

## 🚀 Step 5: Upload to Real PyPI

Once you've verified everything works on Test PyPI:

```bash
python3 -m twine upload dist/*
```

**You'll be prompted for:**

- Username: `__token__`
- Password: Your PyPI API token (paste the `pypi-...` token)

**Expected output:**

```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading trimora-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50.0/50.0 kB • 00:00
Uploading trimora-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 40.0/40.0 kB • 00:00

View at:
https://pypi.org/project/trimora/1.0.0/
```

---

## ✅ Step 6: Verify Publication

### Check PyPI Page

Visit: https://pypi.org/project/trimora/

Verify:

- ✅ Project description renders correctly
- ✅ Version number is correct
- ✅ Author information is displayed
- ✅ Dependencies are listed
- ✅ GitHub links work

### Test Installation

```bash
# In a fresh environment
python3 -m venv fresh_env
source fresh_env/bin/activate

# Install from PyPI
pip install trimora

# Test it
trimora --version
trimora --help

# Clean up
deactivate
```

---

## 🔄 Publishing Updates

When you release a new version:

### 1. Update Version Number

Edit `pyproject.toml`:

```toml
[project]
name = "trimora"
version = "1.0.1"  # ← Increment this
```

Also update in `trimora/__init__.py`:

```python
__version__ = "1.0.1"
```

### 2. Clean Old Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### 3. Rebuild

```bash
python3 -m build
```

### 4. Upload New Version

```bash
python3 -m twine upload dist/*
```

---

## 📝 Version Numbering Guide

Follow **Semantic Versioning** (SemVer):

```
MAJOR.MINOR.PATCH
```

- **MAJOR** (1.x.x): Breaking changes, incompatible API changes
- **MINOR** (x.1.x): New features, backward compatible
- **PATCH** (x.x.1): Bug fixes, backward compatible

**Examples:**

- `1.0.0` → Initial release
- `1.0.1` → Bug fix
- `1.1.0` → Added new CLI option
- `2.0.0` → Changed API, breaking changes

---

## 🔐 Security Best Practices

### Store API Tokens Securely

Create a `~/.pypirc` file:

```bash
nano ~/.pypirc
```

Add:

```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

**Set proper permissions:**

```bash
chmod 600 ~/.pypirc
```

**Now you can upload without being prompted:**

```bash
twine upload dist/*
```

---

## 🚨 Troubleshooting

### Error: "File already exists"

**Problem:** Version already uploaded to PyPI

**Solution:**

- You cannot re-upload the same version
- Increment version number and rebuild
- PyPI versions are immutable once published

### Error: "Invalid or non-existent authentication"

**Problem:** Wrong API token or format

**Solution:**

- Username must be exactly `__token__` (with double underscores)
- Password is your full token including `pypi-` prefix
- Check you're using the correct token (PyPI vs Test PyPI)

### Error: "The description failed to render"

**Problem:** Invalid README markdown

**Solution:**

- Test README rendering: `python3 -m readme_renderer README.md`
- Install: `pip install readme-renderer`
- Fix any markdown syntax errors

### Upload is slow or times out

**Problem:** Large package or slow connection

**Solution:**

- Ensure package size is reasonable
- Check your internet connection
- Try again later

---

## 📊 Post-Publication Checklist

After publishing to PyPI:

- [ ] Check package page renders correctly
- [ ] Test installation in fresh environment
- [ ] Test basic functionality works
- [ ] Update GitHub repository with PyPI badge
- [ ] Announce on social media / lab website
- [ ] Update documentation with installation instructions

---

## 🎨 Add PyPI Badge to README

Add this to the top of your README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/trimora.svg)](https://badge.fury.io/py/trimora)
[![Downloads](https://pepy.tech/badge/trimora)](https://pepy.tech/project/trimora)
```

---

## 📈 Monitoring Your Package

### View Download Statistics

- **PyPI Stats:** https://pypistats.org/packages/trimora
- **PePy Tech:** https://pepy.tech/project/trimora

### Monitor Issues

- Set up GitHub issues for bug reports
- Monitor PyPI project page for user feedback
- Check for security vulnerabilities: `pip-audit`

---

## 🎯 Quick Reference Commands

```bash
# One-time setup
pip install --upgrade build twine

# For each release
rm -rf dist/ build/ *.egg-info     # Clean
python3 -m build                    # Build
twine upload --repository testpypi dist/*  # Test (optional)
twine upload dist/*                 # Publish

# Verify
pip install trimora
trimora --version
```

---

## 🌟 Making Your Package Discoverable

### Add to README:

````markdown
## Installation

```bash
pip install trimora
```
````

### Share on:

- Bioinformatics forums
- Reddit: r/bioinformatics, r/Python
- Twitter/X with hashtags: #bioinformatics #python #genomics
- Your lab website
- GitHub Awesome Lists

### SEO Keywords in `pyproject.toml`:

```toml
keywords = [
    "bioinformatics",
    "fastq",
    "quality-control",
    "trimming",
    "ai",
    "sequencing",
    "genomics",
    "ngs"
]
```

---

## ✅ Final Checklist Before Publishing

- [ ] Package name is unique (search PyPI first)
- [ ] Version number follows SemVer
- [ ] README.md is complete and renders correctly
- [ ] LICENSE file is included
- [ ] Dependencies are correctly specified
- [ ] Package has been tested locally
- [ ] All code is committed to Git
- [ ] Created Git tag for version (e.g., `v1.0.0`)
- [ ] API token is ready
- [ ] Tested on Test PyPI

---

## 🎓 Additional Resources

- **PyPI Documentation:** https://packaging.python.org/
- **Twine Guide:** https://twine.readthedocs.io/
- **Python Packaging User Guide:** https://packaging.python.org/tutorials/packaging-projects/
- **Semantic Versioning:** https://semver.org/

---

**Ready to publish trimora to the world! 🚀**

_Govind Mangropa | Molynex Lab | 2026_
