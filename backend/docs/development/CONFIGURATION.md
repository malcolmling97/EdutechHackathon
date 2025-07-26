# Backend Configuration Guide

This document outlines all the configuration options and environment variables needed for the EdutechHackathon FastAPI backend.

## Environment Variables Setup

Create a `.env` file in the backend root directory with the following configuration:

```bash
# EdutechHackathon Backend Environment Configuration
# Copy these settings to your .env file and fill in your actual values

# ===== CORE APPLICATION SETTINGS =====
ENVIRONMENT=development
DEBUG=true
APP_NAME="EdutechHackathon API"
APP_VERSION="1.0.0"
PORT=8000
HOST=0.0.0.0

# ===== DATABASE CONFIGURATION =====
# SQLite (Development)
DATABASE_URL="sqlite:///./data/edutech.db"

# PostgreSQL (Production - uncomment and configure as needed)
# DATABASE_URL="postgresql://user:password@localhost:5432/edutech_db"
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=edutech_user
# DB_PASSWORD=your_secure_password
# DB_NAME=edutech_db

# ===== SECURITY & AUTHENTICATION =====
# Generate a secure secret key: openssl rand -hex 32
JWT_SECRET_KEY="your-super-secret-jwt-key-at-least-32-characters-long-please-change-this"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=24

# Password hashing configuration
BCRYPT_ROUNDS=12

# ===== AI/ML INTEGRATION =====
# OpenAI Configuration
OPENAI_API_KEY="your-openai-api-key-here"
OPENAI_MODEL="gpt-4"
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000
OPENAI_TIMEOUT=30

# Alternative AI Providers (optional)
# ANTHROPIC_API_KEY="your-anthropic-api-key"
# HUGGINGFACE_API_KEY="your-huggingface-api-key"

# ===== FILE PROCESSING & STORAGE =====
# File Upload Configuration
MAX_FILE_SIZE=26214400  # 25MB in bytes
ALLOWED_FILE_TYPES="application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,text/markdown"

# Storage Configuration
UPLOAD_DIR="./uploads"
TEMP_DIR="./temp"

# ===== CORS CONFIGURATION =====
CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001"
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS="GET,POST,PUT,PATCH,DELETE,OPTIONS"
CORS_ALLOW_HEADERS="Content-Type,Authorization,X-User-Id"

# ===== RATE LIMITING =====
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60  # seconds
RATE_LIMIT_STORAGE="memory"  # or "redis"

# ===== REDIS CONFIGURATION (Optional) =====
# REDIS_URL="redis://localhost:6379/0"
# REDIS_HOST=localhost
# REDIS_PORT=6379
# REDIS_DB=0
# REDIS_PASSWORD=""

# ===== LOGGING CONFIGURATION =====
LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT="json"  # json or text
LOG_FILE="./logs/app.log"

# ===== MONITORING & OBSERVABILITY =====
# Sentry Error Tracking (optional)
# SENTRY_DSN="your-sentry-dsn-here"
# SENTRY_ENVIRONMENT="development"

# Prometheus Metrics (optional)
# METRICS_ENABLED=false
# METRICS_PATH="/metrics"

# ===== TESTING CONFIGURATION =====
# Test Database (separate from main DB)
TEST_DATABASE_URL="sqlite:///./test_data/test_edutech.db"

# ===== DEVELOPMENT TOOLS =====
# Auto-reload for development
RELOAD=true

# API Documentation
DOCS_URL="/docs"
REDOC_URL="/redoc"
OPENAPI_URL="/openapi.json"

# ===== BACKGROUND TASKS (Optional - Celery) =====
# CELERY_BROKER_URL="redis://localhost:6379/1"
# CELERY_RESULT_BACKEND="redis://localhost:6379/1"

# ===== PRODUCTION SETTINGS =====
# Uncomment and configure for production deployment

# WORKERS=4  # Number of worker processes
# WORKER_CLASS="uvicorn.workers.UvicornWorker"
# WORKER_CONNECTIONS=1000
# MAX_REQUESTS=1000
# MAX_REQUESTS_JITTER=100

# SSL Configuration (Production)
# SSL_KEYFILE="/path/to/keyfile.key"
# SSL_CERTFILE="/path/to/certfile.crt"

# Security Headers
# SECURE_HEADERS=true
# HSTS_MAX_AGE=31536000
# FORCE_HTTPS=false

# ===== FEATURE FLAGS =====
# Enable/disable specific features
CHAT_FEATURE_ENABLED=true
QUIZ_FEATURE_ENABLED=true
NOTES_FEATURE_ENABLED=true
FILE_UPLOAD_ENABLED=true
STREAMING_ENABLED=true

# AI Features
AI_CHAT_ENABLED=true
AI_QUIZ_GENERATION_ENABLED=true
AI_NOTES_GENERATION_ENABLED=true

# ===== PERFORMANCE TUNING =====
# Database connection pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# HTTP Client Settings
HTTP_TIMEOUT=30
HTTP_MAX_CONNECTIONS=100
HTTP_MAX_KEEPALIVE_CONNECTIONS=20

# ===== BACKUP & MAINTENANCE =====
# Backup configuration (if needed)
# BACKUP_ENABLED=false
# BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
# BACKUP_RETENTION_DAYS=30
```

## Configuration Categories

### 1. Core Application Settings

These settings control the basic behavior of the FastAPI application:

- **ENVIRONMENT**: Sets the deployment environment (development, staging, production)
- **DEBUG**: Enables/disables debug mode
- **PORT**: Port number for the server to listen on
- **HOST**: Host address to bind to

### 2. Database Configuration

The application supports both SQLite and PostgreSQL:

**SQLite (Development):**
- Simple file-based database
- No additional setup required
- Perfect for development and testing

**PostgreSQL (Production):**
- Scalable relational database
- Requires separate PostgreSQL server
- Recommended for production deployments

## Switching from SQLite to PostgreSQL

### Prerequisites

Before switching to PostgreSQL, ensure you have:

1. **PostgreSQL Server**: A running PostgreSQL instance (local or remote)
2. **Database Credentials**: Username, password, host, port, and database name
3. **Python Dependencies**: PostgreSQL adapter for Python

### Step-by-Step Instructions

#### 1. Install PostgreSQL Dependencies

Add the PostgreSQL adapter to your Python environment:

```bash
# Install psycopg2 (PostgreSQL adapter)
pip install psycopg2-binary

# Or if you prefer the source version (requires PostgreSQL dev headers)
pip install psycopg2

# Update requirements.txt
echo "psycopg2-binary>=2.9.0" >> requirements.txt
```

#### 2. Create PostgreSQL Database

Connect to your PostgreSQL server and create a database:

```sql
-- Connect to PostgreSQL as superuser or database admin
psql -U postgres

-- Create database
CREATE DATABASE edutech_db;

-- Create user (optional, for better security)
CREATE USER edutech_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE edutech_db TO edutech_user;

-- Exit psql
\q
```

#### 3. Update Environment Configuration

In your `.env` file, replace the SQLite configuration with PostgreSQL:

**Before (SQLite):**
```bash
DATABASE_URL="sqlite:///./data/edutech.db"
```

**After (PostgreSQL):**
```bash
# PostgreSQL Configuration
DATABASE_URL="postgresql://edutech_user:your_secure_password@localhost:5432/edutech_db"

# Alternative: Individual PostgreSQL settings (optional)
DB_HOST=localhost
DB_PORT=5432
DB_USER=edutech_user
DB_PASSWORD=your_secure_password
DB_NAME=edutech_db
```

#### 4. Database URL Format Reference

PostgreSQL connection strings follow this format:
```
postgresql://[user[:password]@][host][:port][/database][?param1=value1&...]
```

**Examples:**
```bash
# Local PostgreSQL with user/password
DATABASE_URL="postgresql://user:password@localhost:5432/edutech_db"

# Remote PostgreSQL server
DATABASE_URL="postgresql://user:password@db.example.com:5432/edutech_db"

# PostgreSQL with SSL (recommended for production)
DATABASE_URL="postgresql://user:password@host:5432/edutech_db?sslmode=require"

# Cloud PostgreSQL (e.g., AWS RDS, Google Cloud SQL)
DATABASE_URL="postgresql://user:password@your-instance.region.rds.amazonaws.com:5432/edutech_db"
```

#### 5. Initialize Database Schema

Since you're switching databases (not migrating data), you need to recreate the schema:

```bash
# Stop the application if running
# Then run the database initialization

cd EdutechHackathon/backend

# Method 1: Using the application startup (recommended)
python -c "
from app.core.database import create_tables
create_tables()
print('Database tables created successfully!')
"

# Method 2: Using the main application
python -m app.main --init-db

# Method 3: Using pytest to run database setup
python -m pytest --no-cov -v tests/test_database_setup.py
```

#### 6. Verify the Switch

Test that PostgreSQL is working correctly:

```bash
# 1. Start the application
python -m uvicorn app.main:app --reload

# 2. Check the logs for database connection confirmation
# Look for: "Database connection established" or similar

# 3. Test with a simple API call
curl http://localhost:8000/api/v1/health

# 4. Run authentication tests to verify database operations
python -m pytest tests/test_auth.py -v
```

#### 7. Common Configuration Options

**Connection Pool Settings** (add to .env for production):
```bash
# Database connection pool configuration
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

**SSL Configuration** (for production):
```bash
# Require SSL connection
DATABASE_URL="postgresql://user:password@host:5432/edutech_db?sslmode=require"

# With SSL certificate verification
DATABASE_URL="postgresql://user:password@host:5432/edutech_db?sslmode=verify-full&sslcert=client-cert.pem&sslkey=client-key.pem&sslrootcert=ca-cert.pem"
```

### Troubleshooting

**Common Issues and Solutions:**

1. **psycopg2 Installation Error:**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install libpq-dev python3-dev
   
   # On macOS
   brew install postgresql
   
   # Then reinstall
   pip install psycopg2-binary
   ```

2. **Connection Refused:**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check if PostgreSQL accepts connections: `psql -h localhost -U postgres -l`
   - Verify firewall settings and PostgreSQL configuration

3. **Authentication Failed:**
   - Double-check username and password
   - Verify user has access to the database
   - Check PostgreSQL's `pg_hba.conf` for authentication methods

4. **Database Does Not Exist:**
   ```sql
   -- Connect and create database
   psql -U postgres
   CREATE DATABASE edutech_db;
   ```

### Performance Considerations

**PostgreSQL vs SQLite Performance:**

| Aspect | SQLite | PostgreSQL |
|--------|--------|------------|
| **Setup** | Zero config | Requires server setup |
| **Concurrency** | Limited (file locking) | Excellent (MVCC) |
| **Scalability** | Single file limit | Highly scalable |
| **Features** | Basic SQL | Advanced SQL, JSON, Extensions |
| **Use Case** | Development, Small apps | Production, Large apps |

**When to Switch:**
- **Development to Production**: Always recommended
- **Multiple Users**: PostgreSQL handles concurrent access better
- **Large Datasets**: PostgreSQL offers better performance
- **Advanced Features**: Need JSON columns, full-text search, etc.

### Environment-Specific Database Configuration

**Development:**
```bash
# Use SQLite for simplicity
DATABASE_URL="sqlite:///./data/edutech.db"
```

**Staging:**
```bash
# Use PostgreSQL matching production
DATABASE_URL="postgresql://user:password@staging-db:5432/edutech_staging"
```

**Production:**
```bash
# Use PostgreSQL with SSL and connection pooling
DATABASE_URL="postgresql://user:password@prod-db:5432/edutech_prod?sslmode=require"
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=100
```

### 3. Security & Authentication

**JWT Configuration:**
- **JWT_SECRET_KEY**: Secret key for signing JWT tokens (must be secure)
- **JWT_ALGORITHM**: Algorithm used for JWT signing (HS256 recommended)
- **JWT_EXPIRATION_HOURS**: Token expiration time

**Password Security:**
- **BCRYPT_ROUNDS**: Number of salt rounds for password hashing

### 4. AI/ML Integration

**OpenAI Configuration:**
- **OPENAI_API_KEY**: Your OpenAI API key (required for AI features)
- **OPENAI_MODEL**: GPT model to use (gpt-4 or gpt-3.5-turbo)
- **OPENAI_TEMPERATURE**: Creativity level (0.0-1.0)
- **OPENAI_MAX_TOKENS**: Maximum response length

### 5. File Processing

**Upload Limits:**
- **MAX_FILE_SIZE**: Maximum file size in bytes (default: 25MB)
- **ALLOWED_FILE_TYPES**: Comma-separated list of allowed MIME types

**Storage Paths:**
- **UPLOAD_DIR**: Directory for uploaded files
- **TEMP_DIR**: Temporary file processing directory

### 6. CORS Configuration

Cross-Origin Resource Sharing settings for frontend integration:

- **CORS_ORIGINS**: Allowed frontend URLs
- **CORS_ALLOW_CREDENTIALS**: Enable credential sharing
- **CORS_ALLOW_METHODS**: Allowed HTTP methods
- **CORS_ALLOW_HEADERS**: Allowed request headers

### 7. Rate Limiting

Protect the API from abuse:

- **RATE_LIMIT_ENABLED**: Enable/disable rate limiting
- **RATE_LIMIT_REQUESTS**: Number of requests allowed
- **RATE_LIMIT_WINDOW**: Time window in seconds

### 8. Optional Services

**Redis (Caching & Sessions):**
- **REDIS_URL**: Redis connection string
- Configure for production caching and session storage

**Celery (Background Tasks):**
- **CELERY_BROKER_URL**: Message broker URL
- **CELERY_RESULT_BACKEND**: Result storage backend

### 9. Monitoring & Logging

**Logging:**
- **LOG_LEVEL**: Minimum log level to capture
- **LOG_FORMAT**: Log format (json or text)
- **LOG_FILE**: Log file location

**Error Tracking:**
- **SENTRY_DSN**: Sentry error tracking URL

### 10. Feature Flags

Enable/disable specific features for gradual rollouts:

- **CHAT_FEATURE_ENABLED**: Enable chat functionality
- **QUIZ_FEATURE_ENABLED**: Enable quiz generation
- **NOTES_FEATURE_ENABLED**: Enable notes generation
- **AI_*_ENABLED**: Individual AI feature toggles

## Environment-Specific Configurations

### Development Configuration

```bash
ENVIRONMENT=development
DEBUG=true
DATABASE_URL="sqlite:///./data/edutech.db"
LOG_LEVEL="DEBUG"
RELOAD=true
```

### Production Configuration

```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL="postgresql://user:pass@host:5432/db"
LOG_LEVEL="INFO"
WORKERS=4
SECURE_HEADERS=true
```

### Testing Configuration

```bash
ENVIRONMENT=test
DEBUG=false
DATABASE_URL="sqlite:///./test_data/test.db"
LOG_LEVEL="WARNING"
```

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong, randomly generated JWT secrets**
3. **Rotate API keys regularly**
4. **Use environment-specific configurations**
5. **Enable HTTPS in production**
6. **Configure proper CORS origins**
7. **Set up monitoring and logging**

## Quick Setup for Development

1. Copy the configuration template above to a `.env` file
2. Generate a secure JWT secret: `openssl rand -hex 32`
3. Add your OpenAI API key
4. Adjust file paths as needed
5. Start the development server: `uvicorn app.main:app --reload`

This configuration setup ensures your FastAPI backend is properly configured for development, testing, and production environments. 