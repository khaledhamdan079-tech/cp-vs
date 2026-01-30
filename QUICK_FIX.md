# Quick Fix: npm not recognized

If you see "npm is not recognized" error, use one of these solutions:

## Solution 1: Refresh PATH in Current Terminal (Quick Fix)

Run this command in your PowerShell:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

Then verify:
```powershell
node --version
npm --version
```

Now you can run:
```powershell
cd "C:\Users\khaled\Desktop\projects\CP VS\frontend"
npm run dev
```

## Solution 2: Use the PowerShell Script

Run the provided script:
```powershell
cd "C:\Users\khaled\Desktop\projects\CP VS"
.\start_frontend.ps1
```

## Solution 3: Restart Terminal (Permanent Fix)

1. Close your current PowerShell/terminal window
2. Open a new PowerShell window
3. Node.js should now be available

## Solution 4: Use Full Path (Temporary)

```powershell
& "C:\Program Files\nodejs\npm.cmd" run dev
```

## Why This Happens

When Node.js is installed, it adds itself to the system PATH. However, terminals that were already open don't automatically pick up the new PATH. You need to either:
- Refresh PATH in the current session (Solution 1)
- Restart the terminal (Solution 3)

## Recommended: Use the Batch File

The easiest way is to use the batch file which handles PATH automatically:

```cmd
cd "C:\Users\khaled\Desktop\projects\CP VS"
start_frontend.bat
```
