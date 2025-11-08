#!/bin/bash

# Formula 1 Analytics Setup Script
# This script sets up the project environment and loads initial data

echo "🏎️ Formula 1 Analytics Setup"
echo "============================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment (optional)
read -p "Create virtual environment? (y/n): " create_venv
if [ "$create_venv" = "y" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment activated!"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create data directory
echo ""
echo "Creating data directory..."
mkdir -p data

# Load data
echo ""
read -p "Load data from Ergast API? This may take 10-30 minutes (y/n): " load_data
if [ "$load_data" = "y" ]; then
    echo "Loading data from Ergast API..."
    echo "This may take a while due to API rate limiting..."
    python src/data_loader.py
fi

# Clean data
echo ""
read -p "Clean and prepare data? (y/n): " clean_data
if [ "$clean_data" = "y" ]; then
    echo "Cleaning and preparing data..."
    python src/data_cleaner.py
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run the Jupyter notebook: jupyter notebook notebooks/f1_analytics.ipynb"
echo "2. Launch the dashboard: streamlit run dashboards/app.py"
echo "3. Read the insights report: cat reports/f1_insights.md"

