from . import __version__ as version

app_name = "asset_rounding"
app_title = "Asset Rounding"
app_publisher = "PT Manfield Coatings Indonesia"
app_description = "Rounds asset depreciation amounts per currency"
app_email = "idit@manfieldcoatings.comm"
app_license = "MIT"

# Apps
# ------------------

# Required for frappe to recognise the app
# add any other hooks if needed

doc_events = {
    "Asset": {
        "before_save": "asset_rounding.asset_rounding.api.round_asset"
    },
    "Asset Depreciation Schedule": {
        "before_save": "asset_rounding.asset_rounding.api.round_depreciation_schedule"
    },
    "Journal Entry": {
        "before_save": "asset_rounding.asset_rounding.api.round_journal_entry"
    }
}
