# 🔐 Environment Variables Setup Guide

## Quick Setup

1. **Copy the example file to create your `.env`:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file with your actual credentials:**
   ```bash
   nano .env
   # or
   vim .env
   # or use your preferred editor
   ```

3. **Important:** Never commit the `.env` file to git (it's already in `.gitignore`)

---

## 📋 Required Environment Variables

### Database Configuration
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/botdo
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=botdo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
```

**How to get:**
- For development: Use the default values from docker-compose
- For production: Use your production database credentials

---

### Slack Configuration
```env
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_SIGNING_SECRET=your-slack-signing-secret-here
```

**How to get:**
1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Create a new app or select your existing app
3. **Bot Token**: Go to "OAuth & Permissions" → Copy "Bot User OAuth Token"
4. **App Token**: Go to "Basic Information" → "App-Level Tokens" → Generate Token
5. **Signing Secret**: Go to "Basic Information" → "App Credentials" → Copy "Signing Secret"

---

### Digital Ocean Configuration
```env
DIGITALOCEAN_API_KEY=dop_v1_your_api_key_here
DIGITALOCEAN_AGENT_ID=your-agent-id-here
DIGITALOCEAN_API_URL=https://api.digitalocean.com/v2
```

**How to get:**
1. Go to [https://cloud.digitalocean.com/account/api/tokens](https://cloud.digitalocean.com/account/api/tokens)
2. Click "Generate New Token"
3. Give it a name and select appropriate scopes
4. Copy the token (you won't be able to see it again!)
5. For Agent ID: Check your Digital Ocean Agent configuration

---

### Whapi (WhatsApp) Configuration
```env
WHAPI_API_KEY=your-whapi-api-key-here
WHAPI_BASE_URL=https://gate.whapi.cloud
WHAPI_CHANNEL_ID=your-channel-id-here
```

**How to get:**
1. Go to [https://whapi.cloud](https://whapi.cloud)
2. Sign up or log in
3. Create a new channel or use an existing one
4. Copy your API key from the dashboard
5. Copy your Channel ID

---

### Application Security
```env
SECRET_KEY=your-super-secret-key-min-32-chars-long
```

**How to generate a secure key:**
```bash
# Option 1: Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: Using OpenSSL
openssl rand -base64 32

# Option 3: Using /dev/urandom
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
```

---

### CORS Configuration
```env
CORS_ORIGINS=http://localhost:3000,http://frontend:3000
```

**Notes:**
- Comma-separated list of allowed origins
- No spaces between URLs
- For production, add your production domain

---

## 🚨 Security Best Practices

1. **Never commit `.env` files to version control**
   - Already included in `.gitignore`
   - Double-check before pushing

2. **Use different credentials for development and production**
   - Keep production secrets separate
   - Use a secrets manager in production (AWS Secrets Manager, HashiCorp Vault, etc.)

3. **Rotate keys regularly**
   - Especially after team member changes
   - If you suspect a key has been compromised

4. **Minimum permissions principle**
   - Give API keys only the permissions they need
   - Use read-only keys where possible

5. **Backup your `.env` securely**
   - Use encrypted storage
   - Don't share via unsecured channels (email, Slack, etc.)

---

## 🧪 Testing Your Configuration

After setting up your `.env` file:

```bash
# Test with docker-compose
docker-compose up backend

# You should see:
# ✅ All required environment variables loaded successfully
```

If you see an error like:
```
❌ Environment Configuration Error: Required environment variable 'SLACK_BOT_TOKEN' is not set.
💡 Please create a .env file based on .env.example
```

This means you need to add that variable to your `.env` file.

---

## 🔧 Troubleshooting

### "Required environment variable not set" error
- Make sure `.env` file exists in the project root
- Check that variable names match exactly (they're case-sensitive)
- Ensure there are no spaces around the `=` sign
- Verify the file has no empty values (e.g., `SLACK_BOT_TOKEN=`)

### Variables not loading in Docker
- Restart containers: `docker-compose down && docker-compose up`
- Rebuild images: `docker-compose up --build`
- Check that `env_file: - .env` is in docker-compose.yml

### Values with special characters
- If your value contains special characters, wrap it in quotes:
  ```env
  PASSWORD="my-p@ssw0rd-with-$pecial-chars!"
  ```

---

## 📝 Development vs Production

### Development (Local)
```env
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/botdo
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
LOG_LEVEL=DEBUG
```

### Production
```env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:secure_pass@prod-db:5432/botdo_prod
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
LOG_LEVEL=INFO
```

---

## 🆘 Need Help?

If you're having trouble setting up environment variables:
1. Check this guide thoroughly
2. Verify all API credentials are valid
3. Test each integration separately
4. Check application logs for specific errors

Remember: The application will refuse to start if any required variable is missing. This is a security feature, not a bug! 🔒

