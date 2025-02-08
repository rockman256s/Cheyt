#!/bin/bash
git config --global user.email "noreply@replit.com"
git config --global user.name "Replit"

# Add files
git add main.py .streamlit/config.toml

# Commit
git commit -m "Add interpolation curve visualization and calculation features"

# Configure remote with token
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/$(git remote get-url origin | sed 's/https:\/\/github.com\///')"

# Push changes
git push origin main
