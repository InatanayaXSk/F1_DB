#!/bin/bash

# F1 Prediction System Setup Script

echo "=========================================="
echo "F1 Prediction System Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p cache
mkdir -p models
mkdir -p telemetry_data
echo "✓ Directories created"
echo ""

# Initialize database
echo "Initializing database..."
python src/database.py
echo ""

# Create sample data
echo "Creating sample data..."
python demo.py
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Run Streamlit dashboard: streamlit run src/streamlit_app.py"
echo "  2. Train ML models: jupyter notebook notebooks/f1_ml_pipeline.ipynb"
echo "  3. Fetch F1 data (optional): python src/data_fetcher.py"
echo ""
