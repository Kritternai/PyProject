#!/bin/bash

# Go to the project directory (optional, but good practice if you run from elsewhere)
cd /Users/kbbk/PyProject-1

# Set Environment Variables
export GOOGLE_CLIENT_ID="40820229782-0f7uoqd5ab94cuipmbdk09jeradqvac0.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="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"
export FLASK_SECRET_KEY="your_strong_random_flask_secret_key" # REMEMBER TO CHANGE THIS!
export OAUTHLIB_INSECURE_TRANSPORT="1"

# Activate Virtual Environment
source /Users/kbbk/PyProject-1/venv/bin/activate

# Set Flask Environment
export FLASK_APP=run.py

# Run Flask Application
flask run
