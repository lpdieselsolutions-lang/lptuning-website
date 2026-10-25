@echo off
cd /d "%~dp0"
if exist .git\index.lock move /y .git\index.lock .git\stale-index-lock-%RANDOM% >nul 2>&1
git config user.name >nul 2>&1 || git config user.name "Luuk Piet"
git config user.email >nul 2>&1 || git config user.email "luukpietje@gmail.com"
echo Checking for changes...
git add -A
git diff --cached --quiet || git commit -m "Website update %DATE% %TIME%"
echo Getting the latest from GitHub...
git pull --no-rebase --no-edit origin main
if errorlevel 1 (
  echo Merge problem, undoing the merge so nothing is lost.
  git merge --abort
  goto fail
)
echo Publishing...
git push origin main
if errorlevel 1 goto fail
echo.
echo DONE_OK
exit /b 0
:fail
echo.
echo DONE_FAIL
exit /b 1
