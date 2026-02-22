---
name: odoo-accounting
description: Manage Odoo ERP operations - invoices, customers, vendors, sales orders, products, CRM leads, and account balances. Use this when handling business accounting, invoicing, or CRM tasks.
user-invocable: true
allowed-tools:
  - mcp: odoo
  - Read
  - Write
  - Edit
  - Glob
  - Bash(ls *)
---

# Odoo Accounting & ERP Skill (MCP)

Manage business operations through Odoo ERP - invoices, customers, vendors, sales, products, CRM, and account balances.

## Available MCP Tools

The `odoo` MCP server provides these tools:

### Customers
- **`list_customers`** - List customers from Odoo
  - limit (optional): Max results, default 20
- **`create_customer`** - Create a new customer
  - name (required): Customer name
  - email, phone, street, city, country (optional)

### Vendors
- **`list_vendors`** - List vendors/suppliers
  - limit (optional): Max results, default 20
- **`create_vendor`** - Create a new vendor
  - name (required): Vendor name
  - email, phone (optional)

### Products
- **`search_products`** - Search products by name
  - name (optional): Search query, empty = list all
  - limit (optional): Max results, default 20
- **`create_product`** - Create a new product
  - name (required): Product name
  - price (optional): Sale price, default 0
  - product_type (optional): 'service' or 'consu', default 'service'

### Invoices
- **`create_invoice`** - Create a customer invoice (draft)
  - customer_name (required): Customer name (auto-lookup/create)
  - product_name (required): Product name (auto-lookup/create)
  - quantity (optional): Quantity, default 1
  - price_unit (optional): Price per unit, 0 = use product default
- **`list_invoices`** - List invoices
  - state (optional): 'draft', 'posted', 'cancel', or empty for all
  - limit (optional): Max results, default 20
- **`get_invoice`** - Get full invoice details with line items
  - invoice_id (required): Odoo invoice ID
- **`confirm_invoice`** - Post/confirm a draft invoice
  - invoice_id (required): Odoo invoice ID

### Sale Orders
- **`create_sale_order`** - Create a quotation/sale order
  - customer_name (required): Customer name (auto-lookup/create)
  - product_name (required): Product name (auto-lookup/create)
  - quantity (optional): Quantity, default 1
  - price_unit (optional): Price per unit, 0 = use product default
- **`list_sale_orders`** - List sale orders
  - limit (optional): Max results, default 20
- **`confirm_sale_order`** - Confirm a quotation into a sale order
  - order_id (required): Odoo sale order ID

### Account Balance
- **`get_account_balance`** - Get financial summary (receivable, payable, revenue, expenses, net income)

### CRM
- **`list_crm_leads`** - List CRM leads/opportunities
  - limit (optional): Max results, default 20
- **`create_crm_lead`** - Create a new CRM lead
  - name (required): Lead title
  - customer_name, email, phone, expected_revenue (optional)

## Workflow Examples

### Create an invoice for a customer:
1. `list_customers` or `create_customer` to get the customer
2. `search_products` or `create_product` to get the product
3. `create_invoice` with customer name and product name
4. `confirm_invoice` to post the draft invoice

### Check business financial health:
1. `get_account_balance` for receivable/payable/revenue/expense summary
2. `list_invoices` with state='posted' to see confirmed invoices
3. `list_sale_orders` to see pending quotations

### CRM pipeline:
1. `list_crm_leads` to see current pipeline
2. `create_crm_lead` when a new opportunity comes in (e.g. from WhatsApp/email)

## When to Use

- User asks about invoices, billing, or accounting
- User asks to create/list customers or vendors
- User asks about sales, quotations, or orders
- User asks about business finances, balances, or revenue
- User asks about CRM leads or opportunities
- Processing a cross-domain event (e.g. WhatsApp message about an invoice)

## Safety Rules

- Always verify customer exists before creating invoices (tools handle auto-lookup)
- Use human-approval workflow for confirming invoices over large amounts
- All actions are logged to `AI_Employee_Vault/Logs/odoo_actions_YYYY-MM-DD.md`
- Never delete records - only create and read operations are exposed
