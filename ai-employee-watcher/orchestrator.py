"""
Cross-Domain Orchestrator - Gold Tier
Routes events across personal and business domains.

Example flows:
- WhatsApp message about "invoice" -> Odoo lookup -> Email reply -> Audit log
- Email about "payment" -> Odoo check balance -> Flag for approval
- LinkedIn lead -> CRM entry -> Follow-up email draft

The orchestrator scans Inbox/ for new items, classifies them by domain,
and chains appropriate actions.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
VAULT_PATH = BASE_DIR.parent / "AI_Employee_Vault"
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"

sys.path.insert(0, str(BASE_DIR))

try:
    from audit_logger import log_audit
except ImportError:
    def log_audit(**kwargs): pass

try:
    from odoo_mcp_server import OdooClient
    odoo = OdooClient()
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False
    odoo = None


# Domain keywords for classification
BUSINESS_KEYWORDS = [
    "invoice", "payment", "quotation", "sale", "order", "purchase",
    "customer", "client", "vendor", "supplier", "contract", "proposal",
    "crm", "lead", "opportunity", "revenue", "balance", "accounting",
    "project", "deadline", "deliverable", "milestone",
]

PERSONAL_KEYWORDS = [
    "meeting", "schedule", "reschedule", "appointment", "reminder",
    "birthday", "family", "personal", "vacation", "leave",
]

SOCIAL_KEYWORDS = [
    "linkedin", "facebook", "instagram", "twitter", "post", "engagement",
    "followers", "likes", "comments", "social media",
]

URGENCY_KEYWORDS = [
    "urgent", "asap", "immediately", "critical", "emergency", "deadline today",
    "overdue", "past due", "final notice",
]


class EventClassification:
    """Classification result for an incoming event."""

    def __init__(self, source: str, content: str):
        self.source = source  # 'email', 'whatsapp', 'file', 'linkedin'
        self.content = content.lower()
        self.domains = self._classify_domains()
        self.is_urgent = self._check_urgency()
        self.suggested_actions = self._suggest_actions()

    def _classify_domains(self) -> list:
        domains = []
        if any(kw in self.content for kw in BUSINESS_KEYWORDS):
            domains.append("business")
        if any(kw in self.content for kw in PERSONAL_KEYWORDS):
            domains.append("personal")
        if any(kw in self.content for kw in SOCIAL_KEYWORDS):
            domains.append("social")
        if not domains:
            domains.append("general")
        return domains

    def _check_urgency(self) -> bool:
        return any(kw in self.content for kw in URGENCY_KEYWORDS)

    def _suggest_actions(self) -> list:
        actions = []

        # Business domain actions
        if "business" in self.domains:
            if any(kw in self.content for kw in ["invoice", "payment", "balance"]):
                actions.append({"type": "odoo_lookup", "description": "Look up in Odoo ERP"})
            if any(kw in self.content for kw in ["quotation", "proposal", "order"]):
                actions.append({"type": "create_sale_order", "description": "Create sale order in Odoo"})
            if any(kw in self.content for kw in ["lead", "opportunity", "client"]):
                actions.append({"type": "create_crm_lead", "description": "Create CRM lead in Odoo"})

        # Email-related actions
        if self.source in ["whatsapp", "email"]:
            actions.append({"type": "draft_reply", "description": "Draft email reply"})

        # Social domain actions
        if "social" in self.domains:
            actions.append({"type": "social_post", "description": "Create social media content"})

        # Urgency flag
        if self.is_urgent:
            actions.insert(0, {"type": "flag_urgent", "description": "Flag as urgent - needs immediate attention"})

        return actions

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "domains": self.domains,
            "is_urgent": self.is_urgent,
            "suggested_actions": self.suggested_actions,
        }


def classify_inbox_item(filepath: Path) -> EventClassification:
    """Read and classify an inbox item."""
    content = filepath.read_text(encoding="utf-8")

    # Detect source from content or filename
    source = "file"
    name_lower = filepath.name.lower()
    if "email" in name_lower or "gmail" in name_lower:
        source = "email"
    elif "whatsapp" in name_lower:
        source = "whatsapp"
    elif "linkedin" in name_lower:
        source = "linkedin"

    return EventClassification(source, content)


def process_cross_domain_event(filepath: Path) -> dict:
    """
    Process a cross-domain event: classify it and enrich with Odoo data if relevant.

    Returns a result dict describing what was done.
    """
    classification = classify_inbox_item(filepath)
    result = {
        "file": filepath.name,
        "classification": classification.to_dict(),
        "enrichments": [],
    }

    # Odoo enrichment for business domain
    if "business" in classification.domains and ODOO_AVAILABLE:
        try:
            odoo.authenticate()
            content = filepath.read_text(encoding="utf-8").lower()

            # Look up customer if mentioned
            # Extract potential names (simple heuristic: capitalized words)
            raw_content = filepath.read_text(encoding="utf-8")
            potential_names = re.findall(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', raw_content)

            for name in potential_names[:3]:
                customers = odoo.search_read(
                    "res.partner",
                    [["name", "ilike", name], ["customer_rank", ">", 0]],
                    ["id", "name", "email"],
                    limit=1,
                )
                if customers:
                    result["enrichments"].append({
                        "type": "odoo_customer_found",
                        "data": customers[0],
                    })

                    # Look up their invoices
                    invoices = odoo.search_read(
                        "account.move",
                        [["partner_id", "=", customers[0]["id"]], ["move_type", "=", "out_invoice"]],
                        ["name", "amount_total", "state", "payment_state"],
                        limit=5,
                    )
                    if invoices:
                        result["enrichments"].append({
                            "type": "odoo_invoices",
                            "data": invoices,
                        })
                    break

            # If invoice number mentioned, look it up
            inv_match = re.search(r'INV/\d+/\d+', raw_content)
            if inv_match:
                inv_number = inv_match.group()
                invoices = odoo.search_read(
                    "account.move",
                    [["name", "=", inv_number]],
                    ["name", "partner_id", "amount_total", "state", "payment_state"],
                    limit=1,
                )
                if invoices:
                    result["enrichments"].append({
                        "type": "odoo_invoice_lookup",
                        "data": invoices[0],
                    })

        except Exception as e:
            result["enrichments"].append({"type": "odoo_error", "error": str(e)})

    log_audit(
        action_type="cross_domain_classification",
        target=filepath.name,
        parameters=classification.to_dict(),
    )

    return result


def scan_inbox_for_cross_domain() -> list:
    """Scan all inbox items and classify them."""
    results = []
    if not INBOX_PATH.exists():
        return results

    for f in sorted(INBOX_PATH.iterdir()):
        if f.is_file() and f.suffix == ".md":
            try:
                result = process_cross_domain_event(f)
                results.append(result)
            except Exception as e:
                results.append({"file": f.name, "error": str(e)})

    return results


if __name__ == "__main__":
    print("=== Cross-Domain Orchestrator ===")
    print(f"Scanning {INBOX_PATH}...\n")

    results = scan_inbox_for_cross_domain()
    for r in results:
        print(f"File: {r.get('file', 'unknown')}")
        if "error" in r:
            print(f"  Error: {r['error']}")
        else:
            c = r.get("classification", {})
            print(f"  Domains: {c.get('domains', [])}")
            print(f"  Urgent: {c.get('is_urgent', False)}")
            print(f"  Actions: {[a['description'] for a in c.get('suggested_actions', [])]}")
            if r.get("enrichments"):
                print(f"  Enrichments: {len(r['enrichments'])}")
        print()

    print(f"Total items classified: {len(results)}")
