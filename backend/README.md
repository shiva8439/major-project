# Backend README

See root setup_guide.md

**Run:**
```bash
cd backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**API Docs:** http://localhost:8000/docs

**Models:** Place .pth in `models/` folder
