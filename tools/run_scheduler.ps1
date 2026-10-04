# PowerShell helper to run the email scheduler as a background job
python -m pip install -r requirements.txt
Start-Process -NoNewWindow -FilePath python -ArgumentList "tools\\email_scheduler.py"
Write-Output "Email scheduler started (detached process)."