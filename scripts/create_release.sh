#!/bin/bash
#
# Create release package for MCP System
#

set -e

VERSION=${1:-"1.0.0"}
RELEASE_DIR="releases/mcp-system-v$VERSION"

echo "🚀 Creating release package v$VERSION"

# Create release directory
mkdir -p "$RELEASE_DIR"

# Copy core files
cp -r src/ "$RELEASE_DIR/"
cp -r docs/ "$RELEASE_DIR/"
cp -r scripts/ "$RELEASE_DIR/"
cp -r templates/ "$RELEASE_DIR/"
cp -r .github/ "$RELEASE_DIR/"

cp install.sh "$RELEASE_DIR/"
cp requirements.txt "$RELEASE_DIR/"
cp pyproject.toml "$RELEASE_DIR/"
cp .env.example "$RELEASE_DIR/"
cp .gitignore "$RELEASE_DIR/"
cp Dockerfile "$RELEASE_DIR/"
cp .dockerignore "$RELEASE_DIR/"
cp LICENSE "$RELEASE_DIR/"
cp README.md "$RELEASE_DIR/"
cp CONTRIBUTING.md "$RELEASE_DIR/"

# Create version info
cat > "$RELEASE_DIR/VERSION" << EOF
MCP System v$VERSION
Built: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Commit: $(git rev-parse HEAD 2>/dev/null || echo "unknown")
EOF

# Create installation verification script
cat > "$RELEASE_DIR/verify_install.py" << 'EOF'
#!/usr/bin/env python3
"""Quick installation verification"""
import subprocess
import sys
from pathlib import Path

def verify():
    home = Path.home()
    if not (home / ".mcp-system").exists():
        print("❌ MCP System not installed")
        return False
    
    if not (home / "bin" / "mcp-universal").exists():
        print("❌ mcp-universal not found")
        return False
    
    print("✅ MCP System installation verified")
    return True

if __name__ == "__main__":
    sys.exit(0 if verify() else 1)
EOF

chmod +x "$RELEASE_DIR/verify_install.py"

# Create archive
cd releases/
tar -czf "mcp-system-v$VERSION.tar.gz" "mcp-system-v$VERSION/"
zip -r "mcp-system-v$VERSION.zip" "mcp-system-v$VERSION/"

echo "✅ Release package created:"
echo "   📦 releases/mcp-system-v$VERSION.tar.gz"
echo "   📦 releases/mcp-system-v$VERSION.zip"
echo "   📁 releases/mcp-system-v$VERSION/"

# Create checksums
cd ..
sha256sum "releases/mcp-system-v$VERSION.tar.gz" > "releases/mcp-system-v$VERSION.tar.gz.sha256"
sha256sum "releases/mcp-system-v$VERSION.zip" > "releases/mcp-system-v$VERSION.zip.sha256"

echo "✅ Checksums created"
echo ""
echo "🚀 Ready for distribution!"
echo ""
echo "Quick install command:"
echo "curl -sSL https://github.com/dezocode/mcp-system/releases/download/v$VERSION/mcp-system-v$VERSION.tar.gz | tar -xz && cd mcp-system-v$VERSION && ./install.sh"