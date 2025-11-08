# GitHub Setup Guide for F1 Analytics Project

## Step-by-Step Instructions

### 1. Initialize Git Repository

```bash
cd /Users/niromikha/f1-analytics
git init
```

### 2. Add All Files

```bash
git add .
```

### 3. Make Initial Commit

```bash
git commit -m "Initial commit: Formula 1 Analytics project

- Complete EDA notebook with custom metrics
- Streamlit dashboard with 4 pages
- Data loading and cleaning modules
- ML prediction models
- Driver comparison tool
- Business insights report"
```

### 4. Create GitHub Repository

**Option A: Using GitHub Web Interface (Recommended)**
1. Go to https://github.com/new
2. Repository name: `f1-analytics` (or your preferred name)
3. Description: "Comprehensive Formula 1 data analytics project with EDA, dashboards, and ML models"
4. Choose **Public** (for portfolio) or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

**Option B: Using GitHub CLI**
```bash
gh repo create f1-analytics --public --description "Comprehensive Formula 1 data analytics project"
```

### 5. Connect Local Repository to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/f1-analytics.git
# Replace YOUR_USERNAME with your actual GitHub username
```

### 6. Push to GitHub

```bash
git branch -M main
git push -u origin main
```

## Optional: Add GitHub Actions Badge

If you want to add a badge to your README, you can add this at the top:

```markdown
![GitHub](https://img.shields.io/github/license/YOUR_USERNAME/f1-analytics)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
```

## Important Notes

### What NOT to Commit
- Large data files (CSV files in `data/` directory)
- Virtual environment (`venv/`)
- Model files (`.pkl`, `.joblib`)
- Jupyter notebook checkpoints

These are already in `.gitignore`, but double-check before committing.

### Recommended: Add Data Loading Instructions

Since data files are gitignored, make sure your README clearly explains:
1. How to load data using `data_loader.py`
2. That data will be downloaded from Ergast API
3. Expected time for data loading

### Optional Enhancements

1. **Add a LICENSE file:**
   ```bash
   # MIT License is common for portfolio projects
   ```

2. **Add Topics/Tags on GitHub:**
   - `data-analysis`
   - `formula1`
   - `python`
   - `streamlit`
   - `machine-learning`
   - `data-visualization`
   - `jupyter-notebook`

3. **Add a Project Description:**
   - Go to repository settings
   - Add a clear description
   - Add website URL if you have a portfolio site

4. **Pin the Repository:**
   - On your GitHub profile, pin this repository
   - It will appear at the top of your profile

## Quick Command Summary

```bash
# Navigate to project
cd /Users/niromikha/f1-analytics

# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: Formula 1 Analytics project"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/f1-analytics.git

# Push
git branch -M main
git push -u origin main
```

## Troubleshooting

### If you get authentication errors:
- Use GitHub Personal Access Token instead of password
- Or use SSH: `git remote set-url origin git@github.com:YOUR_USERNAME/f1-analytics.git`

### If data files are too large:
- They should already be gitignored
- If not, add `data/*.csv` to `.gitignore`

### If you need to update later:
```bash
git add .
git commit -m "Update: [describe changes]"
git push
```

