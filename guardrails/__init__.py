"""
Guardrails Module - Security and Quality Validation Framework

Provides comprehensive security validation, quality checking,
and automated compliance monitoring for MCP systems.
"""

__version__ = "1.0.0"

import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SecurityIssue:
    """Represents a security issue found during validation"""
    severity: str  # "critical", "high", "medium", "low"
    category: str  # "injection", "hardcoded_secrets", "unsafe_paths", etc.
    file_path: str
    line_number: int
    description: str
    recommendation: str
    rule_id: str


@dataclass
class QualityIssue:
    """Represents a quality issue found during validation"""
    severity: str  # "error", "warning", "info"
    category: str  # "style", "complexity", "maintainability", etc.
    file_path: str
    line_number: int
    description: str
    recommendation: str
    rule_id: str


@dataclass
class ValidationResult:
    """Results from security and quality validation"""
    timestamp: str
    total_files_scanned: int
    security_issues: List[SecurityIssue]
    quality_issues: List[QualityIssue]
    compliance_score: float
    recommendations: List[str]
    scan_duration: float


class SecurityValidator:
    """Security validation and compliance checking"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_patterns = self._load_security_patterns()
    
    def _load_security_patterns(self) -> Dict[str, Dict]:
        """Load security validation patterns"""
        return {
            "hardcoded_secrets": {
                "patterns": [
                    r"password\s*=\s*['\"][^'\"]+['\"]",
                    r"api_key\s*=\s*['\"][^'\"]+['\"]",
                    r"secret\s*=\s*['\"][^'\"]+['\"]",
                    r"token\s*=\s*['\"][^'\"]+['\"]"
                ],
                "severity": "critical",
                "description": "Hardcoded secrets detected"
            },
            "unsafe_paths": {
                "patterns": [
                    r"os\.system\s*\(",
                    r"subprocess\.call\s*\(",
                    r"eval\s*\(",
                    r"exec\s*\("
                ],
                "severity": "high",
                "description": "Potentially unsafe system calls"
            },
            "sql_injection": {
                "patterns": [
                    r"\.execute\s*\(\s*['\"].*%.*['\"]",
                    r"\.query\s*\(\s*['\"].*\+.*['\"]"
                ],
                "severity": "critical",
                "description": "Potential SQL injection vulnerability"
            }
        }
    
    def validate_file(self, file_path: Path) -> List[SecurityIssue]:
        """Validate a single file for security issues"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for rule_id, rule_config in self.security_patterns.items():
                for pattern in rule_config["patterns"]:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            issue = SecurityIssue(
                                severity=rule_config["severity"],
                                category=rule_id,
                                file_path=str(file_path),
                                line_number=line_num,
                                description=f"{rule_config['description']} in line {line_num}",
                                recommendation=f"Review and secure the code at line {line_num}",
                                rule_id=rule_id
                            )
                            issues.append(issue)
        
        except Exception as e:
            self.logger.warning(f"Could not scan {file_path}: {e}")
        
        return issues
    
    def validate_directory(self, directory: Path) -> List[SecurityIssue]:
        """Validate all Python files in a directory"""
        all_issues = []
        
        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith('.'):
                continue
            issues = self.validate_file(py_file)
            all_issues.extend(issues)
        
        return all_issues


class QualityValidator:
    """Code quality validation and metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.quality_rules = self._load_quality_rules()
    
    def _load_quality_rules(self) -> Dict[str, Dict]:
        """Load quality validation rules"""
        return {
            "long_lines": {
                "max_length": 88,
                "severity": "warning",
                "description": "Line exceeds maximum length"
            },
            "complex_functions": {
                "max_complexity": 10,
                "severity": "warning", 
                "description": "Function complexity too high"
            },
            "missing_docstrings": {
                "severity": "info",
                "description": "Missing function docstring"
            },
            "unused_imports": {
                "severity": "warning",
                "description": "Unused import detected"
            }
        }
    
    def validate_file(self, file_path: Path) -> List[QualityIssue]:
        """Validate a single file for quality issues"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check line length
            for line_num, line in enumerate(lines, 1):
                if len(line) > self.quality_rules["long_lines"]["max_length"]:
                    issue = QualityIssue(
                        severity=self.quality_rules["long_lines"]["severity"],
                        category="style",
                        file_path=str(file_path),
                        line_number=line_num,
                        description=f"Line {line_num} exceeds {self.quality_rules['long_lines']['max_length']} characters",
                        recommendation="Break long line into multiple lines",
                        rule_id="long_lines"
                    )
                    issues.append(issue)
            
            # Check for missing docstrings in functions
            for line_num, line in enumerate(lines, 1):
                if re.match(r'^\s*def\s+\w+\s*\(', line):
                    # Check if next non-empty line is a docstring
                    next_lines = lines[line_num:line_num+3]
                    has_docstring = any('"""' in l or "'''" in l for l in next_lines)
                    
                    if not has_docstring:
                        issue = QualityIssue(
                            severity=self.quality_rules["missing_docstrings"]["severity"],
                            category="documentation",
                            file_path=str(file_path),
                            line_number=line_num,
                            description=f"Function at line {line_num} missing docstring",
                            recommendation="Add descriptive docstring to function",
                            rule_id="missing_docstrings"
                        )
                        issues.append(issue)
        
        except Exception as e:
            self.logger.warning(f"Could not scan {file_path}: {e}")
        
        return issues
    
    def validate_directory(self, directory: Path) -> List[QualityIssue]:
        """Validate all Python files in a directory for quality"""
        all_issues = []
        
        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith('.'):
                continue
            issues = self.validate_file(py_file)
            all_issues.extend(issues)
        
        return all_issues


class GuardrailsSystem:
    """Main guardrails system orchestrator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_validator = SecurityValidator()
        self.quality_validator = QualityValidator()
        
    def run_full_validation(self, target_path: str) -> ValidationResult:
        """Run complete security and quality validation"""
        start_time = datetime.now()
        target = Path(target_path)
        
        self.logger.info(f"Starting full validation of {target}")
        
        # Security validation
        security_issues = self.security_validator.validate_directory(target)
        
        # Quality validation  
        quality_issues = self.quality_validator.validate_directory(target)
        
        # Count files scanned
        total_files = len(list(target.rglob("*.py")))
        
        # Calculate compliance score
        total_issues = len(security_issues) + len(quality_issues)
        compliance_score = max(0, 100 - (total_issues * 2))  # Rough scoring
        
        # Generate recommendations
        recommendations = self._generate_recommendations(security_issues, quality_issues)
        
        scan_duration = (datetime.now() - start_time).total_seconds()
        
        result = ValidationResult(
            timestamp=datetime.now().isoformat(),
            total_files_scanned=total_files,
            security_issues=security_issues,
            quality_issues=quality_issues,
            compliance_score=compliance_score,
            recommendations=recommendations,
            scan_duration=scan_duration
        )
        
        self.logger.info(f"Validation complete. Found {len(security_issues)} security issues, "
                        f"{len(quality_issues)} quality issues. Compliance score: {compliance_score}%")
        
        return result
    
    def _generate_recommendations(self, 
                                 security_issues: List[SecurityIssue], 
                                 quality_issues: List[QualityIssue]) -> List[str]:
        """Generate actionable recommendations based on issues found"""
        recommendations = []
        
        # Security recommendations
        critical_security = [i for i in security_issues if i.severity == "critical"]
        if critical_security:
            recommendations.append(f"URGENT: Fix {len(critical_security)} critical security issues immediately")
        
        high_security = [i for i in security_issues if i.severity == "high"]
        if high_security:
            recommendations.append(f"Address {len(high_security)} high-priority security issues")
        
        # Quality recommendations  
        error_quality = [i for i in quality_issues if i.severity == "error"]
        if error_quality:
            recommendations.append(f"Fix {len(error_quality)} code quality errors")
        
        if len(quality_issues) > 50:
            recommendations.append("Consider implementing automated code formatting and linting")
        
        if not recommendations:
            recommendations.append("No critical issues found. Continue monitoring.")
        
        return recommendations
    
    def export_results(self, result: ValidationResult, output_path: str) -> bool:
        """Export validation results to JSON file"""
        try:
            import json
            output_file = Path(output_path)
            
            # Convert dataclasses to dicts for JSON serialization
            result_dict = {
                "timestamp": result.timestamp,
                "total_files_scanned": result.total_files_scanned,
                "security_issues": [
                    {
                        "severity": issue.severity,
                        "category": issue.category,
                        "file_path": issue.file_path,
                        "line_number": issue.line_number,
                        "description": issue.description,
                        "recommendation": issue.recommendation,
                        "rule_id": issue.rule_id
                    }
                    for issue in result.security_issues
                ],
                "quality_issues": [
                    {
                        "severity": issue.severity,
                        "category": issue.category,
                        "file_path": issue.file_path,
                        "line_number": issue.line_number,
                        "description": issue.description,
                        "recommendation": issue.recommendation,
                        "rule_id": issue.rule_id
                    }
                    for issue in result.quality_issues
                ],
                "compliance_score": result.compliance_score,
                "recommendations": result.recommendations,
                "scan_duration": result.scan_duration
            }
            
            with open(output_file, 'w') as f:
                json.dump(result_dict, f, indent=2)
            
            self.logger.info(f"Results exported to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")
            return False


# Main entry point for CLI usage
def main():
    """Main CLI entry point for guardrails system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP System Guardrails - Security & Quality Validation")
    parser.add_argument("target", help="Target directory to validate")
    parser.add_argument("--output", "-o", help="Output file for results (JSON)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run validation
    guardrails = GuardrailsSystem()
    result = guardrails.run_full_validation(args.target)
    
    # Print summary
    print(f"\n🛡️  Guardrails Validation Complete")
    print(f"📁 Files scanned: {result.total_files_scanned}")
    print(f"🚨 Security issues: {len(result.security_issues)}")
    print(f"⚠️  Quality issues: {len(result.quality_issues)}")
    print(f"📊 Compliance score: {result.compliance_score}%")
    print(f"⏱️  Scan duration: {result.scan_duration:.2f}s")
    
    if result.recommendations:
        print(f"\n📋 Recommendations:")
        for rec in result.recommendations:
            print(f"  • {rec}")
    
    # Export results if requested
    if args.output:
        success = guardrails.export_results(result, args.output)
        if success:
            print(f"\n💾 Results saved to {args.output}")
    
    # Exit with appropriate code
    critical_issues = [i for i in result.security_issues if i.severity == "critical"]
    if critical_issues:
        sys.exit(1)  # Critical security issues found
    else:
        sys.exit(0)  # Clean or manageable issues


if __name__ == "__main__":
    main()
