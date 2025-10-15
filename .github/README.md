# CI/CD Pipeline Documentation

This directory contains the Continuous Integration and Continuous Deployment (CI/CD) configuration for the Smart Learning Hub project.

## 🚀 Workflows Overview

### 1. **CI Pipeline** (`ci.yml`)
- **Triggers**: Push to main/dev branches, Pull Requests
- **Purpose**: Code quality, testing, and validation
- **Jobs**:
  - Code Quality & Linting (Black, isort, Flake8, Bandit)
  - Testing (pytest with coverage)
  - Build validation
  - Security scanning

### 2. **Deployment** (`deploy.yml`)
- **Triggers**: Push to main branch, Manual dispatch
- **Purpose**: Automated deployment to Render
- **Jobs**:
  - Pre-deployment checks
  - Deploy to Render
  - Post-deployment health checks
  - Performance validation

### 3. **Code Coverage** (`coverage.yml`)
- **Triggers**: Push to main/dev branches, Pull Requests
- **Purpose**: Track code coverage metrics
- **Features**:
  - Coverage reports with Codecov integration
  - Coverage trend analysis
  - PR comments with coverage details

### 4. **Performance Testing** (`performance.yml`)
- **Triggers**: Push to main, Pull Requests, Manual dispatch
- **Purpose**: Performance and load testing
- **Jobs**:
  - Load testing with Locust
  - Stress testing
  - Memory and CPU profiling

### 5. **Security Scanning** (`security.yml`)
- **Triggers**: Push to main/dev branches, Pull Requests, Daily schedule
- **Purpose**: Security vulnerability detection
- **Jobs**:
  - Code security analysis (Bandit, Semgrep)
  - Dependency vulnerability scanning (Safety, pip-audit)
  - Container security (Trivy)

### 6. **Dependency Updates** (`dependency-update.yml`)
- **Triggers**: Weekly schedule, Manual dispatch
- **Purpose**: Monitor and update dependencies
- **Features**:
  - Automated dependency checking
  - Security vulnerability reports
  - Auto-update minor versions

## 📋 Requirements

### GitHub Secrets
Configure these secrets in your repository settings:

- `RENDER_API_KEY`: Render API key for deployments
- `RENDER_SERVICE_ID`: Your Render service ID
- `RENDER_SERVICE_URL`: Your deployed service URL
- `CODECOV_TOKEN`: Codecov token for coverage (optional)

See [SECRETS_TEMPLATE.md](SECRETS_TEMPLATE.md) for detailed setup instructions.

### Dependencies
The workflows use these Python packages:
- `pytest` - Testing framework
- `pytest-cov` - Coverage plugin
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `bandit` - Security analysis
- `safety` - Dependency security
- `locust` - Load testing

## 🔧 Configuration Files

### Code Quality Configuration
- `.flake8` - Flake8 linting rules
- `pyproject.toml` - Black, isort, pytest, coverage, mypy configuration

### Workflow Configuration
- All workflows are configured with appropriate triggers and environments
- Matrix testing across Python versions (3.11, 3.12)
- Caching for faster builds
- Artifact uploads for reports and results

## 📊 Reports and Artifacts

Each workflow generates various reports:

### CI Pipeline
- Security reports (Bandit, Safety)
- Test results and coverage
- Build artifacts

### Deployment
- Deployment logs
- Health check results
- Performance metrics

### Coverage
- HTML coverage reports
- XML coverage data
- Coverage trend analysis

### Performance
- Load test results
- Stress test reports
- Memory/CPU profiling data

### Security
- Bandit security reports
- Dependency vulnerability reports
- Semgrep scan results

## 🎯 Quality Gates

The CI/CD pipeline enforces several quality gates:

1. **Code Quality**: All code must pass Black, isort, and Flake8 checks
2. **Security**: No high-severity security issues allowed
3. **Testing**: Minimum 70% code coverage required
4. **Performance**: Response times must be under 2 seconds
5. **Dependencies**: No known vulnerabilities in dependencies

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
