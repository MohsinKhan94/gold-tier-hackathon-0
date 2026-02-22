"""
Retry Handler - Gold Tier
Provides exponential backoff retry logic for transient errors (API timeouts, network issues).
Queues actions locally when external services are down.
NEVER auto-retries payments - requires fresh human approval.
"""

import json
import time
import functools
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path(__file__).parent.parent / "AI_Employee_Vault"
QUEUE_PATH = VAULT_PATH / "Logs" / "retry_queue.json"

# Actions that must NEVER be auto-retried
PAYMENT_ACTIONS = {"payment", "bank_transfer", "pay_invoice", "confirm_payment"}

# Default retry config
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 2  # seconds
DEFAULT_MAX_DELAY = 60  # seconds


def retry_with_backoff(
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    exceptions: tuple = (Exception,),
    action_type: str = "",
):
    """
    Decorator for exponential backoff retry.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        exceptions: Tuple of exception types to catch
        action_type: Type of action (for payment safety check)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # SAFETY: Never auto-retry payment actions
            if action_type.lower() in PAYMENT_ACTIONS:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    queue_failed_action(action_type, str(e), args, kwargs)
                    raise RuntimeError(
                        f"Payment action '{action_type}' failed: {e}. "
                        "Payment actions are NEVER auto-retried. "
                        "Queued for manual review in retry_queue.json."
                    )

            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        time.sleep(delay)
                    else:
                        # All retries exhausted - queue for later
                        queue_failed_action(action_type or func.__name__, str(e), args, kwargs)

            raise last_exception

        return wrapper
    return decorator


def queue_failed_action(action_type: str, error: str, args: tuple = None, kwargs: dict = None):
    """
    Queue a failed action for later retry when services recover.

    Args:
        action_type: Type of the failed action
        error: Error message
        args: Original function args
        kwargs: Original function kwargs
    """
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

    queue = []
    if QUEUE_PATH.exists():
        try:
            with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                queue = json.load(f)
        except (json.JSONDecodeError, IOError):
            queue = []

    entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "error": error,
        "status": "queued",
        "requires_approval": action_type.lower() in PAYMENT_ACTIONS,
        "retry_count": 0,
    }

    # Only store serializable args
    if kwargs:
        safe_kwargs = {}
        for k, v in kwargs.items():
            try:
                json.dumps(v)
                safe_kwargs[k] = v
            except (TypeError, ValueError):
                safe_kwargs[k] = str(v)
        entry["kwargs"] = safe_kwargs

    queue.append(entry)

    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, default=str)


def get_queued_actions() -> list:
    """Get all queued actions waiting for retry."""
    if not QUEUE_PATH.exists():
        return []
    try:
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def clear_queue():
    """Clear the retry queue after manual review."""
    if QUEUE_PATH.exists():
        with open(QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)


def is_service_available(service_name: str) -> bool:
    """
    Quick health check for external services.

    Args:
        service_name: 'odoo', 'gmail', 'linkedin'

    Returns:
        True if service responds, False otherwise
    """
    import requests

    health_checks = {
        "odoo": "http://localhost:8069/web/webclient/version_info",
        "gmail": "https://www.googleapis.com/gmail/v1/users/me/profile",
    }

    url = health_checks.get(service_name)
    if not url:
        return True  # Unknown service - assume available

    try:
        resp = requests.get(url, timeout=5)
        return resp.status_code < 500
    except Exception:
        return False


if __name__ == "__main__":
    print("=== Retry Handler Test ===")

    # Test decorator
    @retry_with_backoff(max_retries=2, base_delay=0.1, action_type="test")
    def flaky_function():
        import random
        if random.random() < 0.7:
            raise ConnectionError("Simulated failure")
        return "success"

    try:
        result = flaky_function()
        print(f"Result: {result}")
    except ConnectionError:
        print("All retries exhausted (expected in test)")

    # Test service check
    print(f"\nOdoo available: {is_service_available('odoo')}")

    # Show queue
    queue = get_queued_actions()
    print(f"Queued actions: {len(queue)}")
