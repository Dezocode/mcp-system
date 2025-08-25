#!/usr/bin/env python3
"""
Enhanced MCP Claude Pipeline Master Orchestrator v2.0
Master orchestrator with state machine, bidirectional communication, and intelligent recovery
Features: Protocol Integration, Performance Optimization, Error Recovery, Comprehensive Reporting

Author: DezoCode
Version: 2.0.0 Enhanced
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click

# Add scripts directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "scripts"))

try:
    from claude_agent_protocol import ClaudeAgentProtocol, TaskType, TaskStatus
    PROTOCOL_AVAILABLE = True
except ImportError:
    PROTOCOL_AVAILABLE = False
    print("⚠️  Claude Agent Protocol not available, running in basic mode")


class OrchestratorState(Enum):
    """Orchestrator state machine states"""
    INITIALIZING = "initializing"
    PROTOCOL_SETUP = "protocol_setup"
    ENVIRONMENT_ANALYSIS = "environment_analysis"
    PIPELINE_EXECUTION = "pipeline_execution"
    QUALITY_ASSURANCE = "quality_assurance"
    SECURITY_VALIDATION = "security_validation"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DEPLOYMENT_PREPARATION = "deployment_preparation"
    MONITORING_ACTIVE = "monitoring_active"
    ERROR_RECOVERY = "error_recovery"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionMode(Enum):
    """Execution modes for the orchestrator"""
    CONTINUOUS = "continuous"
    SINGLE_CYCLE = "single_cycle"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    RECOVERY = "recovery"


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator"""
    max_cycles: int = 100
    target_issues: int = 0
    execution_mode: ExecutionMode = ExecutionMode.CONTINUOUS
    enable_protocol: bool = True
    enable_monitoring: bool = True
    performance_tracking: bool = True
    auto_recovery: bool = True
    session_dir: Path = None
    log_level: str = "INFO"
    timeout_per_cycle: int = 600  # 10 minutes
    batch_size: int = 10
    adaptive_batch_sizing: bool = True


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0
    total_execution_time: float = 0.0
    average_cycle_time: float = 0.0
    issues_resolved: int = 0
    issues_remaining: int = 0
    success_rate: float = 0.0
    adaptive_batch_size: int = 10


class EnhancedMCPOrchestrator:
    """Enhanced MCP Pipeline Orchestrator with state machine and protocol integration"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.current_state = OrchestratorState.INITIALIZING
        self.state_history: List[Tuple[OrchestratorState, float]] = []
        
        # Setup paths
        self.session_dir = config.session_dir or Path.cwd() / "pipeline-sessions"
        self.session_dir.mkdir(exist_ok=True)
        
        self.state_file = self.session_dir / f"orchestrator-state-{self.session_id}.json"
        self.performance_file = self.session_dir / f"performance-{self.session_id}.json"
        self.log_file = self.session_dir / f"orchestrator-{self.session_id}.log"
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.protocol: Optional[ClaudeAgentProtocol] = None
        self.performance_metrics = PerformanceMetrics()
        self.is_running = False
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"Enhanced MCP Orchestrator initialized - Session: {self.session_id}")
    
    def setup_logging(self):
        """Setup enhanced logging"""
        self.logger = logging.getLogger(f"mcp_orchestrator_{self.session_id}")
        self.logger.setLevel(getattr(logging, self.config.log_level))
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.log_level))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.is_running = False
        self.transition_state(OrchestratorState.COMPLETED)
        self.save_state()
        sys.exit(0)
    
    def transition_state(self, new_state: OrchestratorState):
        """Transition to new state with logging and persistence"""
        old_state = self.current_state
        timestamp = time.time()
        
        self.state_history.append((old_state, timestamp))
        self.current_state = new_state
        
        self.logger.info(f"State transition: {old_state.value} -> {new_state.value}")
        self.save_state()
    
    def save_state(self):
        """Save current orchestrator state"""
        state_data = {
            "session_id": self.session_id,
            "current_state": self.current_state.value,
            "state_history": [(state.value, timestamp) for state, timestamp in self.state_history],
            "start_time": self.start_time,
            "current_time": time.time(),
            "config": asdict(self.config),
            "performance_metrics": asdict(self.performance_metrics),
            "recovery_attempts": self.recovery_attempts,
            "is_running": self.is_running
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state_data, f, indent=2, default=str)
    
    async def initialize_protocol(self) -> bool:
        """Initialize Claude Agent Protocol if available"""
        if not PROTOCOL_AVAILABLE or not self.config.enable_protocol:
            self.logger.warning("Protocol not available or disabled")
            return False
        
        try:
            self.protocol = ClaudeAgentProtocol(self.session_dir)
            self.logger.info("Claude Agent Protocol initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize protocol: {e}")
            return False
    
    async def execute_pipeline_cycle(self, cycle_number: int) -> bool:
        """Execute a single pipeline cycle with enhanced monitoring"""
        cycle_start_time = time.time()
        self.logger.info(f"Starting pipeline cycle {cycle_number}")
        
        try:
            # Create task if protocol available
            task = None
            if self.protocol:
                task = self.protocol.create_task(
                    TaskType.LINT_FIX,
                    context={
                        "cycle": cycle_number,
                        "mode": self.config.execution_mode.value,
                        "batch_size": self.performance_metrics.adaptive_batch_size
                    },
                    priority=1
                )
            
            # Execute pipeline components
            success = await self._execute_pipeline_components(cycle_number)
            
            # Update task status
            if self.protocol and task:
                if success:
                    self.protocol.record_observation(task.task_id, {
                        "status": "completed",
                        "cycle": cycle_number,
                        "execution_time": time.time() - cycle_start_time
                    })
                else:
                    self.protocol.record_observation(task.task_id, {
                        "status": "failed",
                        "cycle": cycle_number,
                        "execution_time": time.time() - cycle_start_time
                    })
            
            # Update performance metrics
            cycle_duration = time.time() - cycle_start_time
            self.performance_metrics.total_cycles += 1
            self.performance_metrics.total_execution_time += cycle_duration
            self.performance_metrics.average_cycle_time = (
                self.performance_metrics.total_execution_time / self.performance_metrics.total_cycles
            )
            
            if success:
                self.performance_metrics.successful_cycles += 1
            else:
                self.performance_metrics.failed_cycles += 1
            
            self.performance_metrics.success_rate = (
                self.performance_metrics.successful_cycles / self.performance_metrics.total_cycles * 100
            )
            
            # Adaptive batch sizing
            if self.config.adaptive_batch_sizing:
                self._adjust_batch_size(success, cycle_duration)
            
            self.logger.info(f"Cycle {cycle_number} completed in {cycle_duration:.2f}s - Success: {success}")
            return success
            
        except Exception as e:
            self.logger.error(f"Pipeline cycle {cycle_number} failed: {e}")
            return False
    
    async def _execute_pipeline_components(self, cycle_number: int) -> bool:
        """Execute individual pipeline components"""
        components = [
            ("version_keeper", self._run_version_keeper),
            ("quality_patcher", self._run_quality_patcher),
            ("security_validation", self._run_security_validation),
            ("testing", self._run_testing)
        ]
        
        for component_name, component_func in components:
            self.logger.info(f"Executing component: {component_name}")
            
            try:
                success = await component_func(cycle_number)
                if not success:
                    self.logger.error(f"Component {component_name} failed")
                    return False
            except Exception as e:
                self.logger.error(f"Exception in component {component_name}: {e}")
                return False
        
        return True
    
    async def _run_version_keeper(self, cycle_number: int) -> bool:
        """Run version keeper with enhanced monitoring"""
        cmd = [
            sys.executable,
            str(script_dir / "scripts" / "version_keeper.py"),
            "--claude-lint",
            "--session-dir", str(self.session_dir),
            "--max-cycles", str(min(5, self.performance_metrics.adaptive_batch_size)),
            "--output-format", "json"
        ]
        
        return await self._run_subprocess(cmd, "version_keeper")
    
    async def _run_quality_patcher(self, cycle_number: int) -> bool:
        """Run quality patcher with enhanced monitoring"""
        cmd = [
            sys.executable,
            str(script_dir / "scripts" / "claude_quality_patcher.py"),
            "--continuous-rerun",
            "--session-dir", str(self.session_dir),
            "--max-cycles", str(self.performance_metrics.adaptive_batch_size),
            "--output-format", "json"
        ]
        
        return await self._run_subprocess(cmd, "quality_patcher")
    
    async def _run_security_validation(self, cycle_number: int) -> bool:
        """Run security validation"""
        # Check if bandit is available for security scanning
        try:
            cmd = ["bandit", "-r", ".", "-f", "json", "-o", str(self.session_dir / "security-report.json")]
            result = await self._run_subprocess(cmd, "security_scan", allow_failure=True)
            return True  # Security scan is informational
        except:
            self.logger.info("Bandit security scan not available, skipping")
            return True
    
    async def _run_testing(self, cycle_number: int) -> bool:
        """Run testing suite"""
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "--tb=short",
            "-x",
            "--json-report",
            f"--json-report-file={self.session_dir}/test-report.json"
        ]
        
        return await self._run_subprocess(cmd, "testing", allow_failure=True)
    
    async def _run_subprocess(self, cmd: List[str], component: str, allow_failure: bool = False) -> bool:
        """Run subprocess with timeout and monitoring"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=script_dir
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.timeout_per_cycle
            )
            
            if process.returncode == 0:
                self.logger.debug(f"{component} completed successfully")
                return True
            else:
                self.logger.warning(f"{component} failed with return code {process.returncode}")
                self.logger.debug(f"{component} stderr: {stderr.decode()}")
                return allow_failure
                
        except asyncio.TimeoutError:
            self.logger.error(f"{component} timed out after {self.config.timeout_per_cycle}s")
            return False
        except Exception as e:
            self.logger.error(f"{component} failed with exception: {e}")
            return False
    
    def _adjust_batch_size(self, success: bool, cycle_duration: float):
        """Adjust batch size based on performance"""
        current_batch = self.performance_metrics.adaptive_batch_size
        
        if success and cycle_duration < 60:  # Fast successful cycle
            self.performance_metrics.adaptive_batch_size = min(current_batch + 2, 20)
        elif success and cycle_duration > 180:  # Slow successful cycle
            self.performance_metrics.adaptive_batch_size = max(current_batch - 1, 3)
        elif not success:  # Failed cycle
            self.performance_metrics.adaptive_batch_size = max(current_batch - 2, 1)
        
        if self.performance_metrics.adaptive_batch_size != current_batch:
            self.logger.info(f"Adjusted batch size: {current_batch} -> {self.performance_metrics.adaptive_batch_size}")
    
    async def check_completion_criteria(self) -> bool:
        """Check if orchestrator should complete"""
        try:
            # Run issue counting
            cmd = [
                sys.executable,
                str(script_dir / "scripts" / "version_keeper.py"),
                "--count-issues"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                issues_count = int(stdout.decode().strip())
                self.performance_metrics.issues_remaining = issues_count
                
                self.logger.info(f"Current issues count: {issues_count}")
                return issues_count <= self.config.target_issues
            else:
                self.logger.warning("Failed to get issues count")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking completion criteria: {e}")
            return False
    
    async def attempt_recovery(self) -> bool:
        """Attempt recovery from failure state"""
        if self.recovery_attempts >= self.max_recovery_attempts:
            self.logger.error("Maximum recovery attempts reached")
            return False
        
        self.recovery_attempts += 1
        self.transition_state(OrchestratorState.ERROR_RECOVERY)
        
        self.logger.info(f"Attempting recovery #{self.recovery_attempts}")
        
        try:
            # Reset protocol if available
            if self.protocol:
                await self.initialize_protocol()
            
            # Reset adaptive batch size
            self.performance_metrics.adaptive_batch_size = 5
            
            # Transition back to execution
            self.transition_state(OrchestratorState.PIPELINE_EXECUTION)
            return True
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            return False
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        end_time = time.time()
        total_duration = end_time - self.start_time
        
        report = {
            "session_id": self.session_id,
            "execution_summary": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(end_time).isoformat(),
                "total_duration_seconds": total_duration,
                "final_state": self.current_state.value
            },
            "performance_metrics": asdict(self.performance_metrics),
            "configuration": asdict(self.config),
            "state_transitions": len(self.state_history),
            "recovery_attempts": self.recovery_attempts
        }
        
        # Save report
        report_file = self.session_dir / f"final-report-{self.session_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Enhanced MCP Orchestrator Final Report")
        print(f"{'='*60}")
        print(f"Session ID: {self.session_id}")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Total Cycles: {self.performance_metrics.total_cycles}")
        print(f"Success Rate: {self.performance_metrics.success_rate:.1f}%")
        print(f"Issues Resolved: {self.performance_metrics.issues_resolved}")
        print(f"Issues Remaining: {self.performance_metrics.issues_remaining}")
        print(f"Final State: {self.current_state.value}")
        print(f"Report saved to: {report_file}")
        print(f"{'='*60}")
    
    async def run(self):
        """Main orchestrator execution loop"""
        self.is_running = True
        self.logger.info("Starting Enhanced MCP Orchestrator")
        
        try:
            # Initialize protocol
            self.transition_state(OrchestratorState.PROTOCOL_SETUP)
            await self.initialize_protocol()
            
            # Environment analysis
            self.transition_state(OrchestratorState.ENVIRONMENT_ANALYSIS)
            # Add environment analysis logic here
            
            # Main execution loop
            self.transition_state(OrchestratorState.PIPELINE_EXECUTION)
            
            for cycle in range(1, self.config.max_cycles + 1):
                if not self.is_running:
                    break
                
                self.logger.info(f"=== Pipeline Cycle {cycle}/{self.config.max_cycles} ===")
                
                # Execute cycle
                success = await self.execute_pipeline_cycle(cycle)
                
                if not success and self.config.auto_recovery:
                    recovery_success = await self.attempt_recovery()
                    if not recovery_success:
                        self.transition_state(OrchestratorState.FAILED)
                        break
                
                # Check completion criteria
                if await self.check_completion_criteria():
                    self.logger.info("Completion criteria met!")
                    self.transition_state(OrchestratorState.COMPLETED)
                    break
                
                # Save state periodically
                self.save_state()
                
                # Break for single cycle mode
                if self.config.execution_mode == ExecutionMode.SINGLE_CYCLE:
                    break
            
            if self.current_state not in [OrchestratorState.COMPLETED, OrchestratorState.FAILED]:
                self.transition_state(OrchestratorState.COMPLETED)
                
        except Exception as e:
            self.logger.error(f"Orchestrator execution failed: {e}")
            self.transition_state(OrchestratorState.FAILED)
        finally:
            self.is_running = False
            self.save_state()
            self.generate_final_report()


@click.command()
@click.option('--max-cycles', default=100, help='Maximum number of pipeline cycles')
@click.option('--target-issues', default=0, help='Target number of remaining issues')
@click.option('--execution-mode', type=click.Choice(['continuous', 'single_cycle', 'development', 'production']), 
              default='continuous', help='Execution mode')
@click.option('--session-dir', type=click.Path(), help='Session directory for state and logs')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']), 
              default='INFO', help='Logging level')
@click.option('--timeout', default=600, help='Timeout per cycle in seconds')
@click.option('--batch-size', default=10, help='Initial batch size for processing')
@click.option('--no-protocol', is_flag=True, help='Disable protocol integration')
@click.option('--no-monitoring', is_flag=True, help='Disable monitoring')
@click.option('--no-recovery', is_flag=True, help='Disable auto recovery')
def main(max_cycles, target_issues, execution_mode, session_dir, log_level, timeout, 
         batch_size, no_protocol, no_monitoring, no_recovery):
    """Enhanced MCP Claude Pipeline Master Orchestrator v2.0"""
    
    # Create configuration
    config = OrchestratorConfig(
        max_cycles=max_cycles,
        target_issues=target_issues,
        execution_mode=ExecutionMode(execution_mode),
        enable_protocol=not no_protocol,
        enable_monitoring=not no_monitoring,
        auto_recovery=not no_recovery,
        session_dir=Path(session_dir) if session_dir else None,
        log_level=log_level,
        timeout_per_cycle=timeout,
        batch_size=batch_size
    )
    
    # Create and run orchestrator
    orchestrator = EnhancedMCPOrchestrator(config)
    
    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        print("\nOrchestrator interrupted by user")
    except Exception as e:
        print(f"Orchestrator failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()