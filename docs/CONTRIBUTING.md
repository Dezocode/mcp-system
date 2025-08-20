# Contributing to MCP System

Thank you for your interest in contributing to the MCP System! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ (Python 3.12+ recommended)
- Git
- Node.js 18+ (for TypeScript templates)
- Docker (optional, for testing containerized features)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/mcp-system.git
   cd mcp-system
   ```

2. **Set up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install development dependencies
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

3. **Install MCP System**
   ```bash
   ./install.sh
   ```

4. **Run Tests**
   ```bash
   pytest tests/
   ```

## 🏗️ Project Structure

```
mcp-system/
├── src/                     # Core source code
│   ├── install_mcp_system.py      # Main installer
│   ├── claude_code_mcp_bridge.py  # Claude integration
│   ├── auto_discovery_system.py   # Environment detection
│   ├── mcp-*.py                   # MCP components
│   └── claude-*.sh                # Shell scripts
├── docs/                    # Documentation
├── scripts/                 # Build and utility scripts
├── templates/              # Server templates
├── tests/                  # Test suite
├── .github/workflows/      # CI/CD workflows
├── install.sh             # One-click installer
├── requirements.txt       # Python dependencies
└── pyproject.toml         # Project configuration
```

## 🐛 Bug Reports

When filing bug reports, please include:

1. **Environment Information**
   - Operating system and version
   - Python version
   - MCP System version
   - Claude Code CLI version (if applicable)

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Error messages and logs

3. **Minimal Example**
   - Smallest possible code/configuration that reproduces the issue

**Template:**
```markdown
## Bug Description
Brief description of the issue

## Environment
- OS: macOS 14.5
- Python: 3.12.0
- MCP System: 1.0.0
- Claude Code: latest

## Steps to Reproduce
1. Run `mcp-universal create test-server`
2. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Error Messages
```
Any error output
```

## Additional Context
Any other relevant information
```

## ✨ Feature Requests

Feature requests are welcome! Please:

1. Check existing issues to avoid duplicates
2. Describe the feature and its use case
3. Explain why it would be valuable
4. Consider providing implementation ideas

## 🔧 Development Guidelines

### Code Style

We use automated formatting tools:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Run all checks
python scripts/check_code.py
```

### Coding Standards

1. **Python Code**
   - Follow PEP 8 style guide
   - Use type hints for all functions
   - Write docstrings for public APIs
   - Keep functions focused and testable

2. **Shell Scripts**
   - Use `#!/bin/bash` shebang
   - Set `set -e` for error handling
   - Quote variables properly
   - Include descriptive comments

3. **Documentation**
   - Use clear, concise language
   - Include examples for complex features
   - Update relevant docs with changes

### Testing

1. **Write Tests**
   ```bash
   # Run all tests
   pytest tests/
   
   # Run specific test file
   pytest tests/test_installer.py
   
   # Run with coverage
   pytest --cov=src tests/
   ```

2. **Test Categories**
   - Unit tests for individual functions
   - Integration tests for component interaction
   - End-to-end tests for complete workflows

3. **Test Structure**
   ```python
   def test_function_name():
       # Arrange
       setup_test_data()
       
       # Act
       result = function_under_test()
       
       # Assert
       assert result == expected_value
   ```

## 📝 Commit Guidelines

### Commit Message Format

```
type(scope): brief description

Longer description if needed

Fixes #123
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
git commit -m "feat(bridge): add auto-detection for Claude projects"
git commit -m "fix(installer): handle missing directories gracefully"
git commit -m "docs(readme): update installation instructions"
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update your fork**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests and checks**
   ```bash
   pytest tests/
   black src/ tests/
   isort src/ tests/
   mypy src/
   ```

3. **Update documentation** if needed

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Review Process

1. All PRs require at least one review
2. All tests must pass
3. Documentation must be updated for new features
4. Breaking changes require discussion

## 🏷️ Adding New Features

### Server Templates

To add a new server template:

1. **Create template directory**
   ```bash
   mkdir templates/my-new-template/
   ```

2. **Add template files**
   - `template.json` - Configuration
   - `{{name}}.py` - Main server file
   - `requirements.txt` - Dependencies
   - `README.md` - Template docs

3. **Update template registry**
   Add to `src/mcp_create_server.py`

### Upgrade Modules

To add a new upgrade module:

1. **Create module definition**
   ```json
   {
     "id": "my-module",
     "name": "My Module",
     "description": "Description of what it does",
     "version": "1.0.0",
     "compatibility": ["python-fastmcp"],
     "requirements": [],
     "conflicts": [],
     "files": {
       "src/my_feature.py": "module code here"
     },
     "commands": ["pip install my-dependency"],
     "rollback_commands": ["pip uninstall -y my-dependency"]
   }
   ```

2. **Test module installation**
   ```bash
   mcp-universal upgrade install test-server my-module --dry-run
   ```

## 🧪 Testing Strategy

### Test Environment Setup

```bash
# Create isolated test environment
python -m venv test-env
source test-env/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Testing Checklist

- [ ] Unit tests for new functions
- [ ] Integration tests for component interaction
- [ ] End-to-end tests for user workflows
- [ ] Cross-platform testing (macOS, Linux, Windows)
- [ ] Performance testing for large projects
- [ ] Security testing for permissions and file access

## 📚 Documentation

### Documentation Types

1. **API Documentation** - In-code docstrings
2. **User Guides** - Step-by-step instructions
3. **Reference** - Complete feature reference
4. **Examples** - Real-world usage examples

### Writing Guidelines

- Use clear, simple language
- Include code examples
- Test all examples
- Update with feature changes

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Git tag created
- [ ] Release notes written

## 🤝 Community

### Getting Help

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and community chat
- **Discord** - Real-time community support (coming soon)

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and constructive
- Help others learn and grow
- Give credit where due
- Follow project guidelines

## 📞 Contact

- **Maintainer**: DezoCode
- **Email**: contact@dezocode.com
- **GitHub**: [@dezocode](https://github.com/dezocode)

---

Thank you for contributing to MCP System! Your efforts help make MCP server management better for everyone. 🙏