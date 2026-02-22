"""
Ralph Wiggum Stop Hook - Gold Tier
Keeps Claude Code running until a task is fully complete.

How it works:
1. Orchestrator creates a task state file in AI_Employee_Vault/Needs_Action/
2. Claude Code works on the task
3. Claude tries to exit
4. This stop hook checks: Is the task file in /Done/?
   - NO  -> Block exit, output prompt to re-inject (loop continues)
   - YES -> Allow exit (task complete)
5. Max iterations safety valve (default 10)

Usage in .claude/hooks/:
{
    "hooks": {
        "Stop": [{
            "matcher": "",
            "command": "python C:/Users/useerr/Desktop/hackthon-0/bronze-tier/ai-employee-watcher/ralph_wiggum.py"
        }]
    }
}

The hook script communicates via:
- Exit code 0 + empty stdout = allow exit
- Exit code 0 + stdout with text = block exit and re-inject the text as prompt
- Exit code 2 = block exit (hard block)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
VAULT_PATH = BASE_DIR.parent / "AI_Employee_Vault"
DONE_PATH = VAULT_PATH / "Done"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
TASK_STATE_FILE = VAULT_PATH / "Logs" / "ralph_wiggum_state.json"

MAX_ITERATIONS = 10


def get_state() -> dict:
    """Read the current task loop state."""
    if TASK_STATE_FILE.exists():
        try:
            with open(TASK_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"active": False, "task_file": None, "iteration": 0, "prompt": ""}


def save_state(state: dict):
    """Save the task loop state."""
    TASK_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TASK_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)


def is_task_done(task_filename: str) -> bool:
    """Check if the task file has been moved to Done/."""
    done_file = DONE_PATH / task_filename
    return done_file.exists()


def is_task_active(task_filename: str) -> bool:
    """Check if the task file still exists in Needs_Action/."""
    active_file = NEEDS_ACTION_PATH / task_filename
    return active_file.exists()


def main():
    state = get_state()

    # If no active task loop, allow exit silently
    if not state.get("active") or not state.get("task_file"):
        sys.exit(0)

    task_file = state["task_file"]
    iteration = state.get("iteration", 0)
    prompt = state.get("prompt", "")

    # Safety valve: max iterations reached
    if iteration >= MAX_ITERATIONS:
        state["active"] = False
        state["stopped_reason"] = f"Max iterations ({MAX_ITERATIONS}) reached"
        state["stopped_at"] = datetime.now().isoformat()
        save_state(state)
        # Allow exit
        sys.exit(0)

    # Check if task is done
    if is_task_done(task_file):
        state["active"] = False
        state["completed_at"] = datetime.now().isoformat()
        state["stopped_reason"] = "Task completed (found in Done/)"
        save_state(state)
        # Allow exit
        sys.exit(0)

    # Task not done - block exit and re-inject prompt
    state["iteration"] = iteration + 1
    state["last_check"] = datetime.now().isoformat()
    save_state(state)

    # Output prompt to stdout - this re-injects into Claude Code
    remaining = MAX_ITERATIONS - iteration - 1
    reinject = (
        f"The task '{task_file}' is NOT complete yet (iteration {iteration + 1}/{MAX_ITERATIONS}). "
        f"{remaining} attempts remaining. "
    )
    if prompt:
        reinject += f"Original task: {prompt}. "
    reinject += (
        "Please continue working on this task. "
        "When complete, move the task file to AI_Employee_Vault/Done/."
    )

    print(reinject)
    sys.exit(0)


if __name__ == "__main__":
    main()
