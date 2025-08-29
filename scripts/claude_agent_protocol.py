#!/usr/bin/env python3
"""
Claude Agent Protocol - Enhanced Bidirectional Communication System
Implements ReAct-style structured communication with DSPy-inspired optimization
"""

import json
import queue
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class TaskType(Enum):
    """Types of tasks that can be assigned to Claude"""

    LINT_FIX = "lint_fix"
    CODE_REVIEW = "code_review"
    TEST_CREATION = "test_creation"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    VALIDATION = "validation"
    WEB_SEARCH = "web_search"
    FILE_ANALYSIS = "file_analysis"


class TaskStatus(Enum):
    """Status of assigned tasks"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    VALIDATION_REQUIRED = "validation_required"


class ActionType(Enum):
    """Types of actions Claude can take"""

    READ_FILE = "read_file"
    EDIT_FILE = "edit_file"
    MULTI_EDIT = "multi_edit"
    WEB_SEARCH = "web_search"
    RUN_TEST = "run_test"
    ANALYZE = "analyze"
    VALIDATE = "validate"


@dataclass
class Task:
    """Structured task definition with JSON schema validation"""

    task_id: str
    task_type: TaskType
    status: TaskStatus
    priority: int
    context: Dict[str, Any]
    expected_actions: List[str]
    constraints: Dict[str, Any]
    created_at: str
    updated_at: str
    attempts: int = 0
    max_attempts: int = 3
    success_criteria: Dict[str, Any] = None
    observations: List[Dict] = None
    result: Optional[Dict] = None

    def to_json(self):
        """Convert to JSON-serializable dict"""
        data = asdict(self)
        data["task_type"] = self.task_type.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_json(cls, data):
        """Create from JSON dict"""
        data["task_type"] = TaskType(data["task_type"])
        data["status"] = TaskStatus(data["status"])
        return cls(**data)


class ClaudeAgentProtocol:
    """Enhanced bidirectional communication protocol with Claude"""

    def __init__(self, session_dir: Path = None):
        self.session_dir = session_dir or Path(".claude-session")
        self.session_dir.mkdir(exist_ok=True)

        # Communication files
        self.state_file = self.session_dir / "agent-state.json"
        self.task_queue_file = self.session_dir / "task-queue.json"
        self.observation_log = self.session_dir / "observations.jsonl"
        self.performance_metrics = self.session_dir / "performance.json"

        # In-memory state
        self.current_state = self._load_state()
        self.task_queue = queue.PriorityQueue()
        self.active_tasks = {}
        self.completed_tasks = []
        self.performance_data = self._load_performance_metrics()

        # ReAct loop state
        self.thought_history = []
        self.action_history = []
        self.observation_history = []

        # DSPy-style optimization
        self.prompt_templates = {}
        self.success_patterns = []
        self.failure_patterns = []

    def _load_state(self) -> Dict:
        """Load current state from disk"""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {
            "session_id": str(uuid.uuid4()),
            "started_at": datetime.now().isoformat(),
            "current_phase": "initialization",
            "issues_remaining": -1,
            "files_modified": [],
            "total_fixes_applied": 0,
        }

    def _save_state(self):
        """Persist current state to disk"""
        self.state_file.write_text(json.dumps(self.current_state, indent=2))

    def _load_performance_metrics(self) -> Dict:
        """Load performance metrics"""
        if self.performance_metrics.exists():
            return json.loads(self.performance_metrics.read_text())
        return {
            "fixes_per_minute": [],
            "success_rate": 0.0,
            "retry_counts": {},
            "average_fix_time": 0,
            "patterns_learned": [],
        }

    def _save_performance_metrics(self):
        """Save performance metrics"""
        self.performance_metrics.write_text(json.dumps(self.performance_data, indent=2))

    # ============= TASK MANAGEMENT =============

    def create_task(
        self,
        task_type: TaskType,
        context: Dict[str, Any],
        priority: int = 5,
        constraints: Dict = None,
        success_criteria: Dict = None,
    ) -> Task:
        """Create a structured task for Claude"""
        task = Task(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            status=TaskStatus.PENDING,
            priority=priority,
            context=context,
            expected_actions=self._get_expected_actions(task_type),
            constraints=constraints or {},
            success_criteria=success_criteria or {},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            observations=[],
        )

        # Add to queue with priority
        self.task_queue.put((priority, task.created_at, task))
        self._save_task_queue()

        return task

    def _get_expected_actions(self, task_type: TaskType) -> List[str]:
        """Get expected actions for a task type"""
        action_map = {
            TaskType.LINT_FIX: [
                ActionType.READ_FILE.value,
                ActionType.EDIT_FILE.value,
                ActionType.VALIDATE.value,
            ],
            TaskType.CODE_REVIEW: [
                ActionType.READ_FILE.value,
                ActionType.ANALYZE.value,
            ],
            TaskType.TEST_CREATION: [
                ActionType.READ_FILE.value,
                ActionType.EDIT_FILE.value,
                ActionType.RUN_TEST.value,
            ],
            TaskType.WEB_SEARCH: [
                ActionType.WEB_SEARCH.value,
                ActionType.ANALYZE.value,
            ],
            TaskType.REFACTORING: [
                ActionType.READ_FILE.value,
                ActionType.MULTI_EDIT.value,
                ActionType.VALIDATE.value,
            ],
        }
        return action_map.get(task_type, [])

    def get_next_task(self) -> Optional[Task]:
        """Get highest priority task from queue"""
        if not self.task_queue.empty():
            _, _, task = self.task_queue.get()
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.now().isoformat()
            self.active_tasks[task.task_id] = task
            self._save_state()
            return task
        return None

    def _save_task_queue(self):
        """Save task queue to disk"""
        tasks = []
        temp_queue = queue.PriorityQueue()

        while not self.task_queue.empty():
            priority, created, task = self.task_queue.get()
            tasks.append(task.to_json())
            temp_queue.put((priority, created, task))

        self.task_queue = temp_queue
        self.task_queue_file.write_text(json.dumps(tasks, indent=2))

    # ============= ReAct FRAMEWORK =============

    def record_thought(self, task_id: str, thought: str):
        """Record Claude's reasoning step"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "type": "thought",
            "content": thought,
        }
        self.thought_history.append(entry)
        self._append_observation(entry)

    def record_action(self, task_id: str, action: ActionType, details: Dict):
        """Record Claude's action"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "type": "action",
            "action": action.value,
            "details": details,
        }
        self.action_history.append(entry)
        self._append_observation(entry)

        # Update task
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.observations.append(entry)

    def record_observation(self, task_id: str, observation: Dict):
        """Record observation/result from action"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "type": "observation",
            "content": observation,
        }
        self.observation_history.append(entry)
        self._append_observation(entry)

        # Check if task is complete
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if self._check_success_criteria(task, observation):
                self.complete_task(task_id, success=True, result=observation)

    def _append_observation(self, entry: Dict):
        """Append to observation log"""
        with open(self.observation_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _check_success_criteria(self, task: Task, observation: Dict) -> bool:
        """Check if task success criteria are met"""
        if not task.success_criteria:
            return False

        for key, expected in task.success_criteria.items():
            if key not in observation or observation[key] != expected:
                return False
        return True

    # ============= TASK COMPLETION =============

    def complete_task(self, task_id: str, success: bool, result: Dict = None):
        """Mark task as completed"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            task.result = result
            task.updated_at = datetime.now().isoformat()

            # Move to completed
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]

            # Update performance metrics
            self._update_performance_metrics(task, success)

            # Learn from outcome
            if success:
                self.success_patterns.append(self._extract_pattern(task))
            else:
                self.failure_patterns.append(self._extract_pattern(task))

            self._save_state()

    def _extract_pattern(self, task: Task) -> Dict:
        """Extract pattern from task for learning"""
        return {
            "task_type": task.task_type.value,
            "context_keys": list(task.context.keys()),
            "action_sequence": [
                obs["action"]
                for obs in task.observations
                if obs.get("type") == "action"
            ],
            "success": task.status == TaskStatus.COMPLETED,
        }

    def _update_performance_metrics(self, task: Task, success: bool):
        """Update performance metrics"""
        # Calculate fix time
        created = datetime.fromisoformat(task.created_at)
        completed = datetime.fromisoformat(task.updated_at)
        duration = (completed - created).total_seconds()

        # Update metrics
        if duration > 0:
            fixes_per_minute = 60.0 / duration
            self.performance_data["fixes_per_minute"].append(fixes_per_minute)

        # Update success rate
        total = len(self.completed_tasks)
        successful = sum(
            1 for t in self.completed_tasks if t.status == TaskStatus.COMPLETED
        )
        self.performance_data["success_rate"] = successful / total if total > 0 else 0

        # Track retries
        if task.task_id in self.performance_data["retry_counts"]:
            self.performance_data["retry_counts"][task.task_id] += 1
        else:
            self.performance_data["retry_counts"][task.task_id] = 0

        self._save_performance_metrics()

    # ============= GUARDRAILS & VALIDATION =============

    def validate_action(self, action: ActionType, context: Dict) -> Tuple[bool, str]:
        """Validate if an action is allowed"""
        # Check against failure patterns
        for pattern in self.failure_patterns[-10:]:  # Check last 10 failures
            if self._matches_pattern(action, context, pattern):
                return False, f"Action matches failure pattern: {pattern}"

        # Specific guardrails
        if action == ActionType.EDIT_FILE:
            if "file_path" not in context:
                return False, "file_path required for edit action"
            if not Path(context["file_path"]).exists():
                return False, f"File does not exist: {context['file_path']}"

        return True, "Action validated"

    def _matches_pattern(
        self, action: ActionType, context: Dict, pattern: Dict
    ) -> bool:
        """Check if action matches a pattern"""
        if (
            pattern.get("action_sequence")
            and action.value in pattern["action_sequence"]
        ):
            context_matches = all(
                key in context for key in pattern.get("context_keys", [])
            )
            return context_matches
        return False

    # ============= ADAPTIVE STRATEGIES =============

    def get_optimized_strategy(self, task_type: TaskType) -> Dict:
        """Get optimized strategy based on performance"""
        strategy = {
            "batch_size": 25,  # Even larger batches for speed
            "parallel": True,  # Enable parallel by default for speed
            "use_web_search": "minimal",  # Smart web search when needed
            "validation_level": "standard",
            "web_search_timeout": 60,  # Realistic timeout for Claude
            "direct_communication": True,  # Prioritize direct Claude communication
        }

        # Adapt based on success rate - optimized for speed with smart web search
        if self.performance_data["success_rate"] < 0.3:
            strategy["batch_size"] = 15  # Larger batches even for low success
            strategy["validation_level"] = "standard"  # Less strict = faster
            strategy["use_web_search"] = (
                "smart"  # Smart web search: only for unknown errors, realistic timeout
            )
            strategy["web_search_timeout"] = (
                45  # Realistic timeout for complex searches
            )
        elif self.performance_data["success_rate"] > 0.6:
            strategy["batch_size"] = 50  # Maximum batch size for high performance
            strategy["parallel"] = True
            strategy["use_web_search"] = (
                False  # High success rate = no web search needed
            )
        else:
            strategy["batch_size"] = 25  # Larger default batch
            strategy["parallel"] = True  # Enable parallel for speed
            strategy["use_web_search"] = (
                "minimal"  # Minimal web search: only critical unknowns
            )

        # Adapt based on task type performance
        task_patterns = [
            p for p in self.success_patterns if p["task_type"] == task_type.value
        ]
        if len(task_patterns) > 5:
            # We have enough data to optimize
            common_actions = self._get_common_action_sequence(task_patterns)
            strategy["preferred_actions"] = common_actions

        return strategy

    def _get_common_action_sequence(self, patterns: List[Dict]) -> List[str]:
        """Extract common successful action sequence"""
        if not patterns:
            return []

        sequences = [p["action_sequence"] for p in patterns]
        if not sequences:
            return []

        # Find most common sequence (simple approach)
        from collections import Counter

        sequence_strings = [",".join(seq) for seq in sequences]
        most_common = Counter(sequence_strings).most_common(1)

        if most_common:
            return most_common[0][0].split(",")
        return []

    # ============= STATE MACHINE =============

    def update_phase(self, new_phase: str, context: Dict = None):
        """Update current pipeline phase"""
        self.current_state["current_phase"] = new_phase
        self.current_state["phase_updated_at"] = datetime.now().isoformat()

        if context:
            self.current_state.update(context)

        self._save_state()

        # Trigger phase-specific actions
        self._handle_phase_transition(new_phase)

    def _handle_phase_transition(self, phase: str):
        """Handle phase transitions"""
        transitions = {
            "linting": self._prepare_linting_tasks,
            "fixing": self._prepare_fixing_tasks,
            "validating": self._prepare_validation_tasks,
            "publishing": self._prepare_publishing_tasks,
        }

        handler = transitions.get(phase)
        if handler:
            handler()

    def _prepare_linting_tasks(self):
        """Prepare tasks for linting phase"""
        # Create high-priority lint task
        self.create_task(
            TaskType.LINT_FIX,
            context={"phase": "linting", "action": "run_comprehensive_lint"},
            priority=1,
        )

    def _prepare_fixing_tasks(self):
        """Prepare tasks for fixing phase"""
        # Create fixing tasks based on lint results
        if "lint_issues" in self.current_state:
            for issue in self.current_state["lint_issues"][:10]:  # First 10 issues
                self.create_task(
                    TaskType.LINT_FIX, context=issue, priority=issue.get("severity", 5)
                )

    def _prepare_validation_tasks(self):
        """Prepare validation tasks"""
        self.create_task(
            TaskType.VALIDATION,
            context={"files": self.current_state.get("files_modified", [])},
            priority=2,
        )

    def _prepare_publishing_tasks(self):
        """Prepare publishing tasks"""
        self.create_task(
            TaskType.VALIDATION,
            context={"action": "final_validation", "publish": True},
            priority=1,
        )

    # ============= COMMUNICATION INTERFACE =============

    def generate_claude_instruction(self, task: Task) -> str:
        """Generate structured instruction for Claude"""
        context_str = json.dumps(task.context, indent=2)
        actions_str = chr(10).join(
            f"  {i + 1}. {action}" for i, action in enumerate(task.expected_actions)
        )
        constraints_str = (
            json.dumps(task.constraints, indent=2) if task.constraints else "None"
        )
        success_criteria_str = (
            json.dumps(task.success_criteria, indent=2)
            if task.success_criteria
            else "Complete actions"
        )

        instruction = f"""
        🎯 TASK ASSIGNMENT: {task.task_type.value.upper()}
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        📋 Task ID: {task.task_id}
        🎯 Priority: {task.priority}/10
        🕐 Created: {task.created_at}

        📝 CONTEXT:
        {context_str}

        🔧 EXPECTED ACTIONS:
        {actions_str}

        ⚡ CONSTRAINTS:
        {constraints_str}

        ✅ SUCCESS CRITERIA:
        {success_criteria_str}

        🚀 DIRECT ACTION PROTOCOL (OPTIMIZED FOR SPEED):
        1. IMMEDIATE ACTION: Apply fixes directly using Read/Edit tools - NO DELAYS
        2. FAST VALIDATION: Quick syntax/logic check
        3. EFFICIENT OBSERVATION: Report success/failure immediately
        4. BATCH PROCESSING: Handle multiple similar issues together when possible

        ⚡ SPEED OPTIMIZATION HINTS:
        {self._get_performance_hint(task.task_type)}

        🎯 PRIORITY: Direct communication and immediate fixes - minimize web
        search delays

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        return instruction

    def _get_performance_hint(self, task_type: TaskType) -> str:
        """Get performance-based hint for task"""
        strategy = self.get_optimized_strategy(task_type)

        hints = []
        web_search_setting = strategy.get("use_web_search")
        if web_search_setting == "smart":
            hints.append("Smart web search enabled for unknown errors (45s timeout)")
        elif web_search_setting == "minimal":
            hints.append("Minimal web search for critical unknowns (60s timeout)")

        if strategy.get("batch_size", 10) >= 25:
            hints.append("Large batch processing for maximum speed")
        if strategy.get("parallel"):
            hints.append("Parallel processing enabled")
        if strategy.get("web_search_timeout"):
            hints.append(f"Web search timeout: {strategy['web_search_timeout']}s")

        return " | ".join(hints) if hints else "Optimized for maximum speed"

    def get_status_summary(self) -> Dict:
        """Get current status summary"""
        return {
            "session_id": self.current_state["session_id"],
            "current_phase": self.current_state["current_phase"],
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "pending_tasks": self.task_queue.qsize(),
            "success_rate": self.performance_data["success_rate"],
            "issues_remaining": self.current_state.get("issues_remaining", -1),
            "files_modified": len(self.current_state.get("files_modified", [])),
            "total_fixes": self.current_state.get("total_fixes_applied", 0),
        }


# ============= SINGLETON INSTANCE =============


_protocol_instance = None


def get_protocol(session_dir: Path = None) -> ClaudeAgentProtocol:
    """Get or create protocol instance"""
    global _protocol_instance
    if _protocol_instance is None:
        _protocol_instance = ClaudeAgentProtocol(session_dir)
    return _protocol_instance


if __name__ == "__main__":
    # Example usage
    protocol = get_protocol()

    # Create a task
    task = protocol.create_task(
        TaskType.LINT_FIX,
        context={
            "file_path": "example.py",
            "line_number": 42,
            "issue": "undefined variable",
            "suggestion": "Define variable before use",
        },
        priority=3,
    )

    print(protocol.generate_claude_instruction(task))
    print("\nStatus:", json.dumps(protocol.get_status_summary(), indent=2))
