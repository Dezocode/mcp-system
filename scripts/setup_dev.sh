#!/bin/bash
#
# Development environment setup script
#

set -e

echo "🔧 Setting up MCP System development environment"

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git is required"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [[ $python_major -lt 3 ]] || [[ $python_major -eq 3 && $python_minor -lt 8 ]]; then
    echo "❌ Python 3.8+ required, found $python_version"
    exit 1
fi

echo "✅ Prerequisites OK (Python $python_version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🔨 Installing development dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🎣 Setting up pre-commit hooks..."
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.6.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF

pip install pre-commit
pre-commit install

# Create development environment file
echo "⚙️  Creating development environment..."
cp .env.example .env.dev

cat >> .env.dev << 'EOF'

# Development-specific settings
MCP_ENV=development
MCP_DEBUG=true
MCP_AUTO_RELOAD=true
MCP_LOG_LEVEL=debug
EOF

# Install MCP System in development mode
echo "🚀 Installing MCP System in development mode..."
./install.sh

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🚀 Quick start:"
echo "  source venv/bin/activate"
echo "  export PATH=\"\$HOME/bin:\$PATH\""
echo "  mcp-universal --help"
echo ""
echo "🧪 Run tests:"
echo "  pytest tests/"
echo ""
echo "🔧 Format code:"
echo "  black src/ tests/"
echo "  isort src/ tests/"
echo ""
echo "📝 Type check:"
echo "  mypy src/"