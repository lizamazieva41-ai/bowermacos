# 1. TRIỂN KHAI

## Môi trường
| Môi trường | OS | Python |
|-------------|-----|--------|
| Development | Ubuntu 22.04/Win11/Mac | 3.10+ |
| Production | Ubuntu 22.04 LTS | 3.11+ |

## Hardware Requirements
| Tier | CPU | RAM | Profiles |
|------|-----|-----|----------|
| Small | 4 cores | 8 GB | 10-20 |
| Medium | 8 cores | 16 GB | 30-50 |

## Setup
```bash
python -m venv venv
pip install -r requirements.txt
playwright install chromium
```

## Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

*Document ID: ABB-V2-DOC-1001*
