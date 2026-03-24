git checkout -b feature/fase1-mejoras
touch control_file
git add control_file
git commit -m "feat: add control file for testing pipeline"
git push origin feature/fase1-mejoras
gh pr create --title "feat: add control file for testing pipeline" --body "This