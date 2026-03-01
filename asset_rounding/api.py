import frappe
from frappe.utils import flt

def get_rounded_amount(amount, currency):
    """Rounds amount to a whole number for IDR or 2 decimals for USD."""
    if amount is None or amount == 0:
        return 0
    amount = flt(amount)
    if currency == 'IDR':
        # Indonesian Standard: No decimals in Rupiah
        return int(amount + 0.5) if amount >= 0 else int(amount - 0.5)
    return round(amount, 2)

def round_asset(doc, method):
    """Ensures the main Asset purchase price is a whole number first."""
    if doc.company:
        company = frappe.get_doc("Company", doc.company)
        currency = company.default_currency
        if currency == 'IDR' and doc.gross_purchase_amount:
            doc.gross_purchase_amount = get_rounded_amount(doc.gross_purchase_amount, currency)

def round_depreciation_schedule(doc, method):
    """
    FORCED ROUNDING: This bypasses ERPNext's internal math by 
    stamping the rounded values directly into the database.
    """
    if not doc.get("depreciation_schedule"):
        return

    # 1. Identify Currency and Total Cost
    currency = 'IDR'
    total_to_depreciate = 0
    if doc.asset:
        asset = frappe.get_doc("Asset", doc.asset)
        total_to_depreciate = flt(asset.gross_purchase_amount)
        company = frappe.get_doc("Company", asset.company)
        currency = company.default_currency

    # 2. Sort rows by sequence
    rows = sorted(doc.depreciation_schedule, key=lambda x: x.idx)
    cumulative_rounded = 0
    total_rows = len(rows)

    # 3. Calculate and Force Values
    for i, row in enumerate(rows):
        if i == total_rows - 1:
            # Final month: The "Plug" to reach exactly zero
            monthly_amount = total_to_depreciate - cumulative_rounded
        else:
            # Normal month: Round the system's suggested amount
            monthly_amount = get_rounded_amount(row.depreciation_amount, currency)
        
        cumulative_rounded += monthly_amount

        # Use 'db_set' to force the value so the UI doesn't overwrite it
        row.depreciation_amount = monthly_amount
        row.accumulated_depreciation_amount = cumulative_rounded
        
        # This line ensures the database saves exactly what we want
        if row.name:
            frappe.db.set_value("Depreciation Schedule", row.name, {
                "depreciation_amount": monthly_amount,
                "accumulated_depreciation_amount": cumulative_rounded
            }, update_modified=False)

def round_journal_entry(doc, method):
    """Ensures the final Journal Entry uses these rounded figures."""
    currency = doc.company_currency or 'IDR'
    if currency == 'IDR' and doc.get("accounts"):
        for acc in doc.accounts:
            if acc.get("debit"): acc.debit = get_rounded_amount(acc.debit, currency)
            if acc.get("credit"): acc.credit = get_rounded_amount(acc.credit, currency)
