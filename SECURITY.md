# Security Guidelines

## Environment Variables

This application uses environment variables for sensitive configuration. Never commit these values to version control.

### Required Environment Variables

1. **SECRET_KEY**: Flask session secret key
   - Generate a strong random key for production
   - Example: `python3 -c "import secrets; print(secrets.token_hex(32))"`

2. **FLASK_ENV**: Application environment
   - Use `production` for live deployments
   - Use `development` for local development

### Setting Environment Variables

#### For Development
Create a `.env` file in the project root (this file is ignored by Git):

```bash
SECRET_KEY=your-generated-secret-key-here
FLASK_ENV=development
```

#### For Production
Set environment variables in your deployment platform:

```bash
export SECRET_KEY="your-generated-secret-key-here"
export FLASK_ENV="production"
```

## Password Security

- All passwords are hashed using Werkzeug's PBKDF2 implementation
- Plain text passwords are never stored
- Use the migration script to convert existing plain text passwords

## Data Files

The following files contain sensitive data and are excluded from Git:

- `users.json` - User accounts and balances
- `balance_history.json` - Transaction history
- `users.json.backup` - Backup of user data
- `.env` - Environment variables

## Security Checklist

- [ ] Set strong SECRET_KEY in production
- [ ] Use HTTPS in production
- [ ] Run password migration script before deployment
- [ ] Verify sensitive files are in .gitignore
- [ ] Never commit passwords or secrets to Git
- [ ] Use environment variables for all sensitive configuration

## Migration

If you have existing plain text passwords, run the migration script:

```bash
python3 migrate_passwords.py
```

This will:
1. Create a backup of your users.json file
2. Hash all plain text passwords
3. Update the data format to the new structure 