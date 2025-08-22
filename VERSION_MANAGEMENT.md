# Version Management Guide

This project includes automated version management that handles semantic versioning without adding files to your local workspace.

## 🚀 Automated Version Management

### Automatic Detection
The system automatically detects when version bumps are needed based on:

- **Commit messages with conventional format**:
  - `fix:` or `patch:` → patch version bump (1.0.0 → 1.0.1)
  - `feat:` or `minor:` → minor version bump (1.0.0 → 1.1.0) 
  - `BREAKING` or `major:` → major version bump (1.0.0 → 2.0.0)

- **Commit volume**: After 10+ commits without a release, automatically suggests patch bump

### Manual Triggering
Trigger version management manually via GitHub Actions:

1. **Go to**: Repository → Actions → "Automated Version Management"
2. **Click**: "Run workflow"
3. **Select**:
   - Version type: `patch` | `minor` | `major`
   - Custom version (optional)
   - Create release: `true` | `false`

## 🛠️ Manual Version Management

### Using the Version Manager Script

```bash
# Show current version info and suggestions
python scripts/version_manager.py --info

# Bump patch version (1.0.0 → 1.0.1)
python scripts/version_manager.py --bump patch

# Bump minor version (1.0.0 → 1.1.0)
python scripts/version_manager.py --bump minor

# Bump major version (1.0.0 → 2.0.0)  
python scripts/version_manager.py --bump major

# Set custom version
python scripts/version_manager.py --custom 1.5.2

# Full workflow: bump + branch + tag
python scripts/version_manager.py --bump patch --create-branch --push-branch --create-tag

# Dry run to see what would happen
python scripts/version_manager.py --bump minor --dry-run
```

### Manual Git Workflow

```bash
# 1. Create version branch
git checkout -b version-1.0.1

# 2. Update version in pyproject.toml
# Edit: version = "1.0.1"

# 3. Commit changes  
git add pyproject.toml
git commit -m "🚀 Bump version to 1.0.1"

# 4. Push version branch
git push origin version-1.0.1

# 5. Create and push tag
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

## 📋 What Happens During Version Management

### Automated Process:
1. **Detects** need for version bump based on commits/manual trigger
2. **Creates** version branch (e.g., `version-1.0.1`) 
3. **Updates** `pyproject.toml` version **server-side only**
4. **Updates** `src/__init__.py` version if present
5. **Commits** changes to version branch
6. **Creates** and pushes git tag (e.g., `v1.0.1`)
7. **Triggers** release workflow for PyPI/Docker publishing
8. **Creates** GitHub release with changelog

### Key Benefits:
- ✅ **No local files added** - All changes happen server-side
- ✅ **Clean version branches** - Separate branches for each version
- ✅ **Automatic releases** - PyPI and Docker Hub publishing
- ✅ **Semantic versioning** - Follows semver standards
- ✅ **Changelog integration** - Links to detailed changelogs

## 🎯 Version Branch Strategy

### Branch Naming:
- `version-1.0.1` - Patch releases
- `version-1.1.0` - Minor releases  
- `version-2.0.0` - Major releases

### Workflow:
1. **Development** happens on `main` branch
2. **Version branches** created automatically for releases
3. **Tags** created from version branches  
4. **Releases** published from tags
5. **Version branches** remain for reference

## 🔗 Integration with CI/CD

### Triggered Workflows:
- **Version Management** (`version-management.yml`) - Handles version bumping
- **Release** (`release.yml`) - Publishes to PyPI/Docker when tags are pushed
- **CI** (`ci.yml`) - Validates all changes
- **Pipeline Integration** - Maintains code quality

### Environment Variables:
The system respects these environment variables in CI:
- `GITHUB_TOKEN` - For creating releases and pushing tags
- `PYPI_API_TOKEN` - For publishing to PyPI  
- `DOCKER_USERNAME` / `DOCKER_PASSWORD` - For Docker Hub publishing

## 📚 Examples

### Scenario 1: Bug Fix Release
```bash
# Manual approach
python scripts/version_manager.py --bump patch --create-branch --create-tag

# Automatic approach  
# Commit with: "fix: resolve memory leak in pipeline processing"
# System auto-detects and creates patch release
```

### Scenario 2: Feature Release
```bash
# Manual approach
python scripts/version_manager.py --bump minor --create-branch --create-tag

# Automatic approach
# Commit with: "feat: add new MCP compliance checking tool"
# System auto-detects and creates minor release
```

### Scenario 3: Breaking Change Release
```bash
# Manual approach  
python scripts/version_manager.py --bump major --create-branch --create-tag

# Automatic approach
# Commit with: "BREAKING: refactor API to use MCP v2.0 protocol"
# System auto-detects and creates major release
```

## 🚨 Important Notes

### Version File Management:
- **pyproject.toml** - Primary version source
- **src/__init__.py** - Updated automatically if present
- **No local workspace pollution** - Changes happen in CI/CD only

### Release Automation:
- **Tags trigger releases** - Pushing `v*` tags automatically publishes
- **GitHub releases created** - With changelog and installation instructions
- **Multi-platform publishing** - PyPI packages + Docker images

### Branch Management:
- **Version branches persist** - Available for cherry-picking or reference
- **Clean main branch** - Development continues uninterrupted
- **No merge conflicts** - Version changes isolated to version branches

## 🔍 Troubleshooting

### Common Issues:

**Issue**: Version detection not working
**Solution**: Ensure commit messages follow conventional format (`fix:`, `feat:`, etc.)

**Issue**: Release workflow failing  
**Solution**: Check that `PYPI_API_TOKEN` and Docker secrets are configured

**Issue**: Permission errors in CI
**Solution**: Verify `GITHUB_TOKEN` has proper permissions for creating releases

**Issue**: Version branch conflicts
**Solution**: Each version gets a unique branch - conflicts are rare

### Getting Help:
- Check GitHub Actions logs for detailed error messages
- Review version manager script output for diagnostics
- Use `--dry-run` flag to preview changes before applying