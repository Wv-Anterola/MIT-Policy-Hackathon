# Compile LaTeX Policy Memo to PDF
# Requires: MiKTeX or TeX Live installation

Write-Host "Compiling LaTeX Policy Memo..." -ForegroundColor Cyan

# Check if pdflatex is available
$pdflatexPath = Get-Command pdflatex -ErrorAction SilentlyContinue

if (-not $pdflatexPath) {
    Write-Host "ERROR: pdflatex not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install a LaTeX distribution:" -ForegroundColor Yellow
    Write-Host "  - MiKTeX: https://miktex.org/download" -ForegroundColor Yellow
    Write-Host "  - TeX Live: https://www.tug.org/texlive/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or compile online at: https://www.overleaf.com/" -ForegroundColor Green
    exit 1
}

# Navigate to deliverables folder
Set-Location -Path "HACKATHON_DELIVERABLES"

Write-Host "Running pdflatex (first pass)..." -ForegroundColor Green
pdflatex -interaction=nonstopmode POLICY_MEMO_LATEX.tex | Out-Null

Write-Host "Running pdflatex (second pass for references)..." -ForegroundColor Green
pdflatex -interaction=nonstopmode POLICY_MEMO_LATEX.tex | Out-Null

# Clean up auxiliary files
Remove-Item -Path "*.aux", "*.log", "*.out" -ErrorAction SilentlyContinue

if (Test-Path "POLICY_MEMO_LATEX.pdf") {
    Write-Host ""
    Write-Host "SUCCESS! PDF created: HACKATHON_DELIVERABLES/POLICY_MEMO_LATEX.pdf" -ForegroundColor Green
    Write-Host ""
    
    # Open the PDF
    Start-Process "POLICY_MEMO_LATEX.pdf"
} else {
    Write-Host ""
    Write-Host "ERROR: PDF compilation failed!" -ForegroundColor Red
    Write-Host "Check POLICY_MEMO_LATEX.log for details" -ForegroundColor Yellow
}

# Return to parent directory
Set-Location -Path ".."
