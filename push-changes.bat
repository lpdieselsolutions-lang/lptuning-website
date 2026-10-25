@echo off
cd /d "%~dp0"
echo Removing git lock if present...
if exist ".git\index.lock" del /f ".git\index.lock"
echo Committing vehicle-labels.html...
git config user.email "luukpietje@gmail.com"
git config user.name "Luuk Piet"
git add vehicle-labels.html
git commit -m "Add HL webhook + AdBlue tip + fix email template in vehicle-labels.html"
git push origin main
echo Done!
pause
