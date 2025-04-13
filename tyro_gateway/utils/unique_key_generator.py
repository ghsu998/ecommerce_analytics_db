# tyro_gateway/utils/unique_key_generator.py

def generate_unique_key(model_name: str, data: dict) -> str:
    if model_name == "email_identity":
        return data.get("identity_name", "")
    
    elif model_name == "business_tax":
        return f"{data.get('business_name', '')}-{data.get('tax_year', '')}"
    
    elif model_name == "personal_tax":
        return f"{data.get('tax_platform', '')}-{data.get('year', '')}"
    
    elif model_name == "real_estate":
        return data.get("property_address", "")
    
    elif model_name == "resume_version":
        return f"{data.get('target_job_title', '')}-{data.get('date_created', '')}"

    elif model_name == "stock_strategy":
        return f"{data.get('ticker', '')}-{data.get('trade_action', '')}-{data.get('strategy_date', '')}"
    
    elif model_name == "options_strategy":
        return f"{data.get('ticker', '')}-{data.get('option_strategy', '')}-{data.get('created_date', '')}"
    
    return ""
