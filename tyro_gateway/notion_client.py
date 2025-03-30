import json
import requests

# 讀取 app_config.json 裡的 Notion token
with open("app_config.json", "r") as f:
    config = json.load(f)
NOTION_TOKEN = config["notion_token"]

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

#1.1 Job Application Tracker
def create_job_application(data):
    database_id = "1c32a656-d251-8037-915d-c0e9a52ef4d3"  # Job Application Tracker

    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Date Applied": {
                "date": {
                    "start": str(data.date_applied)
                }
            },
            "Job Title": {
                "rich_text": [{"text": {"content": data.job_title}}]
            },
            "Company Name": {
                "rich_text": [{"text": {"content": data.company_name}}]
            },
            "Status": {
                "rich_text": [{"text": {"content": data.status}}]
            },
            "Job Type": {
                "rich_text": [{"text": {"content": data.job_type}}]
            },
            "Notes": {
                "rich_text": [{"text": {"content": data.notes}}]
            },
            "Title": {
                "title": [{"text": {"content": f"{data.job_title} @ {data.company_name}"}}]
            }
        }
    }

    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()

#1.2 Resume + Cover Letter Version Tracker
def create_resume_version(data):
    database_id = "1c32a656-d251-8047-be41-debb5c2e6c0d"

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Resume Summary": {
                "rich_text": [{"text": {"content": data.resume_summary}}]
            },
            "Target Job Title": {
                "rich_text": [{"text": {"content": data.target_job_title}}]
            },
            "Date Created": {
                "date": {"start": str(data.date_created)}
            },
            "Cover Letter Content": {
                "rich_text": [{"text": {"content": data.cover_letter_content or ""}}]
            },
            "Title": {
                "title": [{"text": {"content": f"{data.target_job_title} Resume"}}]
            }
        }
    }

    url = "https://api.notion.com/v1/pages"
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()

#2.1 Personal Annual Tax Filing Summary
def create_personal_tax(data):
    database_id = "1c42a656-d251-80b1-b969-ebbf790ab828"
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Total Tax": {"number": data.total_tax},
            "AGI": {"number": data.agi},
            "Tax Platform": {"rich_text": [{"text": {"content": data.tax_platform}}]},
            "Year": {"rich_text": [{"text": {"content": data.year}}]},
            "Filing Date": {"date": {"start": str(data.filing_date)}},
            "Withholding / Estimated Paid": {"number": data.withholding_paid},
            "Refund / Balance Due": {"number": data.refund_due},
            "Notes": {"rich_text": [{"text": {"content": data.notes}}]},
            "Title": {"title": [{"text": {"content": f"{data.year} Tax Filing"}}]}
        }
    }
    url = "https://api.notion.com/v1/pages"
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()

# 2.2 Business Annual Tax Filing Summary
def create_business_tax(data):
    database_id = "1c42a656-d251-803b-b514-e843e5039cdd"

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Entity Type": {
                "rich_text": [{"text": {"content": data.entity_type}}]
            },
            "COGS": {
                "number": data.cogs
            },
            "Business Name": {
                "rich_text": [{"text": {"content": data.business_name}}]
            },
            "Tax Year": {
                "number": data.tax_year
            },
            "Franchise Tax (CA)": {
                "number": data.franchise_tax
            },
            "Notes": {
                "rich_text": [{"text": {"content": data.notes or ""}}]
            },
            "Total Revenue": {
                "number": data.total_revenue
            },
            "Estimated Tax Paid": {
                "number": data.estimated_tax_paid
            },
            "Filing Date": {
                "date": {"start": str(data.filing_date)}
            },
            "Title": {
                "title": [{"text": {"content": f"{data.business_name} - {data.tax_year}"}}]
            },
            "Net Income / Loss": {
                "number": data.net_income
            },
            "Total Expenses": {
                "number": data.total_expenses
            },
        }
    }

    url = "https://api.notion.com/v1/pages"
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()


#3.1 Stock Strategy Log
def create_stock_strategy(data):
    database_id = "1c42a656-d251-806f-9937-ddf04500ea15"

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Ticker": {
                "rich_text": [{"text": {"content": data.ticker}}]
            },
            "Position Size": {
                "number": data.position_size
            },
            "Strategy Note": {
                "rich_text": [{"text": {"content": data.strategy_note}}]
            },
            "Action": {
                "rich_text": [{"text": {"content": data.action}}]
            },
            "Strike Price": {
                "number": data.strike_price
            },
            "Date": {
                "date": {"start": str(data.date)}
            },
            "Title": {
                "title": [{"text": {"content": f"{data.ticker} Strategy"}}]
            }
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=payload)
    return res.status_code, res.json()

#3.2 Options Play Log
def create_options_play(data):
    database_id = "1c42a656-d251-80d6-9423-d36c3c55d606"

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Delta": {"number": data.delta},
            "Ticker": {"rich_text": [{"text": {"content": data.ticker}}]},
            "Option Strategy": {"rich_text": [{"text": {"content": data.option_strategy}}]},
            "Date": {"date": {"start": str(data.date)}},
            "Expiration": {"date": {"start": str(data.expiration)}},
            "Action": {"rich_text": [{"text": {"content": data.action}}]},
            "Entry Option Price": {"number": data.entry_option_price},
            "Contract Size": {"number": data.contract_size},
            "Strategy Note": {"rich_text": [{"text": {"content": data.strategy_note}}]},
            "Title": {
                "title": [{"text": {"content": f"{data.ticker} {data.option_strategy} Play"}}]
            }
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=payload)
    return res.status_code, res.json()

#3.3 Real Estate Tracker
def create_real_estate_entry(data):
    database_id = "1c42a656-d251-80e5-b765-caa4c5bc6b14"  # Real Estate Tracker

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Purchase Date": {
                "date": {"start": str(data.purchase_date)}
            },
            "Purchase Price": {
                "number": data.purchase_price
            },
            "Property Address": {
                "rich_text": [{"text": {"content": data.property_address}}]
            },
            "Monthly Cash Flow": {
                "number": data.monthly_cash_flow
            },
            "Notes": {
                "rich_text": [{"text": {"content": data.notes or ""}}]
            },
            "Loan Amount": {
                "number": data.loan_amount
            },
            "Strategy": {
                "rich_text": [{"text": {"content": data.strategy or ""}}]
            },
            "Title": {
                "title": [{"text": {"content": f"{data.property_address} Real Estate"}}]
            }
        }
    }

    url = "https://api.notion.com/v1/pages"
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()

#4.1 Email Identity DB
def create_email_identity(data):
    database_id = "1c42a656-d251-80c1-a3d9-d6ed033a60e5"
    url = "https://api.notion.com/v1/pages"

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Language": {"rich_text": [{"text": {"content": data.language}}]},
            "Used For": {"rich_text": [{"text": {"content": data.used_for}}]},
            "Tone Style": {"rich_text": [{"text": {"content": data.tone_style}}]},
            "Identity Name": {"rich_text": [{"text": {"content": data.identity_name}}]},
            "Example Phrase": {"rich_text": [{"text": {"content": data.example_phrase}}]},
            "Title": {"title": [{"text": {"content": f"{data.identity_name} Identity"}}]}
        }
    }

    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()

#4.2 Client CRM DB
def create_client_crm(data):
    database_id = "1c42a656-d251-80c5-b261-f488a8c1ed04"
    url = "https://api.notion.com/v1/pages"

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Client Name": {"rich_text": [{"text": {"content": data.client_name}}]},
            "Client Company": {"rich_text": [{"text": {"content": data.client_company}}]},
            "Status": {"rich_text": [{"text": {"content": data.status}}]},
            "Assigned To Identity": {"rich_text": [{"text": {"content": data.assigned_to_identity}}]},
            "Client Notes": {"rich_text": [{"text": {"content": data.client_notes}}]},
            "Client Last Contacted": {
                "date": {"start": str(data.client_last_contacted)} if data.client_last_contacted else None
            },
            "Title": {"title": [{"text": {"content": f"{data.client_name} @ {data.client_company}"}}]}
        }
    }

    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()
