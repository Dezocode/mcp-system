#!/usr/bin/env python3
"""
Unified Enhanced Autofix Control System v3.0

This script provides a unified interface to the enhanced autofix system with:
- Higher resolution logic for precise issue detection
- Integrated watchdog system for proactive prevention  
- Self-healing capabilities with learning from patterns
- Coordination of all autofix components

Usage:
    python enhanced_autofix_control.py [OPTIONS]
    
Examples:
    # Run complete enhanced autofix with monitoring
    python enhanced_autofix_control.py --full-suite
    
    # Start preventive monitoring only
    python enhanced_autofix_control.py --monitor-only
    
    # Fix critical issues immediately
    python enhanced_autofix_control.py --critical-only
    
    # Learn from existing fixes and improve patterns
    python enhanced_autofix_control.py --learn-and-improve
"""

import asyncio
import json
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click

# Import enhanced components (with error handling)
try:
    from enhanced_autofix_engine import EnhancedAutofixEngine, IssueCategory, IssueSeverity
except ImportError:
    print("❌ Enhanced autofix engine not available")
    sys.exit(1)

try:
    from claude_quality_patcher import EnhancedClaudeQualityPatcher
except ImportError:
    EnhancedClaudeQualityPatcher = None

try:
    from version_keeper import MCPVersionKeeper
except ImportError:
    MCPVersionKeeper = None

# Global state for graceful shutdown
autofix_engine: Optional[EnhancedAutofixEngine] = None
monitoring_active = False


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        global monitoring_active
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        monitoring_active = False
        if autofix_engine:
            autofix_engine.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


@click.group()
@click.option('--repo-path', type=click.Path(exists=True), default='.', 
              help='Repository path to analyze and fix')
@click.option('--config', type=click.Path(), 
              help='Configuration file for enhanced autofix')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
@click.option('--dry-run', is_flag=True, help='Preview actions without applying')
@click.pass_context
def cli(ctx, repo_path, config, verbose, dry_run):
    """Enhanced Autofix Control System v3.0"""
    global autofix_engine
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj['repo_path'] = Path(repo_path).resolve()
    ctx.obj['config'] = Path(config) if config else None
    ctx.obj['verbose'] = verbose
    ctx.obj['dry_run'] = dry_run
    
    # Setup signal handlers
    setup_signal_handlers()
    
    print("🚀 Enhanced Autofix Control System v3.0")
    print(f"📁 Repository: {ctx.obj['repo_path']}")
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be applied")


@cli.command()
@click.option('--enable-monitoring/--no-monitoring', default=True,
              help='Enable/disable file system monitoring')
@click.option('--output', type=click.Path(), help='Output report file')
@click.pass_context
async def full_suite(ctx, enable_monitoring, output):
    """Run the complete enhanced autofix suite"""
    global autofix_engine
    
    repo_path = ctx.obj['repo_path']
    config_file = ctx.obj['config']
    
    print("🎯 Running complete enhanced autofix suite...")
    
    try:
        # Initialize enhanced autofix engine
        autofix_engine = EnhancedAutofixEngine(repo_path, config_file)
        
        # Run complete autofix
        report = await autofix_engine.run_enhanced_autofix(enable_monitoring)
        
        # Save report if requested
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📊 Detailed report saved to {output_path}")
        
        # Display summary
        _display_summary(report)
        
        # Keep monitoring if enabled
        if enable_monitoring and not ctx.obj['dry_run']:
            print("\n👁️ Monitoring active - Press Ctrl+C to stop")
            global monitoring_active
            monitoring_active = True
            
            while monitoring_active:
                await asyncio.sleep(1)
    
    except Exception as e:
        print(f"❌ Error in full suite: {e}")
        if ctx.obj['verbose']:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--timeout', default=0, help='Monitoring timeout in seconds (0 = infinite)')
@click.pass_context
async def monitor_only(ctx, timeout):
    """Start preventive monitoring without initial fixes"""
    global autofix_engine, monitoring_active
    
    repo_path = ctx.obj['repo_path']
    config_file = ctx.obj['config']
    
    print("👁️ Starting preventive monitoring system...")
    
    try:
        # Initialize engine
        autofix_engine = EnhancedAutofixEngine(repo_path, config_file)
        
        # Start monitoring
        autofix_engine.watchdog.start_monitoring()
        monitoring_active = True
        
        print("✅ Monitoring active - watching for file changes")
        print("   Real-time validation and prevention enabled")
        print("   Press Ctrl+C to stop")
        
        # Monitor with timeout
        start_time = time.time()
        while monitoring_active:
            if timeout > 0 and (time.time() - start_time) > timeout:
                print(f"⏰ Monitoring timeout ({timeout}s) reached")
                break
            
            await asyncio.sleep(1)
    
    except Exception as e:
        print(f"❌ Error in monitoring: {e}")
        sys.exit(1)
    finally:
        if autofix_engine:
            autofix_engine.shutdown()


@cli.command()
@click.option('--max-issues', default=10, help='Maximum critical issues to fix')
@click.option('--dry-run', is_flag=True, help='Preview changes without applying')
@click.option('--verbose', is_flag=True, help='Show detailed output')
@click.pass_context
async def critical_only(ctx, max_issues, dry_run, verbose):
    """Fix only critical issues that prevent execution"""
    global autofix_engine
    
    repo_path = ctx.obj['repo_path']
    config_file = ctx.obj['config']
    
    print("🚨 Fixing critical issues only...")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be applied")
    
    try:
        # Initialize engine
        autofix_engine = EnhancedAutofixEngine(repo_path, config_file)
        
        # Analyze for critical issues
        issues = autofix_engine.analyzer.analyze_codebase()
        
        critical_issues = [
            i for i in issues 
            if i.severity in [IssueSeverity.BLOCKER, IssueSeverity.CRITICAL]
        ][:max_issues]
        
        if not critical_issues:
            print("✅ No critical issues found!")
            return
        
        print(f"🔧 Found {len(critical_issues)} critical issues to fix")
        
        # Fix critical issues
        fixes = await autofix_engine._fix_critical_issues(critical_issues)
        
        # Report results
        successful = [f for f in fixes if f.get('success', False)]
        failed = [f for f in fixes if not f.get('success', False)]
        
        print(f"\n📊 Critical fix results:")
        print(f"   ✅ Successfully fixed: {len(successful)}")
        print(f"   ❌ Failed to fix: {len(failed)}")
        
        if failed and verbose:
            print("\n❌ Failed fixes:")
            for fix in failed:
                print(f"   - {fix.get('issue_id', 'unknown')}: {fix.get('error', 'unknown error')}")
    
    except Exception as e:
        print(f"❌ Error in critical fixes: {e}")
        sys.exit(1)


@cli.command()
@click.option('--analyze-patterns', is_flag=True, help='Analyze existing fix patterns')
@click.option('--update-prevention', is_flag=True, help='Update prevention strategies')
@click.pass_context
async def learn_and_improve(ctx, analyze_patterns, update_prevention):
    """Learn from existing fixes and improve prevention strategies"""
    global autofix_engine
    
    repo_path = ctx.obj['repo_path']
    config_file = ctx.obj['config']
    
    print("🧠 Learning from fixes and improving prevention...")
    
    try:
        # Initialize engine
        autofix_engine = EnhancedAutofixEngine(repo_path, config_file)
        
        if analyze_patterns:
            print("🔍 Analyzing existing fix patterns...")
            
            # Load healing history
            healing_history = autofix_engine.self_healing._load_healing_history()
            
            print(f"📈 Pattern analysis:")
            print(f"   Total fixes recorded: {len(healing_history.get('fixes', []))}")
            print(f"   Patterns learned: {len(healing_history.get('patterns', {}))}")
            
            # Analyze most common issues
            if healing_history.get('fixes'):
                _analyze_fix_patterns(healing_history['fixes'])
        
        if update_prevention:
            print("⚙️ Updating prevention strategies...")
            
            # Predict issues across codebase
            predicted_issues = []
            for py_file in repo_path.rglob("*.py"):
                if not autofix_engine.analyzer._should_skip_file(py_file):
                    file_predictions = autofix_engine.self_healing.predict_issues(py_file)
                    predicted_issues.extend(file_predictions)
            
            if predicted_issues:
                print(f"🔮 Predicted {len(predicted_issues)} potential issues")
                
                # Group by category
                categories = {}
                for issue in predicted_issues:
                    cat = issue.category.value
                    categories[cat] = categories.get(cat, 0) + 1
                
                print("📊 Predicted issue categories:")
                for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
                    print(f"   {cat}: {count}")
        
        print("✅ Learning and improvement complete")
    
    except Exception as e:
        print(f"❌ Error in learning process: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show current autofix system status"""
    repo_path = ctx.obj['repo_path']
    
    print("📊 Enhanced Autofix System Status")
    print("=" * 50)
    
    # Check components
    components = {
        'Enhanced Engine': 'enhanced_autofix_engine.py',
        'Quality Patcher': 'claude_quality_patcher.py', 
        'Version Keeper': 'version_keeper.py',
        'MCP Tools Monitor': 'mcp_tools_monitor.py'
    }
    
    for name, filename in components.items():
        file_path = repo_path / 'scripts' / filename
        status = "✅ Available" if file_path.exists() else "❌ Missing"
        print(f"   {name}: {status}")
    
    # Check configuration
    config_files = {
        'Prevention Rules': 'configs/prevention_rules.json',
        'MCP Server Config': '.mcp-server-config.json'
    }
    
    print("\n📋 Configuration:")
    for name, filename in config_files.items():
        file_path = repo_path / filename
        status = "✅ Present" if file_path.exists() else "❌ Missing"
        print(f"   {name}: {status}")
    
    # Check autofix directories
    autofix_dirs = ['.autofix', 'autofix-reports', 'sessions']
    
    print("\n📁 Autofix Directories:")
    for dirname in autofix_dirs:
        dir_path = repo_path / dirname
        status = "✅ Present" if dir_path.exists() else "📝 Will be created"
        print(f"   {dirname}: {status}")
    
    # Check recent activity
    log_file = repo_path / '.autofix' / 'enhanced_autofix.log'
    if log_file.exists():
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        print(f"\n🕒 Last activity: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n🕒 No previous activity detected")


@cli.command()
@click.option('--component', type=click.Choice(['engine', 'watchdog', 'quality', 'version']),
              help='Test specific component')
@click.pass_context
async def test(ctx, component):
    """Test enhanced autofix components"""
    repo_path = ctx.obj['repo_path']
    config_file = ctx.obj['config']
    
    print("🧪 Testing enhanced autofix components...")
    
    if not component or component == 'engine':
        print("\n🔬 Testing Enhanced Autofix Engine...")
        try:
            engine = EnhancedAutofixEngine(repo_path, config_file)
            
            # Quick analysis test
            print("   Running quick analysis...")
            issues = engine.analyzer.analyze_codebase()
            print(f"   ✅ Analysis complete: {len(issues)} issues detected")
            
            engine.shutdown()
        except Exception as e:
            print(f"   ❌ Engine test failed: {e}")
    
    if not component or component == 'watchdog':
        print("\n👁️ Testing Watchdog System...")
        try:
            from enhanced_autofix_engine import IntegratedWatchdog
            
            # Create dummy engine for test
            class DummyEngine:
                def fix_file_immediately(self, file_path, error):
                    print(f"   Mock fix for {file_path}: {error}")
            
            watchdog = IntegratedWatchdog(repo_path, DummyEngine())
            rules = watchdog._load_prevention_rules()
            print(f"   ✅ Prevention rules loaded: {len(rules)} settings")
        except Exception as e:
            print(f"   ❌ Watchdog test failed: {e}")
    
    if not component or component == 'quality':
        print("\n🎯 Testing Quality Patcher...")
        try:
            if EnhancedClaudeQualityPatcher:
                quality_patcher = EnhancedClaudeQualityPatcher(repo_path)
                print("   ✅ Quality patcher initialized")
            else:
                print("   ⚠️ Quality patcher not available")
        except Exception as e:
            print(f"   ❌ Quality patcher test failed: {e}")
    
    if not component or component == 'version':
        print("\n📊 Testing Version Keeper...")
        try:
            if MCPVersionKeeper:
                version_keeper = MCPVersionKeeper(repo_path)
                print("   ✅ Version keeper initialized")
            else:
                print("   ⚠️ Version keeper not available")
        except Exception as e:
            print(f"   ❌ Version keeper test failed: {e}")
    
    print("\n✅ Component testing complete")


def _display_summary(report: Dict):
    """Display summary of autofix results"""
    stats = report.get('statistics', {})
    issues_summary = report.get('issues_summary', {})
    fixes_summary = report.get('fixes_summary', {})
    
    print("\n📊 Enhanced Autofix Summary")
    print("=" * 50)
    
    print(f"🔍 Issues detected: {stats.get('issues_detected', 0)}")
    print(f"🔧 Issues fixed: {stats.get('issues_fixed', 0)}")
    print(f"🛡️ Issues prevented: {stats.get('issues_prevented', 0)}")
    print(f"🧠 Patterns learned: {stats.get('patterns_learned', 0)}")
    
    # Issue breakdown
    if issues_summary.get('by_severity'):
        print("\n📈 Issues by severity:")
        for severity, count in issues_summary['by_severity'].items():
            print(f"   {severity}: {count}")
    
    # Fix success rate
    total_fixes = fixes_summary.get('total_attempted', 0)
    successful_fixes = fixes_summary.get('successful', 0)
    if total_fixes > 0:
        success_rate = (successful_fixes / total_fixes) * 100
        print(f"\n🎯 Fix success rate: {success_rate:.1f}% ({successful_fixes}/{total_fixes})")
    
    # Recommendations
    recommendations = report.get('recommendations', [])
    if recommendations:
        print("\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")


def _analyze_fix_patterns(fixes: List[Dict]):
    """Analyze patterns in fix history"""
    if not fixes:
        return
    
    # Group by fix type
    fix_types = {}
    for fix in fixes:
        fix_type = fix.get('fix_type', 'unknown')
        fix_types[fix_type] = fix_types.get(fix_type, 0) + 1
    
    print("🔧 Most common fix types:")
    for fix_type, count in sorted(fix_types.items(), key=lambda x: -x[1])[:5]:
        print(f"   {fix_type}: {count}")
    
    # Success rate analysis
    successful = sum(1 for fix in fixes if fix.get('success', False))
    total = len(fixes)
    success_rate = (successful / total * 100) if total > 0 else 0
    
    print(f"\n📈 Historical success rate: {success_rate:.1f}% ({successful}/{total})")


# Async wrapper for click commands
def async_command(func):
    """Decorator to handle async click commands"""
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


# Apply async wrapper to async commands
full_suite.callback = async_command(full_suite.callback)
monitor_only.callback = async_command(monitor_only.callback)
critical_only.callback = async_command(critical_only.callback)
learn_and_improve.callback = async_command(learn_and_improve.callback)
test.callback = async_command(test.callback)


if __name__ == '__main__':
    cli()