# Virtual Environment Guide

## Quick Start

### Activate Virtual Environment

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Or use the batch file:**
```cmd
start_server.bat
```

### Start the Server

Once the venv is activated, you'll see `(venv)` in your prompt:

```powershell
(venv) PS> uvicorn app.main:app --reload
```

### Deactivate Virtual Environment

When you're done:
```powershell
deactivate
```

## Common Commands

### Install/Update Dependencies
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Check Installed Packages
```powershell
.\venv\Scripts\Activate.ps1
pip list
```

### Run Tests
```powershell
.\venv\Scripts\Activate.ps1
python test_setup.py
```

### Start Server
```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

## Notes

- The virtual environment is located in `backend/venv/`
- Always activate the venv before running Python commands
- The `start_server.bat` file automatically activates the venv
- Never commit the `venv/` folder to git (it's in `.gitignore`)
