# CI/CD Pipeline Documentation

This directory contains the simplified Continuous Integration and Continuous Deployment (CI/CD) configuration for the Smart Learning Hub project.

## 🚀 Workflow Overview

### **Main CI/CD Pipeline** (`main.yml`)
- **Triggers**: Push to main/dev branches, Pull Requests, Manual dispatch
- **Purpose**: Complete CI/CD pipeline in one workflow
- **Features**:
  - Code Quality & Security checks (Black, isort, Flake8, Bandit, Safety)
  - Testing with coverage (pytest)
  - Build validation for PRs
  - Automated deployment to Render (main branch only)
  - Post-deployment health checks
  - Test reports and artifacts

## 📋 Requirements

### GitHub Secrets
Configure these secrets in your repository settings:

- `RENDER_API_KEY`: Render API key for deployments
- `RENDER_SERVICE_ID`: Your Render service ID
- `RENDER_SERVICE_URL`: Your deployed service URL
- `CODECOV_TOKEN`: Codecov token for coverage (optional)

See [SECRETS_TEMPLATE.md](SECRETS_TEMPLATE.md) for detailed setup instructions.

### Dependencies
The workflow uses these essential Python packages:
- `pytest` - Testing framework
- `pytest-cov` - Coverage plugin
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `bandit` - Security analysis
- `safety` - Dependency security

## 🔧 Configuration Files

### Code Quality Configuration
- `.flake8` - Flake8 linting rules

### Workflow Configuration
- Single workflow with all necessary steps
- Python 3.11 environment
- Caching for faster builds
- Artifact uploads for test reports

## 📊 Reports and Artifacts

The main workflow generates:

- **Test Results**: pytest reports with coverage
- **Coverage Reports**: HTML and XML coverage data
- **Security Reports**: Bandit and Safety scan results
- **Deployment Logs**: Render deployment status and health checks

## 🎯 Quality Gates

The CI/CD pipeline enforces essential quality gates:

1. **Code Quality**: All code must pass Black, isort, and Flake8 checks
2. **Security**: No high-severity security issues allowed
3. **Testing**: Minimum 60% code coverage required
4. **Dependencies**: No known vulnerabilities in dependencies

## 🚀 Getting Started

1. **Set up secrets** in GitHub repository settings
2. **Push code** to trigger workflows
3. **Monitor progress** in the Actions tab
4. **Review reports** in workflow artifacts
5. **Fix issues** identified by the pipeline

## 🔍 Monitoring and Alerts

### Success Notifications
- Workflows post success messages to PR comments
- Coverage reports are automatically uploaded to Codecov
- Deployment status is logged and reported

### Failure Handling
- Failed workflows block deployments
- Security issues create GitHub issues
- Performance regressions are flagged
- Dependency vulnerabilities are reported

## 📈 Continuous Improvement

The CI/CD pipeline is designed to evolve:

1. **Add new tests** as features are developed
2. **Update quality gates** based on project needs
3. **Enhance security scanning** with new tools
4. **Improve performance testing** with realistic scenarios
5. **Expand coverage** to include more scenarios

## 🛠️ Troubleshooting

### Common Issues

1. **Workflow failures**: Check logs in Actions tab
2. **Secret errors**: Verify secrets are correctly configured
3. **Test failures**: Review test output and fix issues
4. **Deployment issues**: Check Render service configuration
5. **Performance regressions**: Analyze performance reports

### Getting Help

- Review workflow logs for detailed error messages
- Check uploaded artifacts for reports
- Ensure all secrets are properly configured
- Verify external service configurations (Render, Codecov)

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Render Deployment Guide](https://render.com/docs)
- [Codecov Integration](https://docs.codecov.com/docs)
- [Security Best Practices](https://docs.github.com/en/code-security)

---

**Smart Learning Hub CI/CD Pipeline** - Automated quality assurance and deployment 🚀
