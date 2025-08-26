#!/usr/bin/env python3
"""
Differential Restoration Engine for Pipeline MCP
Implements surgical code restoration to prevent accidental deletions
Matches the interactive mode's differential DIFF analysis capabilities
"""

import difflib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeDeletion:
    """Represents a detected code deletion"""
    file_path: str
    line_number: int
    deleted_content: str
    context_before: List[str]
    context_after: List[str]
    severity: str  # 'critical', 'important', 'minor'
    restoration_confidence: float  # 0.0 to 1.0


@dataclass
class RestorationPlan:
    """Plan for surgical code restoration"""
    deletions_detected: List[CodeDeletion]
    restorations_needed: List[CodeDeletion]
    edit_commands: List[Dict[str, Any]]
    summary: Dict[str, int]


class DifferentialRestoration:
    """
    Implements surgical code restoration to match interactive mode's capabilities.
    Detects unintended deletions and restores only necessary code.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.baseline_snapshots: Dict[str, List[str]] = {}
        self.critical_patterns = [
            r'def\s+\w+',  # Function definitions
            r'class\s+\w+',  # Class definitions
            r'import\s+',  # Import statements
            r'from\s+.*\s+import',  # From imports
            r'@\w+',  # Decorators
            r'if\s+__name__',  # Main guards
            r'async\s+def',  # Async functions
            r'try:',  # Try blocks
            r'except\s+',  # Exception handlers
        ]
        
    def capture_baseline(self, file_path: Path) -> None:
        """Capture baseline snapshot of file before fixes"""
        try:
            with open(file_path, 'r') as f:
                self.baseline_snapshots[str(file_path)] = f.readlines()
                logger.info(f"Captured baseline for {file_path}")
        except Exception as e:
            logger.error(f"Failed to capture baseline for {file_path}: {e}")
            
    def detect_deletions(self, file_path: Path) -> List[CodeDeletion]:
        """Detect code deletions by comparing to baseline"""
        deletions = []
        
        if str(file_path) not in self.baseline_snapshots:
            logger.warning(f"No baseline snapshot for {file_path}")
            return deletions
            
        try:
            with open(file_path, 'r') as f:
                current_lines = f.readlines()
                
            baseline_lines = self.baseline_snapshots[str(file_path)]
            
            # Use difflib to find differences
            differ = difflib.unified_diff(
                baseline_lines,
                current_lines,
                lineterm='',
                n=3  # Context lines
            )
            
            deletion_blocks = []
            current_block = []
            
            for line in differ:
                if line.startswith('-') and not line.startswith('---'):
                    # Line was deleted
                    current_block.append(line[1:])
                elif current_block:
                    # End of deletion block
                    deletion_blocks.append(current_block)
                    current_block = []
                    
            if current_block:
                deletion_blocks.append(current_block)
                
            # Analyze each deletion block
            for block in deletion_blocks:
                deletion = self._analyze_deletion_block(
                    file_path, block, baseline_lines
                )
                if deletion:
                    deletions.append(deletion)
                    
        except Exception as e:
            logger.error(f"Error detecting deletions in {file_path}: {e}")
            
        return deletions
        
    def _analyze_deletion_block(
        self, 
        file_path: Path, 
        block: List[str], 
        baseline_lines: List[str]
    ) -> Optional[CodeDeletion]:
        """Analyze a deletion block to determine severity and context"""
        
        # Find the line number in baseline
        block_text = ''.join(block)
        line_number = -1
        
        for i, line in enumerate(baseline_lines):
            if block[0].strip() in line:
                line_number = i + 1
                break
                
        if line_number == -1:
            return None
            
        # Determine severity based on content
        severity = self._assess_deletion_severity(block_text)
        
        # Get context
        context_before = baseline_lines[max(0, line_number-4):line_number-1]
        context_after = baseline_lines[line_number+len(block):min(len(baseline_lines), line_number+len(block)+3)]
        
        # Calculate restoration confidence
        confidence = self._calculate_restoration_confidence(block_text, severity)
        
        return CodeDeletion(
            file_path=str(file_path),
            line_number=line_number,
            deleted_content=block_text,
            context_before=context_before,
            context_after=context_after,
            severity=severity,
            restoration_confidence=confidence
        )
        
    def _assess_deletion_severity(self, content: str) -> str:
        """Assess the severity of a code deletion"""
        
        # Check for critical patterns
        for pattern in self.critical_patterns:
            if re.search(pattern, content):
                return 'critical'
                
        # Check for important patterns
        if any(keyword in content for keyword in ['return', 'raise', 'yield', 'await']):
            return 'important'
            
        # Default to minor
        return 'minor'
        
    def _calculate_restoration_confidence(self, content: str, severity: str) -> float:
        """Calculate confidence that deletion was unintended"""
        
        confidence = 0.5  # Base confidence
        
        # Adjust based on severity
        if severity == 'critical':
            confidence += 0.3
        elif severity == 'important':
            confidence += 0.2
            
        # Adjust based on content patterns
        if 'TODO' in content or 'FIXME' in content:
            confidence -= 0.2  # Might be intentional removal
            
        if 'deprecated' in content.lower():
            confidence -= 0.3  # Likely intentional
            
        # Check for complete function/class removal
        if re.search(r'^(def|class)\s+\w+.*:$', content, re.MULTILINE):
            confidence += 0.2  # Complete structure removal is suspicious
            
        return max(0.0, min(1.0, confidence))
        
    def create_restoration_plan(
        self, 
        deletions: List[CodeDeletion],
        threshold: float = 0.6
    ) -> RestorationPlan:
        """Create a surgical restoration plan for high-confidence deletions"""
        
        restorations_needed = [
            d for d in deletions 
            if d.restoration_confidence >= threshold
        ]
        
        # Sort by severity and line number
        restorations_needed.sort(
            key=lambda x: (
                {'critical': 0, 'important': 1, 'minor': 2}[x.severity],
                x.line_number
            )
        )
        
        # Generate Edit/MultiEdit commands
        edit_commands = self._generate_edit_commands(restorations_needed)
        
        # Create summary
        summary = {
            'total_deletions': len(deletions),
            'restorations_planned': len(restorations_needed),
            'critical_restorations': len([r for r in restorations_needed if r.severity == 'critical']),
            'important_restorations': len([r for r in restorations_needed if r.severity == 'important']),
            'minor_restorations': len([r for r in restorations_needed if r.severity == 'minor'])
        }
        
        return RestorationPlan(
            deletions_detected=deletions,
            restorations_needed=restorations_needed,
            edit_commands=edit_commands,
            summary=summary
        )
        
    def _generate_edit_commands(self, restorations: List[CodeDeletion]) -> List[Dict[str, Any]]:
        """Generate Claude-compatible Edit/MultiEdit commands"""
        
        commands = []
        
        # Group by file for MultiEdit efficiency
        by_file = {}
        for restoration in restorations:
            if restoration.file_path not in by_file:
                by_file[restoration.file_path] = []
            by_file[restoration.file_path].append(restoration)
            
        for file_path, file_restorations in by_file.items():
            if len(file_restorations) == 1:
                # Single edit
                r = file_restorations[0]
                commands.append({
                    'tool': 'Edit',
                    'file_path': r.file_path,
                    'old_string': ''.join(r.context_after[:1]) if r.context_after else '',
                    'new_string': r.deleted_content + (''.join(r.context_after[:1]) if r.context_after else ''),
                    'description': f"Restore {r.severity} deletion at line {r.line_number}"
                })
            else:
                # MultiEdit for multiple restorations in same file
                edits = []
                for r in file_restorations:
                    edits.append({
                        'old_string': ''.join(r.context_after[:1]) if r.context_after else '',
                        'new_string': r.deleted_content + (''.join(r.context_after[:1]) if r.context_after else ''),
                        'description': f"Restore {r.severity} deletion at line {r.line_number}"
                    })
                    
                commands.append({
                    'tool': 'MultiEdit',
                    'file_path': file_path,
                    'edits': edits,
                    'description': f"Restore {len(edits)} deletions in {Path(file_path).name}"
                })
                
        return commands
        
    def apply_restoration_plan(self, plan: RestorationPlan) -> Dict[str, Any]:
        """Apply the restoration plan and return results"""
        
        results = {
            'restorations_applied': 0,
            'restorations_failed': 0,
            'files_modified': set(),
            'errors': []
        }
        
        for command in plan.edit_commands:
            try:
                file_path = Path(command['file_path'])
                
                if command['tool'] == 'Edit':
                    # Apply single edit
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    new_content = content.replace(
                        command['old_string'],
                        command['new_string']
                    )
                    
                    with open(file_path, 'w') as f:
                        f.write(new_content)
                        
                    results['restorations_applied'] += 1
                    results['files_modified'].add(str(file_path))
                    
                elif command['tool'] == 'MultiEdit':
                    # Apply multiple edits
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    for edit in command['edits']:
                        content = content.replace(
                            edit['old_string'],
                            edit['new_string']
                        )
                        
                    with open(file_path, 'w') as f:
                        f.write(content)
                        
                    results['restorations_applied'] += len(command['edits'])
                    results['files_modified'].add(str(file_path))
                    
            except Exception as e:
                results['restorations_failed'] += 1
                results['errors'].append(f"Failed to apply restoration: {e}")
                logger.error(f"Restoration failed: {e}")
                
        results['files_modified'] = list(results['files_modified'])
        return results
        
    def get_restoration_report(self, plan: RestorationPlan) -> str:
        """Generate a detailed restoration report"""
        
        report = []
        report.append("=" * 60)
        report.append("DIFFERENTIAL RESTORATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("SUMMARY:")
        report.append(f"  Total deletions detected: {plan.summary['total_deletions']}")
        report.append(f"  Restorations planned: {plan.summary['restorations_planned']}")
        report.append(f"    - Critical: {plan.summary['critical_restorations']}")
        report.append(f"    - Important: {plan.summary['important_restorations']}")
        report.append(f"    - Minor: {plan.summary['minor_restorations']}")
        report.append("")
        
        # Detailed restorations
        if plan.restorations_needed:
            report.append("RESTORATIONS NEEDED:")
            for r in plan.restorations_needed:
                report.append(f"\n  File: {Path(r.file_path).name}")
                report.append(f"  Line: {r.line_number}")
                report.append(f"  Severity: {r.severity}")
                report.append(f"  Confidence: {r.restoration_confidence:.2f}")
                report.append(f"  Content: {r.deleted_content[:50]}...")
                
        # Edit commands
        report.append("\n" + "=" * 60)
        report.append(f"EDIT COMMANDS GENERATED: {len(plan.edit_commands)}")
        
        return '\n'.join(report)