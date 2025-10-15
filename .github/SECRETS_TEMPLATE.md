# GitHub Secrets Configuration

This document outlines the required secrets for the CI/CD pipeline to work properly.

## Required Secrets

### For Deployment (Render)

1. **RENDER_API_KEY**
   - Description: Render API key for automated deployments
   - How to get: Go to Render Dashboard → Account Settings → API Keys
   - Format: `rnd_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

2. **RENDER_SERVICE_ID**
   - Description: Your Render service ID
   - How to get: Go to your service on Render → Settings → General
   - Format: `srv-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

3. **RENDER_SERVICE_URL**
   - Description: Your deployed service URL (optional, for health checks)
   - Format: `https://your-app-name.onrender.com`

### For Security Scanning (Optional)

4. **CODECOV_TOKEN**
   - Description: Codecov token for coverage reporting
   - How to get: Go to Codecov.io → Add repository → Get token
   - Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

## How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the exact name and value

## Security Notes

- Never commit these secrets to your repository
- Secrets are encrypted and only accessible to GitHub Actions
- Each secret is masked in logs and outputs
- Consider using environment-specific secrets for different deployments

## Environment Variables for Local Development

For local development, create a `.env` file with these variables:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
FLASK_SECRET_KEY=your_development_secret_key

# Database
DATABASE_URL=sqlite:///site.db

# Google OAuth (for development)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Security
OAUTHLIB_INSECURE_TRANSPORT=1
```

## Production Environment Variables

For production deployment on Render, set these environment variables in the Render dashboard:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_SECRET_KEY=your_production_secret_key

# Database (automatically set by Render)
DATABASE_URL=postgresql://...

# Google OAuth
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_CLIENT_SECRET=your_production_google_client_secret

# Security
OAUTHLIB_INSECURE_TRANSPORT=0
```

## Testing the CI/CD Pipeline

1. Add all required secrets to your repository
2. Create a test branch and push changes
3. Check the Actions tab to see workflows running
4. Verify that:
   - Code quality checks pass
   - Tests run successfully
   - Security scans complete
   - Deployment works (if on main branch)

## Troubleshooting

### Common Issues

1. **Deployment fails**: Check if RENDER_API_KEY and RENDER_SERVICE_ID are correct
2. **Health check fails**: Verify RENDER_SERVICE_URL is set correctly
3. **Coverage upload fails**: Check if CODECOV_TOKEN is valid
4. **Security scan fails**: Review the security reports in artifacts

### Getting Help

- Check the Actions logs for detailed error messages
- Review the uploaded artifacts for reports
- Ensure all secrets are properly configured
- Verify your Render service is properly set up
