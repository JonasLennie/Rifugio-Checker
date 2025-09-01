#!/bin/bash
# Development Environment Setup Script
# Supports both conda and virtualenv approaches

set -e  # Exit on error

echo "🏔️ Rifugio Monitor - Development Environment Setup"
echo "=================================================="

# Check if conda is available
if command -v conda &> /dev/null; then
    echo "✅ Conda found - using conda environment"
    
    # Create conda environment
    if conda env list | grep -q "rifugio-monitor"; then
        echo "📦 Environment 'rifugio-monitor' already exists"
        echo "   To recreate: conda env remove -n rifugio-monitor"
    else
        echo "📦 Creating conda environment..."
        conda env create -f environment.yml
        echo "✅ Conda environment created successfully"
    fi
    
    echo ""
    echo "🚀 To activate the environment:"
    echo "   conda activate rifugio-monitor"
    echo ""
    echo "🧪 To run tests:"
    echo "   pytest tests/ -v --cov=src"
    echo ""
    echo "▶️  To run the monitor:"
    echo "   cd src && python monitor.py"
    
else
    echo "⚠️  Conda not found - using Python venv instead"
    
    # Create virtual environment
    if [ -d "venv" ]; then
        echo "📦 Virtual environment 'venv' already exists"
        echo "   To recreate: rm -rf venv"
    else
        echo "📦 Creating Python virtual environment..."
        python3 -m venv venv
        echo "✅ Virtual environment created"
    fi
    
    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    echo "✅ Dependencies installed"
    
    # Install pre-commit hooks
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        echo "✅ Pre-commit hooks installed"
    fi
    
    echo ""
    echo "🚀 To activate the environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "🧪 To run tests:"
    echo "   source venv/bin/activate && pytest tests/ -v --cov=src"
    echo ""
    echo "▶️  To run the monitor:"
    echo "   source venv/bin/activate && cd src && python monitor.py"
fi

echo ""
echo "🔧 Environment Variables Required:"
echo "   export EMAIL_FROM='your@gmail.com'"
echo "   export EMAIL_TO='notify@example.com'"
echo "   export EMAIL_PASSWORD='your-app-password'"
echo "   export TARGET_DATES='2025-09-12,2025-09-21'"
echo ""
echo "📝 Quick test commands:"
echo "   make test          # Run tests"
echo "   make test-cov      # Run tests with coverage"
echo "   make lint          # Run linting"
echo "   make format        # Format code"
echo "   make check-env     # Check environment variables"
echo "   make test-email    # Test email connection"
echo ""
echo "✅ Development environment setup complete!"