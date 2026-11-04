# Dot-source this in PowerShell to run demo scripts from the local uv venv
# against the Docker stack's published localhost ports:
#     . .\demo-env.ps1
#     python demos\demo.py all
& "$PSScriptRoot\.venv\Scripts\Activate.ps1"
$env:PYTHONPATH   = $PSScriptRoot
$env:AGENT_URL    = "http://localhost:8000"
$env:KEYCLOAK_URL = "http://localhost:8080"
$env:OPA_URL      = "http://localhost:8181"
$env:MLFLOW_TRACKING_URI = "http://localhost:5000"
$env:LANGFUSE_HOST = "http://localhost:3000"
$env:AGENT_SPIFFE_ID = "spiffe://governance.demo/agent/demo-agent"
$env:DATABASE_URL = "postgresql+psycopg2://agent_app:agent_app_change_me@localhost:5432/governance_demo"
$env:PYTHONIOENCODING = "utf-8"
# Langfuse keys for the compliance report, read from .env
Get-Content "$PSScriptRoot\.env" | Where-Object { $_ -match '^(LANGFUSE_PUBLIC_KEY|LANGFUSE_SECRET_KEY)=(.*)$' } |
    ForEach-Object { Set-Item "env:$($Matches[1])" $Matches[2] }
Write-Host "Demo env ready (venv active, pointing at localhost services)." -ForegroundColor Green
