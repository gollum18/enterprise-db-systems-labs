Set-Item -Path Env:FLASK_APP -Value app.py
Set-Item -Path Env:FLASK_ENV -Value development

Invoke-Expression -Command:"flask run"
