# utils/unique_key_generator.py

from datetime import datetime

def generate_unique_key(model_name: str, data: dict) -> str:
    def safe_get(*fields) -> str:
        """安全取得多個欄位組合並清理空格"""
        values = [str(data.get(field, "")).strip() for field in fields]
        return "-".join(filter(None, values))

    key = ""

    if model_name == "email_identity":
        key = safe_get("identity_name")

    elif model_name == "job_application":
        key = safe_get("job_title", "company_name")

    elif model_name == "resume_version":
        key = safe_get("target_job_title", "date_created")

    elif model_name == "stock_strategy":
        key = safe_get("ticker", "trade_action", "strategy_date")

    elif model_name == "options_strategy":
        key = safe_get("ticker", "action", "created_date", "option_strategy")

    elif model_name == "real_estate":
        key = safe_get("property_address")

    elif model_name == "strategy":
        key = safe_get("strategy_name", "module_project", "category")

    elif model_name == "client_crm":
        key = safe_get("client_name", "client_company", "client_email")

    elif model_name == "retailer_crm":
        key = safe_get("retailer_name", "retailer_company", "retailer_email")

    elif model_name == "personal_tax":
        key = safe_get("tax_platform", "year")

    elif model_name == "business_tax":
        key = safe_get("business_name", "tax_year")

    # ⛔ fallback 處理
    if not key:
        print(f"⚠️ Warning: Failed to generate unique key for {model_name}")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        key = f"unknown-{model_name}-{timestamp}"

    return key
