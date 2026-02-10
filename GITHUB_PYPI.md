# GitHub + PyPI Publication Guide

**Automatic PyPI Publishing via GitHub Actions**

Author: Govind Mangropa | Molynex Lab

---

## 🎯 Overview

This guide shows how to:

1. Push trimora to GitHub
2. Automatically publish to PyPI when you create a release

**Benefits:**

- ✅ No manual PyPI uploads
- ✅ Version control integrated
- ✅ Automatic builds on GitHub
- ✅ Professional workflow
- ✅ One command to publish

---

## 📋 Step 1: Create GitHub Repository

### Option A: Via GitHub Website

1. Go to: https://github.com/new
2. Repository name: `trimora`
3. Description: `AI-Powered FASTQ Quality Control & Trimming Tool`
4. Visibility: **Public** (required for PyPI)
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

You'll get a URL like: `https://github.com/govindab34/trimora`

---

## 🔧 Step 2: Initialize Git and Push to GitHub

Run these commands in your terminal:

```bash
# Navigate to trimora directory
cd "/home/gnmx/Desktop/wes_scripts /wgs/WGS _NEW/refastq/trimora"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial release: trimora v1.0.0

- AI-powered FASTQ quality control
- Local LLM integration via Ollama
- Iterative optimization engine
- Cross-platform CLI tool
- Complete documentation

Author: Govind Mangropa
Lab: Molynex Lab"

# Set main branch
git branch -M main

# Add GitHub remote (replace with YOUR GitHub username)
git remote add origin https://github.com/govindab34/trimora.git

# Push to GitHub
git push -u origin main
```

---

## 🔐 Step 3: Add PyPI API Token to GitHub Secrets

### Get PyPI API Token

1. Go to: https://pypi.org/account/register/ (or login if you have account)
2. Go to Account Settings → API tokens
3. Click "Add API token"
   - Token name: `trimora-github-actions`
   - Scope: "Entire account" (or limit to trimora project later)
4. **Copy the token** (starts with `pypi-...`)

### Add to GitHub Secrets

1. Go to your GitHub repository: `https://github.com/govindab34/trimora`
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**
5. Name: `PYPI_API_TOKEN`
6. Value: [paste your PyPI token]
7. Click **Add secret**

---

## 🚀 Step 4: Publish to PyPI (Automatic!)

### Method 1: Create a GitHub Release (Recommended)

1. Go to: `https://github.com/govindab34/trimora/releases`
2. Click **"Draft a new release"**
3. Click **"Choose a tag"** → Type `v1.0.0` → Click "Create new tag"
4. Release title: `trimora v1.0.0 - Initial Release`
5. Description:

   ````markdown
   ## 🎉 First Release of trimora!

   AI-Powered FASTQ Quality Control & Trimming Tool

   ### Features

   - 🤖 Local AI decision-making via Ollama
   - 🔄 Iterative quality optimization
   - ⚡ Multi-threaded processing
   - 📊 Comprehensive FastQC integration
   - 🎨 Beautiful CLI with branding

   ### Installation

   ```bash
   pip install trimora
   ```
   ````

   ### Quick Start

   ```bash
   trimora sample.fastq
   ```

   **Author:** Govind Mangropa  
   **Lab:** Molynex Lab

   ```

   ```

6. Click **"Publish release"**

**That's it!** GitHub Actions will automatically:

- Build the package
- Upload to PyPI
- Make it available worldwide

Watch progress: `https://github.com/govindab34/trimora/actions`

### Method 2: Manual Trigger

1. Go to: `https://github.com/govindab34/trimora/actions`
2. Click **"Publish to PyPI"** workflow
3. Click **"Run workflow"**
4. Select branch: `main`
5. Click **"Run workflow"**

---

## ✅ Step 5: Verify Publication

### Check PyPI

1. Visit: https://pypi.org/project/trimora/
2. Verify all information looks correct

### Test Installation

```bash
# In a fresh environment
pip install trimora
trimora --version
trimora --help
```

### Check GitHub Actions

Go to: `https://github.com/govindab34/trimora/actions`

You should see a green checkmark ✅ for the "Publish to PyPI" workflow.

---

## 🔄 Publishing Future Updates

### 1. Make Your Changes

```bash
# Edit code
vim trimora/cli.py

# Update version in TWO places:
# - pyproject.toml: version = "1.0.1"
# - trimora/__init__.py: __version__ = "1.0.1"
```

### 2. Commit and Push

```bash
git add .
git commit -m "Fix: Updated CLI help text"
git push
```

### 3. Create New Release

1. Go to: `https://github.com/govindab34/trimora/releases/new`
2. Tag: `v1.0.1`
3. Title: `trimora v1.0.1 - Bug Fixes`
4. Description: List changes
5. Click **"Publish release"**

**Done!** GitHub Actions automatically uploads the new version to PyPI.

---

## 📊 Complete Workflow Diagram

```
┌─────────────────┐
│  Code Changes   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  git commit     │
│  git push       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub Repo    │
└────────┬────────┘
         │
    Create Release (v1.0.0)
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
│ - Build package │
│ - Run twine     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PyPI.org       │
│  ✅ Published!  │
└─────────────────┘
         │
         ▼
    Users: pip install trimora
```

---

## 🛠️ Troubleshooting

### Error: "Repository not found"

**Fix:** Make sure you created the GitHub repository and the URL is correct

```bash
# Check current remote
git remote -v

# Update if wrong
git remote set-url origin https://github.com/YOUR_USERNAME/trimora.git
```

### Error: "Secret PYPI_API_TOKEN not found"

**Fix:** Add the secret to GitHub repository settings (see Step 3)

### Error: "File already exists on PyPI"

**Fix:** You cannot re-upload the same version

- Increment version number in `pyproject.toml` and `__init__.py`
- Create new release with new tag (e.g., `v1.0.1`)

### Workflow fails

1. Go to: `https://github.com/govindab34/trimora/actions`
2. Click the failed workflow
3. Click the failed job
4. Check error logs
5. Fix the issue, commit, and create new release

---

## 🎨 Add Badges to README

Add these to the top of your README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/trimora.svg)](https://badge.fury.io/py/trimora)
[![GitHub release](https://img.shields.io/github/v/release/govindab34/trimora)](https://github.com/govindab34/trimora/releases)
[![Build Status](https://github.com/govindab34/trimora/workflows/Publish%20to%20PyPI/badge.svg)](https://github.com/govindab34/trimora/actions)
[![Downloads](https://pepy.tech/badge/trimora)](https://pepy.tech/project/trimora)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

---

## 📝 Quick Reference

```bash
# Initial setup (once)
git init
git add .
git commit -m "Initial release"
git remote add origin https://github.com/govindab34/trimora.git
git push -u origin main

# For each update
# 1. Update version numbers
# 2. Make changes
git add .
git commit -m "Your change description"
git push

# 3. Create release on GitHub → Automatic PyPI upload!
```

---

## 🌟 Best Practices

1. **Version Numbering:** Follow SemVer (1.0.0, 1.0.1, 1.1.0, 2.0.0)
2. **Release Notes:** Always write clear descriptions
3. **Test First:** Create `v1.0.0-rc1` release candidate to test
4. **Tag Format:** Always use `vX.Y.Z` format (e.g., `v1.0.0`)
5. **Commit Messages:** Be descriptive about changes

---

## 🎓 Additional Resources

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **PyPI Publishing Guide:** https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
- **Semantic Versioning:** https://semver.org/

---

## ✅ Final Checklist

Before creating your first release:

- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] PyPI API token created
- [ ] Token added to GitHub Secrets as `PYPI_API_TOKEN`
- [ ] GitHub Actions workflow file exists (`.github/workflows/publish.yml`)
- [ ] Version number is correct in both files
- [ ] README.md is complete
- [ ] LICENSE file is included

---

**Now You Can:**

1. ✅ Push code to GitHub
2. ✅ Create a release
3. ✅ Automatically publish to PyPI
4. ✅ Share with the world! 🌍

**One command:** Create GitHub release → Package available on PyPI! 🚀

_Govind Mangropa | Molynex Lab | 2026_
