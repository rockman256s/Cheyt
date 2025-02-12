#!/bin/bash
git config --global user.email "noreply@replit.com"
git config --global user.name "Replit"

# Add all modified and new files
git add .

# Commit changes
git commit -m "Update Weight Calculator application with latest features"

# Configure remote with token
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/$(git remote get-url origin | sed 's/https:\/\/github.com\///')"

# Push changes
git push origin main