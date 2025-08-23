#!/usr/bin/env bash

# GitHub CLI Branch Monitor
# Usage: gh-branch-monitor.sh [options]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
SHOW_REMOTE=true
SHOW_STATUS=true
CONTINUOUS=false
INTERVAL=30

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--continuous)
            CONTINUOUS=true
            shift
            ;;
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -h|--help)
            echo "GitHub CLI Branch Monitor"
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -c, --continuous    Run continuously"
            echo "  -i, --interval NUM  Refresh interval in seconds (default: 30)"
            echo "  -h, --help          Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

show_branch_info() {
    clear
    echo -e "${BLUE}GitHub Branch Monitor${NC}"
    echo -e "${BLUE}=====================${NC}"
    echo ""
    
    # Repository info
    REPO_NAME=$(gh repo view --json name --jq -r .name 2>/dev/null || echo "Unknown")
    DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef --jq -r .defaultBranchRef.name 2>/dev/null || echo "main")
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "Unknown")
    
    echo -e "${GREEN}Repository:${NC} $REPO_NAME"
    echo -e "${GREEN}Default Branch:${NC} $DEFAULT_BRANCH"
    echo -e "${YELLOW}Current Branch:${NC} $CURRENT_BRANCH"
    echo ""
    
    # Branch comparison
    if [[ "$CURRENT_BRANCH" != "$DEFAULT_BRANCH" ]]; then
        echo -e "${BLUE}Branch Comparison:${NC}"
        AHEAD=$(git rev-list --count HEAD..origin/$DEFAULT_BRANCH 2>/dev/null || echo "0")
        BEHIND=$(git rev-list --count origin/$DEFAULT_BRANCH..HEAD 2>/dev/null || echo "0")
        
        if [[ $BEHIND -gt 0 ]]; then
            echo -e "  ${GREEN}Ahead by $BEHIND commits${NC}"
        fi
        if [[ $AHEAD -gt 0 ]]; then
            echo -e "  ${RED}Behind by $AHEAD commits${NC}"
        fi
        if [[ $AHEAD -eq 0 && $BEHIND -eq 0 ]]; then
            echo -e "  ${GREEN}Up to date${NC}"
        fi
        echo ""
    fi
    
    # Recent commits
    echo -e "${BLUE}Recent Commits:${NC}"
    git log --oneline -5 --color=always 2>/dev/null || echo "No commits found"
    echo ""
    
    # Git status
    echo -e "${BLUE}Working Directory:${NC}"
    git status --short --branch 2>/dev/null || echo "No git status available"
    echo ""
    
    # Remote branches
    echo -e "${BLUE}Remote Branches:${NC}"
    gh api repos/:owner/:repo/branches --jq '.[] | "  " + .name + (if .protected then " (protected)" else "" end)' 2>/dev/null | head -10 || echo "Unable to fetch remote branches"
    
    if $CONTINUOUS; then
        echo ""
        echo -e "${YELLOW}Refreshing in $INTERVAL seconds... (Ctrl+C to exit)${NC}"
    fi
}

# Main execution
if $CONTINUOUS; then
    while true; do
        show_branch_info
        sleep $INTERVAL
    done
else
    show_branch_info
fi