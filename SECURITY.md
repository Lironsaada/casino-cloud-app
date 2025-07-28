# Security Guidelines

## 🔐 Environment Variables

The following environment variables contain sensitive information and must be configured securely:

### Required Environment Variables

1. **SECRET_KEY**: Flask session secret key
   - Generate a strong random key for production
   - Never use the default value in production
   - Example: `python -c "import secrets; print(secrets.token_hex(32))"`

2. **ADMIN_PASSWORD**: Admin panel access password
   - Set a strong, unique password for admin access
   - Never use default or easily guessable passwords
   - This replaces the previously hardcoded admin password

3. **GRAFANA_ADMIN_PASSWORD**: Grafana dashboard admin password
   - Required for monitoring dashboard access
   - Use a strong, unique password different from admin password

### Development Setup

Create a `.env` file in the project root (this file is ignored by Git):

```bash
SECRET_KEY=your-generated-secret-key-here
ADMIN_PASSWORD=your-secure-admin-password
GRAFANA_ADMIN_PASSWORD=your-grafana-admin-password
```

### Production Setup

Set environment variables in your deployment environment:

```bash
export SECRET_KEY="your-generated-secret-key-here"
export ADMIN_PASSWORD="your-secure-admin-password"
export GRAFANA_ADMIN_PASSWORD="your-grafana-admin-password"
```

## 🚨 Security Checklist

### Before Deployment
- [ ] All environment variables are set with secure values
- [ ] No hardcoded passwords in source code
- [ ] `.env` files are in `.gitignore`
- [ ] User data directories are in `.gitignore`
- [ ] Kubernetes secrets are properly configured
- [ ] Default passwords have been changed

### Kubernetes Secrets

For Kubernetes deployments, create secrets instead of using environment variables:

```bash
# Create admin secret
kubectl create secret generic casino-admin-secret \
  --from-literal=admin-password=your-secure-admin-password \
  --namespace=casino

# Create Grafana secret  
kubectl create secret generic grafana-admin-secret \
  --from-literal=admin-password=your-grafana-admin-password \
  --namespace=monitoring
```

## 🔒 Files to Never Commit

The following files should NEVER be committed to version control:

- `.env` - Environment variables
- `*.key` - Private keys
- `*.pem` - Certificate files
- `id_rsa*` - SSH keys
- `app/.users/` - User data directory
- `data/users.json` - User database
- `data/balance_history.json` - Transaction history

## 🛡️ Security Best Practices

1. **Password Security**
   - Use strong, unique passwords for all accounts
   - Never hardcode passwords in source code
   - Use environment variables or secrets management
   - Regularly rotate passwords

2. **Secret Management**
   - Use Kubernetes secrets for sensitive data
   - Encrypt secrets at rest
   - Limit access to secrets using RBAC
   - Audit secret access regularly

3. **Development Security**
   - Keep `.env` files local and never commit them
   - Use different passwords for development and production
   - Regularly scan for leaked credentials
   - Use tools like `git-secrets` to prevent accidental commits

4. **Monitoring Security**
   - Monitor for failed authentication attempts
   - Set up alerts for suspicious activity
   - Regularly review access logs
   - Keep security patches up to date

## 🚨 Emergency Response

If sensitive data has been accidentally committed:

1. **Immediate Actions**
   - Change all affected passwords immediately
   - Revoke any exposed API keys or tokens
   - Notify team members

2. **Git History Cleanup**
   ```bash
   # Remove sensitive file from all history
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch path/to/sensitive/file' \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push to update remote
   git push origin --force --all
   ```

3. **Verification**
   - Scan entire repository for sensitive data
   - Update all affected systems with new credentials
   - Document the incident for future prevention 