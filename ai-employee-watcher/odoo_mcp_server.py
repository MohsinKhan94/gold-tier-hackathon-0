"""
Odoo MCP Server - Gold Tier
Exposes Odoo ERP operations (invoices, customers, vendors, sales, purchases, products)
as MCP tools for Claude Code via JSON-RPC API.
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
SCRIPT_DIR = Path(__file__).parent
ENV_PATH = SCRIPT_DIR.parent / ".env"
load_dotenv(ENV_PATH)

# Odoo connection settings
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "ai_employee")
ODOO_USER = os.getenv("ODOO_USER", "sherankhan666@gmail.com")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")
JSONRPC_URL = f"{ODOO_URL}/jsonrpc"

# Vault paths for logging
VAULT_PATH = SCRIPT_DIR.parent / "AI_Employee_Vault"
LOGS_PATH = VAULT_PATH / "Logs"
LOGS_PATH.mkdir(parents=True, exist_ok=True)

# Initialize MCP server
mcp = FastMCP("odoo", instructions="Odoo ERP MCP server for managing invoices, customers, vendors, sales, purchases, and products via Odoo JSON-RPC API.")


# ─── Odoo JSON-RPC Client ───────────────────────────────────────────────────

class OdooClient:
    """Handles all communication with Odoo via JSON-RPC."""

    def __init__(self):
        self.url = JSONRPC_URL
        self.db = ODOO_DB
        self.user = ODOO_USER
        self.password = ODOO_PASSWORD
        self.uid = None
        self._request_id = 0

    def _next_id(self):
        self._request_id += 1
        return self._request_id

    def _call(self, service: str, method: str, args: list) -> dict:
        """Make a JSON-RPC call to Odoo."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,
                "args": args,
            },
            "id": self._next_id(),
        }
        resp = requests.post(self.url, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if "error" in result:
            error_data = result["error"]
            msg = error_data.get("data", {}).get("message", error_data.get("message", str(error_data)))
            raise Exception(f"Odoo error: {msg}")
        return result.get("result")

    def authenticate(self) -> int:
        """Authenticate with Odoo and return user ID."""
        if self.uid:
            return self.uid
        self.uid = self._call("common", "login", [self.db, self.user, self.password])
        if not self.uid:
            raise Exception("Odoo authentication failed. Check credentials.")
        return self.uid

    def execute_kw(self, model: str, method: str, args: list, kwargs: dict = None) -> any:
        """Execute a method on an Odoo model."""
        uid = self.authenticate()
        call_args = [self.db, uid, self.password, model, method, args]
        if kwargs:
            call_args.append(kwargs)
        return self._call("object", "execute_kw", call_args)

    def search_read(self, model: str, domain: list = None, fields: list = None, limit: int = None, order: str = None) -> list:
        """Search and read records from an Odoo model."""
        kwargs = {}
        if fields:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        if order:
            kwargs["order"] = order
        return self.execute_kw(model, "search_read", [domain or []], kwargs)

    def create(self, model: str, values: dict) -> int:
        """Create a record and return its ID."""
        return self.execute_kw(model, "create", [values])

    def write(self, model: str, ids: list, values: dict) -> bool:
        """Update existing records."""
        return self.execute_kw(model, "write", [ids, values])

    def read(self, model: str, ids: list, fields: list = None) -> list:
        """Read specific records by ID."""
        kwargs = {}
        if fields:
            kwargs["fields"] = fields
        return self.execute_kw(model, "read", [ids], kwargs)


# Global client instance
odoo = OdooClient()


# ─── Logging ─────────────────────────────────────────────────────────────────

def log_action(action: str, details: dict):
    """Log Odoo actions to the vault for audit trail."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"odoo_actions_{date_str}.md"

    entry = f"\n## [{timestamp}] {action}\n"
    for key, value in details.items():
        entry += f"- **{key}:** {value}\n"
    entry += "---\n"

    if not log_file.exists():
        header = f"# Odoo Action Log - {date_str}\n\nAll Odoo ERP actions performed via Odoo MCP Server.\n\n---\n"
        log_file.write_text(header + entry, encoding="utf-8")
    else:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)


# ─── Helper functions ────────────────────────────────────────────────────────

def find_partner_by_name(name: str, is_company: bool = None) -> dict | None:
    """Find a partner (customer/vendor) by name. Returns first match or None."""
    domain = [["name", "ilike", name]]
    if is_company is not None:
        domain.append(["is_company", "=", is_company])
    results = odoo.search_read("res.partner", domain, ["id", "name", "email", "phone"], limit=1)
    return results[0] if results else None


def find_or_create_partner(name: str, email: str = "", phone: str = "") -> int:
    """Find a partner by name or create one. Returns partner ID."""
    partner = find_partner_by_name(name)
    if partner:
        return partner["id"]
    values = {"name": name, "is_company": True}
    if email:
        values["email"] = email
    if phone:
        values["phone"] = phone
    return odoo.create("res.partner", values)


def find_product_by_name(name: str) -> dict | None:
    """Find a product by name. Returns first match or None."""
    results = odoo.search_read(
        "product.product",
        [["name", "ilike", name]],
        ["id", "name", "list_price", "type"],
        limit=1,
    )
    return results[0] if results else None


def find_or_create_product(name: str, price: float = 0.0) -> int:
    """Find a product by name or create one. Returns product ID."""
    product = find_product_by_name(name)
    if product:
        return product["id"]
    return odoo.create("product.product", {
        "name": name,
        "list_price": price,
        "type": "service",
    })


# ─── MCP Tools: Customers ───────────────────────────────────────────────────

@mcp.tool()
def list_customers(limit: int = 20) -> str:
    """List customers (contacts) from Odoo.

    Args:
        limit: Maximum number of customers to return (default 20)

    Returns:
        JSON string with list of customers (id, name, email, phone, city, country)
    """
    try:
        customers = odoo.search_read(
            "res.partner",
            [["customer_rank", ">", 0]],
            ["id", "name", "email", "phone", "city", "country_id"],
            limit=limit,
            order="name asc",
        )
        for c in customers:
            if c.get("country_id"):
                c["country"] = c["country_id"][1] if isinstance(c["country_id"], list) else c["country_id"]
            else:
                c["country"] = ""
            del c["country_id"]

        log_action("LIST_CUSTOMERS", {"Count": len(customers), "Limit": limit})
        return json.dumps({"status": "success", "count": len(customers), "customers": customers})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def create_customer(name: str, email: str = "", phone: str = "", street: str = "", city: str = "", country: str = "") -> str:
    """Create a new customer in Odoo.

    Args:
        name: Customer name (required)
        email: Customer email address
        phone: Customer phone number
        street: Street address
        city: City
        country: Country name (e.g. 'Pakistan', 'United States')

    Returns:
        JSON string with the created customer ID
    """
    try:
        values = {"name": name, "customer_rank": 1, "is_company": True}
        if email:
            values["email"] = email
        if phone:
            values["phone"] = phone
        if street:
            values["street"] = street
        if city:
            values["city"] = city
        if country:
            countries = odoo.search_read("res.country", [["name", "ilike", country]], ["id"], limit=1)
            if countries:
                values["country_id"] = countries[0]["id"]

        customer_id = odoo.create("res.partner", values)
        log_action("CREATE_CUSTOMER", {"Name": name, "Email": email, "ID": customer_id})
        return json.dumps({"status": "success", "customer_id": customer_id, "name": name})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


# ─── MCP Tools: Vendors ─────────────────────────────────────────────────────

@mcp.tool()
def list_vendors(limit: int = 20) -> str:
    """List vendors (suppliers) from Odoo.

    Args:
        limit: Maximum number of vendors to return (default 20)

    Returns:
        JSON string with list of vendors (id, name, email, phone)
    """
    try:
        vendors = odoo.search_read(
            "res.partner",
            [["supplier_rank", ">", 0]],
            ["id", "name", "email", "phone"],
            limit=limit,
            order="name asc",
        )
        log_action("LIST_VENDORS", {"Count": len(vendors), "Limit": limit})
        return json.dumps({"status": "success", "count": len(vendors), "vendors": vendors})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def create_vendor(name: str, email: str = "", phone: str = "") -> str:
    """Create a new vendor (supplier) in Odoo.

    Args:
        name: Vendor name (required)
        email: Vendor email address
        phone: Vendor phone number

    Returns:
        JSON string with the created vendor ID
    """
    try:
        values = {"name": name, "supplier_rank": 1, "is_company": True}
        if email:
            values["email"] = email
        if phone:
            values["phone"] = phone

        vendor_id = odoo.create("res.partner", values)
        log_action("CREATE_VENDOR", {"Name": name, "Email": email, "ID": vendor_id})
        return json.dumps({"status": "success", "vendor_id": vendor_id, "name": name})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


# ─── MCP Tools: Products ────────────────────────────────────────────────────

@mcp.tool()
def search_products(name: str = "", limit: int = 20) -> str:
    """Search products in Odoo.

    Args:
        name: Product name to search for (partial match). Leave empty to list all.
        limit: Maximum number of products to return (default 20)

    Returns:
        JSON string with list of products (id, name, list_price, type)
    """
    try:
        domain = []
        if name:
            domain = [["name", "ilike", name]]
        products = odoo.search_read(
            "product.product",
            domain,
            ["id", "name", "list_price", "type", "default_code"],
            limit=limit,
            order="name asc",
        )
        log_action("SEARCH_PRODUCTS", {"Query": name or "ALL", "Count": len(products)})
        return json.dumps({"status": "success", "count": len(products), "products": products})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def create_product(name: str, price: float = 0.0, product_type: str = "service") -> str:
    """Create a new product in Odoo.

    Args:
        name: Product name (required)
        price: Sale price (default 0.0)
        product_type: Product type - 'service' or 'consu' for consumable (default 'service')

    Returns:
        JSON string with the created product ID
    """
    try:
        values = {
            "name": name,
            "list_price": price,
            "type": product_type,
        }
        product_id = odoo.create("product.product", values)
        log_action("CREATE_PRODUCT", {"Name": name, "Price": price, "Type": product_type, "ID": product_id})
        return json.dumps({"status": "success", "product_id": product_id, "name": name})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


# ─── MCP Tools: Invoices ────────────────────────────────────────────────────

@mcp.tool()
def create_invoice(customer_name: str, product_name: str, quantity: float = 1.0, price_unit: float = 0.0) -> str:
    """Create a customer invoice (draft) in Odoo.

    Args:
        customer_name: Name of the customer (will be looked up or created)
        product_name: Name of the product/service (will be looked up or created)
        quantity: Quantity of items (default 1)
        price_unit: Price per unit. If 0, uses the product's default price.

    Returns:
        JSON string with the created invoice ID and number
    """
    try:
        partner_id = find_or_create_partner(customer_name)
        product = find_product_by_name(product_name)
        if product:
            product_id = product["id"]
            if price_unit == 0.0:
                price_unit = product.get("list_price", 0.0)
        else:
            product_id = find_or_create_product(product_name, price_unit)

        invoice_id = odoo.create("account.move", {
            "move_type": "out_invoice",
            "partner_id": partner_id,
            "invoice_line_ids": [(0, 0, {
                "product_id": product_id,
                "quantity": quantity,
                "price_unit": price_unit,
            })],
        })

        invoice = odoo.read("account.move", [invoice_id], ["name", "amount_total", "state"])[0]
        log_action("CREATE_INVOICE", {
            "Customer": customer_name,
            "Product": product_name,
            "Quantity": quantity,
            "Price": price_unit,
            "Total": invoice["amount_total"],
            "Invoice ID": invoice_id,
            "Number": invoice["name"],
        })
        return json.dumps({
            "status": "success",
            "invoice_id": invoice_id,
            "invoice_number": invoice["name"],
            "amount_total": invoice["amount_total"],
            "state": invoice["state"],
            "customer": customer_name,
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def list_invoices(state: str = "", limit: int = 20) -> str:
    """List invoices from Odoo.

    Args:
        state: Filter by state - 'draft', 'posted', 'cancel', or empty for all
        limit: Maximum number of invoices to return (default 20)

    Returns:
        JSON string with list of invoices (id, name, partner, amount, state, date)
    """
    try:
        domain = [["move_type", "=", "out_invoice"]]
        if state:
            domain.append(["state", "=", state])

        invoices = odoo.search_read(
            "account.move",
            domain,
            ["id", "name", "partner_id", "amount_total", "amount_residual", "state", "invoice_date", "invoice_date_due"],
            limit=limit,
            order="create_date desc",
        )
        for inv in invoices:
            if inv.get("partner_id"):
                inv["customer"] = inv["partner_id"][1] if isinstance(inv["partner_id"], list) else inv["partner_id"]
            else:
                inv["customer"] = ""
            del inv["partner_id"]

        log_action("LIST_INVOICES", {"State": state or "ALL", "Count": len(invoices)})
        return json.dumps({"status": "success", "count": len(invoices), "invoices": invoices})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def get_invoice(invoice_id: int) -> str:
    """Get detailed information about a specific invoice.

    Args:
        invoice_id: The Odoo ID of the invoice

    Returns:
        JSON string with full invoice details including line items
    """
    try:
        invoices = odoo.read("account.move", [invoice_id], [
            "name", "partner_id", "amount_total", "amount_residual", "amount_untaxed",
            "amount_tax", "state", "move_type", "invoice_date", "invoice_date_due",
            "invoice_line_ids", "payment_state",
        ])
        if not invoices:
            return json.dumps({"status": "error", "error": f"Invoice {invoice_id} not found"})

        invoice = invoices[0]
        if invoice.get("partner_id"):
            invoice["customer"] = invoice["partner_id"][1] if isinstance(invoice["partner_id"], list) else invoice["partner_id"]
        del invoice["partner_id"]

        # Get line item details
        if invoice.get("invoice_line_ids"):
            lines = odoo.read("account.move.line", invoice["invoice_line_ids"], [
                "product_id", "name", "quantity", "price_unit", "price_subtotal",
            ])
            invoice["lines"] = []
            for line in lines:
                invoice["lines"].append({
                    "product": line["product_id"][1] if isinstance(line.get("product_id"), list) else line.get("name", ""),
                    "description": line.get("name", ""),
                    "quantity": line.get("quantity", 0),
                    "price_unit": line.get("price_unit", 0),
                    "subtotal": line.get("price_subtotal", 0),
                })
            del invoice["invoice_line_ids"]

        log_action("GET_INVOICE", {"Invoice ID": invoice_id, "Number": invoice.get("name", "")})
        return json.dumps({"status": "success", "invoice": invoice})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def confirm_invoice(invoice_id: int) -> str:
    """Confirm (post) a draft invoice in Odoo. Changes state from 'draft' to 'posted'.

    Args:
        invoice_id: The Odoo ID of the invoice to confirm

    Returns:
        JSON string with confirmation status
    """
    try:
        odoo.execute_kw("account.move", "action_post", [[invoice_id]])
        invoice = odoo.read("account.move", [invoice_id], ["name", "state", "amount_total"])[0]
        log_action("CONFIRM_INVOICE", {
            "Invoice ID": invoice_id,
            "Number": invoice["name"],
            "Amount": invoice["amount_total"],
            "State": invoice["state"],
        })
        return json.dumps({
            "status": "success",
            "invoice_id": invoice_id,
            "invoice_number": invoice["name"],
            "state": invoice["state"],
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


# ─── MCP Tools: Sale Orders ─────────────────────────────────────────────────

@mcp.tool()
def create_sale_order(customer_name: str, product_name: str, quantity: float = 1.0, price_unit: float = 0.0) -> str:
    """Create a sale order (quotation) in Odoo.

    Args:
        customer_name: Name of the customer (will be looked up or created)
        product_name: Name of the product/service (will be looked up or created)
        quantity: Quantity of items (default 1)
        price_unit: Price per unit. If 0, uses the product's default price.

    Returns:
        JSON string with the created sale order ID and number
    """
    try:
        partner_id = find_or_create_partner(customer_name)
        product = find_product_by_name(product_name)
        if product:
            product_id = product["id"]
            if price_unit == 0.0:
                price_unit = product.get("list_price", 0.0)
        else:
            product_id = find_or_create_product(product_name, price_unit)

        order_id = odoo.create("sale.order", {
            "partner_id": partner_id,
            "order_line": [(0, 0, {
                "product_id": product_id,
                "product_uom_qty": quantity,
                "price_unit": price_unit,
            })],
        })

        order = odoo.read("sale.order", [order_id], ["name", "amount_total", "state"])[0]
        log_action("CREATE_SALE_ORDER", {
            "Customer": customer_name,
            "Product": product_name,
            "Quantity": quantity,
            "Price": price_unit,
            "Total": order["amount_total"],
            "Order ID": order_id,
            "Number": order["name"],
        })
        return json.dumps({
            "status": "success",
            "order_id": order_id,
            "order_number": order["name"],
            "amount_total": order["amount_total"],
            "state": order["state"],
            "customer": customer_name,
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def list_sale_orders(limit: int = 20) -> str:
    """List sale orders from Odoo.

    Args:
        limit: Maximum number of orders to return (default 20)

    Returns:
        JSON string with list of sale orders
    """
    try:
        orders = odoo.search_read(
            "sale.order",
            [],
            ["id", "name", "partner_id", "amount_total", "state", "date_order"],
            limit=limit,
            order="create_date desc",
        )
        for o in orders:
            if o.get("partner_id"):
                o["customer"] = o["partner_id"][1] if isinstance(o["partner_id"], list) else o["partner_id"]
            else:
                o["customer"] = ""
            del o["partner_id"]

        log_action("LIST_SALE_ORDERS", {"Count": len(orders)})
        return json.dumps({"status": "success", "count": len(orders), "orders": orders})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def confirm_sale_order(order_id: int) -> str:
    """Confirm a quotation into a sale order in Odoo.

    Args:
        order_id: The Odoo ID of the sale order to confirm

    Returns:
        JSON string with confirmation status
    """
    try:
        odoo.execute_kw("sale.order", "action_confirm", [[order_id]])
        order = odoo.read("sale.order", [order_id], ["name", "state", "amount_total"])[0]
        log_action("CONFIRM_SALE_ORDER", {
            "Order ID": order_id,
            "Number": order["name"],
            "Amount": order["amount_total"],
            "State": order["state"],
        })
        return json.dumps({
            "status": "success",
            "order_id": order_id,
            "order_number": order["name"],
            "state": order["state"],
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


# ─── MCP Tools: Account Balance ─────────────────────────────────────────────

@mcp.tool()
def get_account_balance() -> str:
    """Get a summary of account balances from Odoo (receivable, payable, bank/cash).

    Returns:
        JSON string with account balance summary
    """
    try:
        # Get receivable balance (what customers owe us)
        receivable = odoo.search_read(
            "account.move.line",
            [["account_id.account_type", "=", "asset_receivable"], ["parent_state", "=", "posted"]],
            ["debit", "credit", "balance"],
            limit=None,
        )
        total_receivable = sum(line.get("balance", 0) for line in receivable)

        # Get payable balance (what we owe vendors)
        payable = odoo.search_read(
            "account.move.line",
            [["account_id.account_type", "=", "liability_payable"], ["parent_state", "=", "posted"]],
            ["debit", "credit", "balance"],
            limit=None,
        )
        total_payable = sum(line.get("balance", 0) for line in payable)

        # Get revenue
        revenue = odoo.search_read(
            "account.move.line",
            [["account_id.account_type", "=", "income"], ["parent_state", "=", "posted"]],
            ["balance"],
            limit=None,
        )
        total_revenue = abs(sum(line.get("balance", 0) for line in revenue))

        # Get expenses
        expenses = odoo.search_read(
            "account.move.line",
            [["account_id.account_type", "=", "expense"], ["parent_state", "=", "posted"]],
            ["balance"],
            limit=None,
        )
        total_expenses = sum(line.get("balance", 0) for line in expenses)

        summary = {
            "accounts_receivable": round(total_receivable, 2),
            "accounts_payable": round(total_payable, 2),
            "total_revenue": round(total_revenue, 2),
            "total_expenses": round(total_expenses, 2),
            "net_income": round(total_revenue - total_expenses, 2),
        }

        log_action("GET_ACCOUNT_BALANCE", summary)
        return json.dumps({"status": "success", "balance_summary": summary})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


# ─── MCP Tools: CRM Leads ───────────────────────────────────────────────────

@mcp.tool()
def list_crm_leads(limit: int = 20) -> str:
    """List CRM leads/opportunities from Odoo.

    Args:
        limit: Maximum number of leads to return (default 20)

    Returns:
        JSON string with list of CRM leads
    """
    try:
        leads = odoo.search_read(
            "crm.lead",
            [],
            ["id", "name", "partner_id", "expected_revenue", "probability", "stage_id", "type", "email_from", "phone"],
            limit=limit,
            order="create_date desc",
        )
        for lead in leads:
            if lead.get("partner_id"):
                lead["customer"] = lead["partner_id"][1] if isinstance(lead["partner_id"], list) else lead["partner_id"]
            else:
                lead["customer"] = ""
            del lead["partner_id"]
            if lead.get("stage_id"):
                lead["stage"] = lead["stage_id"][1] if isinstance(lead["stage_id"], list) else lead["stage_id"]
            else:
                lead["stage"] = ""
            del lead["stage_id"]

        log_action("LIST_CRM_LEADS", {"Count": len(leads)})
        return json.dumps({"status": "success", "count": len(leads), "leads": leads})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def create_crm_lead(name: str, customer_name: str = "", email: str = "", phone: str = "", expected_revenue: float = 0.0) -> str:
    """Create a new CRM lead/opportunity in Odoo.

    Args:
        name: Lead title (required)
        customer_name: Customer/company name
        email: Contact email
        phone: Contact phone
        expected_revenue: Expected revenue amount

    Returns:
        JSON string with the created lead ID
    """
    try:
        values = {"name": name, "type": "opportunity"}
        if customer_name:
            partner_id = find_or_create_partner(customer_name, email)
            values["partner_id"] = partner_id
        if email:
            values["email_from"] = email
        if phone:
            values["phone"] = phone
        if expected_revenue:
            values["expected_revenue"] = expected_revenue

        lead_id = odoo.create("crm.lead", values)
        log_action("CREATE_CRM_LEAD", {"Name": name, "Customer": customer_name, "Revenue": expected_revenue, "ID": lead_id})
        return json.dumps({"status": "success", "lead_id": lead_id, "name": name})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


# ─── Run Server ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
