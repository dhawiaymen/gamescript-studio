$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($env:OS -ne "Windows_NT") { throw "Build Windows binaries on Windows." }
python -m pip install -c constraints-release.txt ".[dev]"
if ($LASTEXITCODE) { throw "Dependency installation failed" }
python -m pytest --junitxml=build-tests.xml
if ($LASTEXITCODE) { throw "Tests failed" }
python -m PyInstaller --noconfirm --clean --onedir --windowed --name GameScriptStudio --collect-all gamescript_studio launch.py
if ($LASTEXITCODE) { throw "Build failed" }
Copy-Item LICENSE,README.md,CHANGELOG.md -Destination dist/GameScriptStudio
Copy-Item examples -Destination dist/GameScriptStudio/examples -Recurse
python scripts/collect_licenses.py dist/GameScriptStudio
if ($LASTEXITCODE) { throw "License collection failed" }
python scripts/verify_distribution.py dist/GameScriptStudio GameScriptStudio gamescript-studio
if ($LASTEXITCODE) { throw "Extracted executable verification failed; do not publish" }
Write-Host "Verified archives and checksums are in release-assets/."
