$ErrorActionPreference = "Stop"

$tempDir = Join-Path $env:TEMP "agentops-gh-pages"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Copy-Item -Recurse "frontend\dist\*" $tempDir

Push-Location $tempDir
try {
    git init
    git config user.name "Vijay Mahes"
    git config user.email "Vijaypradhap2004@gmail.com"
    git branch -M gh-pages
    git add .
    git commit -m "deploy: publish production build to gh-pages"
    git remote add origin "https://github.com/vijaymahes9080/AgentOps-Observatory.git"
    git push -u origin gh-pages --force
    Write-Host "Successfully deployed production build to gh-pages branch!"
}
finally {
    Pop-Location
    Remove-Item -Recurse -Force $tempDir
}
