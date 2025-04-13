# tyro_gateway/utils/unique_key_generator.py

def generate_unique_key(model_name: str, data: dict) -> str:
    # 📁 2.1 Email Identity DB
    if model_name == "email_identity":
        return data.get("identity_name", "")

    # 📁 2.2 Job Applications DB
    elif model_name == "job_application":
        return f"{data.get('job_title', '')}-{data.get('company_name', '')}"

    # 📁 2.3 Resume Versions DB
    elif model_name == "resume_version":
        return f"{data.get('target_job_title', '')}-{data.get('date_created', '')}"

    # 📁 2.4 Personal Tax DB
    elif model_name == "personal_tax":
        return f"{data.get('tax_platform', '')}-{data.get('year', '')}"

    # 📁 2.5 Business Tax DB
    elif model_name == "business_tax":
        return f"{data.get('business_name', '')}-{data.get('tax_year', '')}"

    # 📁 2.6 Stock Strategy DB
    elif model_name == "stock_strategy":
        return f"{data.get('ticker', '')}-{data.get('trade_action', '')}-{data.get('strategy_date', '')}"

    # 📁 2.7 Options Strategy DB
    elif model_name == "options_strategy":
        return f"{data.get('ticker', '')}-{data.get('trade_action', '')}-{data.get('created_date', '')}-{data.get('option_strategy', '')}"

    # 📁 2.8 Real Estate DB
    elif model_name == "real_estate":
        return data.get("property_address", "")

    # 📁 2.9 Strategy Master DB
    elif model_name == "strategy":
        return f"{data.get('strategy_name', '')}-{data.get('module_project', '')}-{data.get('category', '')}"

    # 📁 3.1 Client CRM DB
    elif model_name == "client_crm":
        return f"{data.get('client_name', '')}-{data.get('client_company', '')}-{data.get('client_email', '')}"

    # 📁 3.2 Retailer CRM DB
    elif model_name == "retailer_crm":
        return f"{data.get('retailer_name', '')}-{data.get('retailer_company', '')}-{data.get('retailer_email', '')}"

    return ""
