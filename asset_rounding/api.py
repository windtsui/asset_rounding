import frappe

def get_rounded_amount(amount, currency):
    """Round amount based on currency rules (IDR → whole number, USD → 2 decimals)
       using standard rounding (0.5 always rounds up)."""
    if amount is None or amount == 0:
        return amount
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return amount

    if currency == 'IDR':
        # Standard rounding to nearest integer (half up)
        return int(amount + 0.5) if amount >= 0 else int(amount - 0.5)
    elif currency == 'USD':
        # Round to 2 decimals with half up
        return int(amount * 100 + 0.5) / 100 if amount >= 0 else int(amount * 100 - 0.5) / 100
    return amount


def round_asset(doc, method):
    """Rounds gross_purchase_amount in Asset using the company's currency."""
    currency = None
    if doc.company:
        company = frappe.get_doc("Company", doc.company)
        currency = company.default_currency

    if currency and doc.get("gross_purchase_amount"):
        doc.gross_purchase_amount = get_rounded_amount(doc.gross_purchase_amount, currency)


def round_depreciation_schedule(doc, method):
    """Rounds main and child table amounts in Asset Depreciation Schedule."""
    currency = 'IDR'  # fallback
    if doc.asset:
        asset = frappe.get_doc("Asset", doc.asset)
        if asset.company:
            company = frappe.get_doc("Company", asset.company)
            currency = company.default_currency

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
