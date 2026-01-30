# Installing Node.js and npm

Node.js is required to run the frontend. Here are the installation options:

## Option 1: Download Installer (Recommended)

1. **Download Node.js:**
   - Go to: https://nodejs.org/
   - Download the **LTS (Long Term Support)** version
   - Choose the Windows Installer (.msi) for your system (64-bit)

2. **Run the Installer:**
   - Double-click the downloaded `.msi` file
   - Follow the installation wizard
   - **Important:** Make sure "Add to PATH" is checked during installation
   - Complete the installation

3. **Verify Installation:**
   - Open a **new** PowerShell/Command Prompt window
   - Run:
     ```powershell
     node --version
     npm --version
     ```
   - You should see version numbers (e.g., v20.10.0 and 10.2.3)

4. **Restart Your Terminal:**
   - Close and reopen your terminal/PowerShell
   - This ensures PATH changes take effect

## Option 2: Using Winget (Windows Package Manager)

If you have Windows 10/11 with winget:

```powershell
winget install OpenJS.NodeJS.LTS
```

Then restart your terminal and verify:
```powershell
node --version
npm --version
```

## Option 3: Using Chocolatey

If you have Chocolatey installed:

```powershell
choco install nodejs-lts
```

Then restart your terminal and verify:
```powershell
node --version
npm --version
```

## After Installation

Once Node.js is installed, you can set up the frontend:

```powershell
cd "C:\Users\khaled\Desktop\projects\CP VS\frontend"
npm install
npm run dev
```

## Troubleshooting

**"npm is not recognized" after installation:**
- Close and reopen your terminal/PowerShell
- Restart your computer if needed
- Verify PATH: Check if `C:\Program Files\nodejs\` is in your PATH environment variable

**Check PATH:**
```powershell
$env:PATH -split ';' | Select-String nodejs
```

If Node.js path is not there, you may need to add it manually or reinstall Node.js with "Add to PATH" option checked.
