# TYRO GPT Gateway

TYRO is a private, modular backend system powered by FastAPI and GPT, originally designed to support the creator's own workflows. It manages job tracking, financial records, client operations, and integrates with external services like GitHub and Notion. TYRO operates through a secure, chat-based interface, with role-based access that controls which APIs and modules are active.

> **Try it (guest mode):** [Launch TYRO Assistant](https://chatgpt.com/g/g-67e1bef044288191b4b0cb21e6132063-tyro-ai)

---

## Why TYRO?

While the project is public, it is not intended as a general-purpose tool. Most of its capabilities are private, available only to authenticated identities. Guest users (chat mode) can explore a limited subset via the chat interface, while elevated modes unlock operational and development features.

This structure allows TYRO to:
- Centralize operational logic into GPT-driven workflows
- Automate and log personal financial and job-related tasks
- Maintain modular separation of concerns
- Keep full control within a secure, identity-based access model

---

## Core Modules (WIP)

TYRO is composed of two main systems:

### 1. TYRO Gateway — API Control Center

Located in `tyro_gateway/`

- Modular routers for:
  - Client Relationship Management (CRM)
  - Job Applications & Resume Versioning
  - Tax Records (Personal & Business)
  - Investment Strategies (Stocks & Options)
- GitHub integration: auto commit, webhook deployment, repo scanning
- Notion API integration for structured data sync
- GPT_MODE system: loads different modules per user role

### 2. TYRO Data Clean — Preprocessing Engine

Located in `tyro_data_clean/`

- Ingests data from:
  - Google Drive
  - Microsoft OneDrive
  - MySQL databases
- Cleans and maps spreadsheet data
- Converts Excel to Google Sheets
- Supports data normalization for downstream AI usage

---

## Roles & Access

TYRO is identity-aware. Roles determine what each user can access:

| Role        | Description                             |
|-------------|-----------------------------------------|
| `chat`      | Guest mode via GPT interface            |
| `ops_team`  | Access to strategy and CRM modules      |
| `ops_root`  | Full access to ops-related modules      |
| `dev`       | Full developer access (GitHub tools, etc) |

> Access requires entering a private access code during chat.  
> There is no public signup or web login.

---

## Deployment & Status

- Live on private VPS (FastAPI + Uvicorn)
- GitHub Webhook CI/CD supported
- Health check endpoints:
  - `/` — base route
  - `/api/dev/project_status` — shows current GPT_MODE + loaded files
- Auto logs snapshot to `/logs/project_snapshot.json`

---

## Project Status

This project is actively evolving and used as a personal operations assistant. More features will be added as needs grow.

Future additions may include:
- Frontend admin UI (React or Streamlit)
- Authentication tokens for team-based access
- GPT-integrated prompt flows for smart strategy planning

---

## License

MIT License — this repo is public for reference, not intended for general use.
