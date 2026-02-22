"""
Watchdog Monitor - Gold Tier
Monitors all watcher processes and auto-restarts crashed ones.
Quarantines corrupted files instead of crashing.
Logs health status to the vault.
"""

import subprocess
import sys
import time
import json
import signal
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
VAULT_PATH = BASE_DIR.parent / "AI_Employee_Vault"
LOGS_PATH = VAULT_PATH / "Logs"
QUARANTINE_PATH = VAULT_PATH / "Quarantine"
HEALTH_FILE = LOGS_PATH / "watchdog_health.json"

LOGS_PATH.mkdir(parents=True, exist_ok=True)
QUARANTINE_PATH.mkdir(parents=True, exist_ok=True)

# Import audit logger
sys.path.insert(0, str(BASE_DIR))
try:
    from audit_logger import log_audit
except ImportError:
    def log_audit(**kwargs):
        pass

# Maximum restart attempts per process before giving up
MAX_RESTARTS = 5
# Seconds between health checks
HEALTH_CHECK_INTERVAL = 30
# Minimum uptime (seconds) before resetting restart counter
MIN_UPTIME_FOR_RESET = 300


class ProcessMonitor:
    """Monitors a single subprocess."""

    def __init__(self, name: str, script: str, required: bool = False):
        self.name = name
        self.script = str(script)
        self.required = required
        self.process = None
        self.restart_count = 0
        self.last_start = None
        self.status = "stopped"

    def start(self):
        """Start the subprocess."""
        try:
            self.process = subprocess.Popen(
                [sys.executable, self.script],
                cwd=str(BASE_DIR),
                creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.last_start = datetime.now()
            self.status = "running"
            log_audit(
                action_type="watchdog_start_process",
                target=self.name,
                parameters={"pid": self.process.pid, "script": self.script},
            )
            return True
        except Exception as e:
            self.status = "failed"
            log_audit(
                action_type="watchdog_start_failed",
                target=self.name,
                result="failure",
                error_message=str(e),
            )
            return False

    def is_alive(self) -> bool:
        """Check if process is still running."""
        if not self.process:
            return False
        return self.process.poll() is None

    def restart(self) -> bool:
        """Restart a crashed process with safety limits."""
        if self.restart_count >= MAX_RESTARTS:
            self.status = "abandoned"
            log_audit(
                action_type="watchdog_abandon_process",
                target=self.name,
                result="failure",
                error_message=f"Exceeded max restarts ({MAX_RESTARTS})",
            )
            return False

        # If process ran long enough, reset counter
        if self.last_start:
            uptime = (datetime.now() - self.last_start).total_seconds()
            if uptime > MIN_UPTIME_FOR_RESET:
                self.restart_count = 0

        self.restart_count += 1
        log_audit(
            action_type="watchdog_restart_process",
            target=self.name,
            parameters={"attempt": self.restart_count, "max": MAX_RESTARTS},
        )
        return self.start()

    def stop(self):
        """Stop the subprocess."""
        if self.process and self.is_alive():
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.status = "stopped"

    def to_dict(self) -> dict:
        """Export status as dict."""
        return {
            "name": self.name,
            "script": self.script,
            "status": self.status,
            "pid": self.process.pid if self.process else None,
            "restart_count": self.restart_count,
            "last_start": self.last_start.isoformat() if self.last_start else None,
        }


class Watchdog:
    """Monitors all processes and handles health checks."""

    def __init__(self):
        self.monitors: list[ProcessMonitor] = []
        self.running = False

    def add_process(self, name: str, script: str, required: bool = False):
        """Register a process to monitor."""
        script_path = BASE_DIR / script if not Path(script).is_absolute() else Path(script)
        if not script_path.exists():
            print(f"  Warning: Script not found: {script_path}")
            return
        self.monitors.append(ProcessMonitor(name, str(script_path), required))

    def start_all(self):
        """Start all registered processes."""
        print(f"Starting {len(self.monitors)} processes...")
        for monitor in self.monitors:
            print(f"  Starting {monitor.name}...")
            if monitor.start():
                print(f"    PID: {monitor.process.pid}")
            else:
                print(f"    FAILED to start {monitor.name}")

    def stop_all(self):
        """Stop all processes."""
        print("\nStopping all processes...")
        for monitor in self.monitors:
            monitor.stop()
            print(f"  Stopped {monitor.name}")
        self.running = False

    def check_health(self) -> dict:
        """Check health of all processes, restart crashed ones."""
        health = {
            "timestamp": datetime.now().isoformat(),
            "processes": [],
            "restarts": 0,
            "failures": 0,
        }

        for monitor in self.monitors:
            if monitor.status == "abandoned":
                health["failures"] += 1
                health["processes"].append(monitor.to_dict())
                continue

            if not monitor.is_alive() and monitor.status == "running":
                print(f"  {monitor.name} has crashed! Restarting...")
                if monitor.restart():
                    health["restarts"] += 1
                    print(f"    Restarted (attempt {monitor.restart_count})")
                else:
                    health["failures"] += 1
                    print(f"    ABANDONED after {MAX_RESTARTS} restarts")

            health["processes"].append(monitor.to_dict())

        # Save health status
        try:
            with open(HEALTH_FILE, "w", encoding="utf-8") as f:
                json.dump(health, f, indent=2, default=str)
        except IOError:
            pass

        return health

    def run(self):
        """Main watchdog loop."""
        self.running = True
        self.start_all()

        print(f"\nWatchdog active. Checking every {HEALTH_CHECK_INTERVAL}s.")
        print("Press Ctrl+C to stop.\n")

        try:
            while self.running:
                time.sleep(HEALTH_CHECK_INTERVAL)
                health = self.check_health()
                alive = sum(1 for p in health["processes"] if p["status"] == "running")
                total = len(health["processes"])
                if health["restarts"] > 0 or health["failures"] > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Health: {alive}/{total} running, "
                          f"{health['restarts']} restarts, {health['failures']} failures")
        except KeyboardInterrupt:
            self.stop_all()


def quarantine_file(filepath: Path, reason: str = "corrupted"):
    """
    Move a corrupted/problematic file to Quarantine instead of crashing.

    Args:
        filepath: Path to the problematic file
        reason: Why the file was quarantined
    """
    if not filepath.exists():
        return

    dest = QUARANTINE_PATH / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filepath.name}"
    filepath.rename(dest)

    # Log the quarantine
    log_audit(
        action_type="quarantine_file",
        target=str(filepath),
        parameters={"reason": reason, "destination": str(dest)},
    )

    # Write quarantine metadata
    meta_file = dest.with_suffix(dest.suffix + ".meta.json")
    meta = {
        "original_path": str(filepath),
        "quarantined_at": datetime.now().isoformat(),
        "reason": reason,
    }
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def get_watchdog_health() -> dict:
    """Read the latest watchdog health status."""
    if not HEALTH_FILE.exists():
        return {"status": "no data"}
    try:
        with open(HEALTH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"status": "error reading health file"}


if __name__ == "__main__":
    # Setup signal handler
    watchdog = Watchdog()

    def signal_handler(sig, frame):
        watchdog.stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Register all watcher processes
    watchdog.add_process("File Watcher", "file_watcher.py")
    watchdog.add_process("Mock Watcher", "mock_watcher.py")
    watchdog.add_process("LinkedIn Poster", "linkedin_poster.py")
    watchdog.add_process("Plan Loop", "plan_loop.py")

    # Gmail watcher (optional)
    if (BASE_DIR / "credentials.json").exists() or (BASE_DIR / "gmail_token.pickle").exists():
        watchdog.add_process("Gmail Watcher", "gmail_watcher.py")

    watchdog.run()
