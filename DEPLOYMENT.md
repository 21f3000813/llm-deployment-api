# Deployment Guide

## Production Deployment

### Student API Deployment

#### Option 1: Heroku

1. **Install Heroku CLI**:
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku app**:
   ```bash
   heroku create my-llm-deployment
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set STUDENT_EMAIL=your@email.com
   heroku config:set STUDENT_SECRET=your-secret
   heroku config:set GITHUB_TOKEN=ghp_your_token
   heroku config:set GITHUB_USERNAME=your-username
   heroku config:set OPENAI_API_KEY=sk-your-key
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

5. **Verify**:
   ```bash
   heroku logs --tail
   heroku open
   ```

#### Option 2: DigitalOcean App Platform

1. Connect GitHub repository
2. Set environment variables in dashboard
3. Configure build command: `npm install`
4. Configure run command: `npm start`
5. Deploy

#### Option 3: AWS Lambda + API Gateway

1. **Package application**:
   ```bash
   npm install --production
   zip -r function.zip .
   ```

2. **Create Lambda function** in AWS Console
3. **Set up API Gateway** trigger
4. **Configure environment variables**
5. **Test endpoint**

### Instructor System Deployment

#### Database Setup (PostgreSQL)

1. **Install PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Create database**:
   ```sql
   CREATE DATABASE llm_deployment;
   CREATE USER instructor WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE llm_deployment TO instructor;
   ```

3. **Update DATABASE_URL**:
   ```
   DATABASE_URL=postgresql://instructor:secure_password@localhost:5432/llm_deployment
   ```

#### Evaluation API Deployment

1. **Install production server**:
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**:
   ```bash
   gunicorn scripts.instructor.evaluation_api:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000
   ```

3. **Create systemd service** (`/etc/systemd/system/evaluation-api.service`):
   ```ini
   [Unit]
   Description=LLM Deployment Evaluation API
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/llm-deployment
   Environment="PATH=/var/www/llm-deployment/venv/bin"
   ExecStart=/var/www/llm-deployment/venv/bin/gunicorn \
     scripts.instructor.evaluation_api:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service**:
   ```bash
   sudo systemctl start evaluation-api
   sudo systemctl enable evaluation-api
   ```

#### Nginx Reverse Proxy

1. **Install Nginx**:
   ```bash
   sudo apt-get install nginx
   ```

2. **Configure** (`/etc/nginx/sites-available/evaluation-api`):
   ```nginx
   server {
       listen 80;
       server_name evaluation.yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

3. **Enable and restart**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/evaluation-api /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

#### SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d evaluation.yourdomain.com
```

#### Scheduled Tasks (Cron)

1. **Edit crontab**:
   ```bash
   crontab -e
   ```

2. **Add jobs**:
   ```cron
   # Send Round 1 tasks every Monday at 9 AM
   0 9 * * 1 cd /var/www/llm-deployment && /usr/bin/python3 scripts/instructor/round1.py

   # Run evaluations every hour
   0 * * * * cd /var/www/llm-deployment && /usr/bin/python3 scripts/instructor/evaluate.py

   # Export results daily at midnight
   0 0 * * * cd /var/www/llm-deployment && /usr/bin/python3 scripts/instructor/export_results.py
   ```

## Docker Deployment

### Student API Dockerfile

Create `Dockerfile.student`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY src/ ./src/
COPY .env ./

EXPOSE 3000

CMD ["node", "src/student/server.js"]
```

Build and run:
```bash
docker build -f Dockerfile.student -t llm-student-api .
docker run -p 3000:3000 --env-file .env llm-student-api
```

### Instructor System Dockerfile

Create `Dockerfile.instructor`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

COPY scripts/ ./scripts/
COPY config/ ./config/
COPY .env ./

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "scripts.instructor.evaluation_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: llm_deployment
      POSTGRES_USER: instructor
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  student-api:
    build:
      context: .
      dockerfile: Dockerfile.student
    ports:
      - "3000:3000"
    env_file:
      - .env
    depends_on:
      - postgres

  evaluation-api:
    build:
      context: .
      dockerfile: Dockerfile.instructor
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://instructor:secure_password@postgres:5432/llm_deployment

volumes:
  postgres_data:
```

Run:
```bash
docker-compose up -d
```

## Monitoring and Logging

### Application Logging

Add structured logging to `src/student/server.js`:
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

### Health Monitoring

Use tools like:
- **UptimeRobot**: Monitor endpoint availability
- **DataDog**: Application performance monitoring
- **Sentry**: Error tracking

### Database Backups

```bash
# Backup
pg_dump llm_deployment > backup_$(date +%Y%m%d).sql

# Restore
psql llm_deployment < backup_20251016.sql
```

Automated daily backups:
```cron
0 2 * * * pg_dump llm_deployment > /backups/llm_$(date +\%Y\%m\%d).sql
```

## Security Hardening

### Environment Variables

Never commit:
- API keys
- Database passwords
- GitHub tokens
- Secrets

Use secret management:
- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Azure Key Vault**

### API Rate Limiting

Add to `src/student/server.js`:
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', limiter);
```

### Input Sanitization

```javascript
const validator = require('validator');

function sanitizeInput(input) {
  return validator.escape(input);
}
```

### HTTPS Only

In production, always use HTTPS:
- Use Let's Encrypt for free certificates
- Configure SSL in Nginx
- Redirect HTTP to HTTPS

### Database Security

- Use prepared statements (SQLAlchemy does this)
- Limit database user permissions
- Enable SSL connections
- Regular security updates

## Performance Optimization

### Caching

Add Redis caching for LLM responses:
```javascript
const redis = require('redis');
const client = redis.createClient();

async function getCachedResponse(prompt) {
  const cached = await client.get(prompt);
  if (cached) return JSON.parse(cached);
  
  const response = await callLLM(prompt);
  await client.setex(prompt, 3600, JSON.stringify(response));
  return response;
}
```

### Database Indexing

```sql
CREATE INDEX idx_repos_email ON repos(email);
CREATE INDEX idx_repos_task ON repos(task);
CREATE INDEX idx_results_email ON results(email);
CREATE INDEX idx_tasks_round ON tasks(round);
```

### CDN for Static Assets

Use CloudFront, Cloudflare, or similar for:
- Faster global access
- DDoS protection
- SSL termination

## Scaling

### Horizontal Scaling

- Run multiple API instances behind load balancer
- Use Redis for session sharing
- Database connection pooling

### Load Balancing

With Nginx:
```nginx
upstream api_backend {
    server api1.internal:3000;
    server api2.internal:3000;
    server api3.internal:3000;
}

server {
    location /api/ {
        proxy_pass http://api_backend;
    }
}
```

### Queue System

For long-running evaluations, use a job queue:
- **Celery** (Python)
- **Bull** (Node.js)
- **RabbitMQ**
- **AWS SQS**

## Troubleshooting Production Issues

### High Memory Usage

Monitor with:
```bash
# Node.js
node --max-old-space-size=4096 src/student/server.js

# Python
python -m memory_profiler scripts/instructor/evaluate.py
```

### Slow Database Queries

```sql
-- Enable query logging
ALTER DATABASE llm_deployment SET log_statement = 'all';

-- Find slow queries
SELECT query, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

### API Timeouts

Increase timeouts:
```javascript
// Express
server.timeout = 120000; // 2 minutes

// Axios
axios.defaults.timeout = 60000;
```

## Maintenance

### Database Cleanup

```sql
-- Remove old results (older than 6 months)
DELETE FROM results WHERE timestamp < NOW() - INTERVAL '6 months';

-- Vacuum database
VACUUM ANALYZE;
```

### Log Rotation

Configure logrotate (`/etc/logrotate.d/llm-deployment`):
```
/var/log/llm-deployment/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

## Disaster Recovery

### Backup Strategy

1. **Database**: Daily automated backups
2. **Code**: Version controlled in Git
3. **Configuration**: Stored securely
4. **Secrets**: Documented recovery process

### Recovery Procedure

1. Provision new server
2. Install dependencies
3. Restore database from backup
4. Deploy latest code
5. Configure environment variables
6. Start services
7. Verify functionality

## Support and Monitoring

### Health Check Endpoints

```javascript
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date(),
    uptime: process.uptime(),
    memory: process.memoryUsage()
  });
});
```

### Alerting

Set up alerts for:
- API downtime
- High error rates
- Database connection issues
- Disk space warnings
- Memory/CPU thresholds

Use services like:
- **PagerDuty**
- **OpsGenie**
- **AWS CloudWatch Alarms**
