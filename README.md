# Ecommerce Analytics DB

A modular data automation system for managing e-commerce datasets, inventory forecasting, and content workflow orchestration.  
Designed by Gary Hsu as part of a personal infrastructure project to support multi-brand operations across Shopify, SellerCloud, and content marketing channels.

---

## 📦 Overview

This repository supports two primary use cases:

- **Inventory Planning Automation**  
  Built around the DVF (Demand Variation Forecasting) model, this module processes historical Excel files, classifies SKU demand types, and outputs reorder signals to support operational purchasing.

- **Content Workflow Prototyping**  
  A blog content system powered by GPT and Google Ads Keyword data, with a pipeline to sync and publish content directly to Shopify CMS.

---

## ⚙️ Features

### 🧮 Inventory Forecasting
- Clean and consolidate raw sales/inventory Excel files from Google Drive or OneDrive
- Apply DVF logic (Z-score) to detect SKU variability and seasonality
- Output master Excel files with reorder triggers, adaptable to BI dashboards

### ✍️ Shopify Blog Automation (Prototype)
- Extract high-intent keywords via Amazon & Google Ads API
- Generate SEO blog drafts using OpenAI
- Sync content to Shopify via API

### 🔗 API Integration
- Google Drive & OneDrive: Excel file automation
- Google Ads API: Keyword Planner & Search Volume
- Shopify Admin API: Blog/Product sync

---

## 🧰 Tech Stack

- Python 3
- Pandas / MySQL
- OpenAI GPT API
- Google Ads API
- Shopify Admin API
- Google Drive API / Microsoft Graph API (OneDrive)
- XlsxWriter for output
- Tableau (BI integration roadmap)

---

## 🚧 Roadmap

- [ ] Add Tableau-ready output format with sample dashboard
- [ ] Merge blog automation module into main inventory system
- [ ] Add `.env`-based secret & credential handling
- [ ] Design FastAPI backend for internal SaaS use
- [ ] Refactor logging & retry mechanisms for edge case handling

---

## 🗂️ Project Structure
ecommerce_analytics_db/
├── main.py                                # Runs client data sync and transformation
├── blog_generator_db_with_openai_module.py
├── blog_sync_db_with_shopify_module.py
├── google_ads_keyword_plan.py
├── google_ads_keyword_historical.py
├── product_sync_db_with_shopify_module.py
├── app_config.py                          # API keys, logging, config loader
├── app_utility.py                         # Column cleaner, date formatter, etc.
├── api_google_drive_functions.py
├── api_microsoft_onedrive_functions.py
├── client_file_mapping_config.py          # Per-client settings
└── logs/
---

## 👤 About

Built by **Gary Hsu**, a digital marketing and e-commerce strategist with 10+ years of experience scaling growth through automation, content systems, and full-stack operations.  
Email: [ghsu998@gmail.com](mailto:ghsu998@gmail.com)

> “This project is not a demo. It’s a real foundation built from real operations needs. I’m using it today—and building the future of it tomorrow.”