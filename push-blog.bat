@echo off
cd /d "%~dp0"
echo Clearing any stale git lock...
if exist ".git\index.lock" del /f ".git\index.lock"
git config user.email "luukpietje@gmail.com"
git config user.name "Luuk Piet"
git add -A website
git add blog-earthmoving-tuning-results-cat-d6-komatsu-wa600.html scripts/clean_dashes.py cat-d6-on-site.webp komatsu-wa600-test-drive.mp4 komatsu-wa600-test-drive-poster.webp
git commit -m "New earthmoving results post, truck page update, diesel price 2.80/L, remove em dashes site-wide, blog generator guardrails" -- website cat-d6-on-site.webp komatsu-wa600-test-drive.mp4 komatsu-wa600-test-drive-poster.webp 4wd-tuning.html adblue-delete.html agricultural-tuning.html blog-adblue-delete-tractors-heavy-machinery-queensland.html blog-combine-harvester-tuning-queensland.html blog-dpf-problems-farm-machinery.html blog-earthmoving-equipment-tuning-queensland.html blog-ecu-remapping-tractors-queensland.html blog-egr-delete-farm-machinery-queensland.html blog-fuel-savings-mining-equipment.html blog-fuel-savings-tractor-heavy-machinery-queensland.html blog-hilux-diesel-tuning-brisbane.html blog-john-deere-ecu-tuning-queensland.html blog-komatsu-cat-excavator-tuning-queensland.html blog-landcruiser-ecu-tuning-queensland.html blog-tractor-ecu-tuning-queensland.html blog.html cloudflare-setup-guide.md dpf-delete.html ecu-remapping-vs-chip-tuning.html ecu-remapping.html egr-delete.html free-fuel-check.backup-2026-10-09.html free-fuel-check.html index.html mining-tuning.html privacy-policy.html scripts/generate_blog.py sitemap.xml truck-tuning.html vehicle-labels.html blog-earthmoving-tuning-results-cat-d6-komatsu-wa600.html scripts/clean_dashes.py 
git commit -m "Fix auto-blog workflow: Monday/Thursday schedule, rebase before push, model fallback" -- .github/workflows/auto-blog.yml scripts/generate_blog.py
git pull --rebase --autostash origin main
git push origin main
echo Done. Netlify will publish in a minute or two.
pause
