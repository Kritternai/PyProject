#!/bin/bash

echo "🔧 Google OAuth Setup Script"
echo "================================"

# Get credentials from user
read -p "Enter your Google Client ID: " CLIENT_ID
read -p "Enter your Google Client Secret: " CLIENT_SECRET
read -p "Enter your Flask Secret Key: " SECRET_KEY

# Create .env file
cat > .env << EOL
# Flask Configuration
FLASK_SECRET_KEY=$SECRET_KEY
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URL=sqlite:///instance/site.db

# Google OAuth Configuration
GOOGLE_CLIENT_ID=$CLIENT_ID
GOOGLE_CLIENT_SECRET=$CLIENT_SECRET

# Server Configuration
PORT=5004
HOST=0.0.0.0
EOL

echo "✅ Environment variables configured!"
echo "✅ .env file created!"
echo ""
echo "Next steps:"
echo "1. Start the application: python start_server.py"
echo "2. Go to http://localhost:5004"
echo "3. Click 'Create New Class' → 'Import from Google Classroom'"
