import frappe

def get_rounded_amount(amount, currency):
    """Round amount based on currency rules (IDR → whole number, USD → 2 decimals)."""
    if amount is None or amount == 0:
        return amount
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return amount

    if currency == 'IDR':
        return round(amount)
    elif currency == 'USD':
        return round(amount, 2)
    # Add other currencies as needed
    return amount


def round_asset(doc, method):
    """Rounds gross_purchase_amount in Asset."""
    currency = None
    if doc.company:
        company = frappe.get_doc("Company", doc.company)
        currency = company.default_currency

    if currency and doc.get("gross_purchase_amount"):
        doc.gross_purchase_amount = get_rounded_amount(doc.gross_purchase_amount, currency)


def round_depreciation_schedule(doc, method):
    """Rounds main and child table amounts in Asset Depreciation Schedule."""
    # Determine currency from linked Asset or fallback
    currency = 'IDR'
    if doc.asset:
        asset = frappe.get_doc("Asset", doc.asset)
        currency = asset.currency or frappe.db.get_value("Company", asset.company, "default_currency")

    if doc.get("depreciation_amount"):
        doc.depreciation_amount = get_rounded_amount(doc.depreciation_amount, currency)

    if doc.get("depreciation_schedule"):
        for row in doc.depreciation_schedule:
            if row.get("depreciation_amount"):
                row.depreciation_amount = get_rounded_amount(row.depreciation_amount, currency)
            if row.get("accumulated_depreciation_amount"):
                row.accumulated_depreciation_amount = get_rounded_amount(row.accumulated_depreciation_amount, currency)


def round_journal_entry(doc, method):
    """Rounds debit/credit in Journal Entry accounts."""
    currency = doc.company_currency or 'IDR'
    if doc.get("accounts"):
        for acc in doc.accounts:
            if acc.get("debit"):
                acc.debit = get_rounded_amount(acc.debit, currency)
            if acc.get("credit"):
                acc.credit = get_rounded_amount(acc.credit, currency)
