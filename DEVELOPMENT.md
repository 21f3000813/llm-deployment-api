# Development Guide

## Project Structure

```
llm-code-deployment/
├── src/student/              # Student system (Node.js)
│   ├── server.js            # Express API server
│   ├── request_handler.js   # Request validation
│   ├── llm_generator.js     # LLM code generation
│   ├── github_manager.js    # GitHub operations
│   └── evaluation_notifier.js # Submit to evaluation
│
├── scripts/instructor/       # Instructor system (Python)
│   ├── db_models.py         # SQLAlchemy database models
│   ├── init_db.py           # Database initialization
│   ├── task_generator.py    # Generate tasks from templates
│   ├── round1.py            # Send Round 1 tasks
│   ├── round2.py            # Send Round 2 tasks
│   ├── evaluation_api.py    # FastAPI submission endpoint
│   ├── evaluate.py          # Run all evaluations
│   ├── static_checks.py     # LICENSE, README checks
│   ├── dynamic_checks.py    # Playwright testing
│   ├── llm_checks.py        # LLM-based evaluation
│   ├── export_results.py    # Export to CSV
│   └── view_stats.py        # View statistics
│
├── config/
│   └── task_templates.json  # Task definitions
│
└── tests/                    # Unit tests
    ├── student/
    └── instructor/
```

## Development Workflow

### Adding a New Task Template

1. Edit `config/task_templates.json`
2. Add new template with:
   - Unique `id`
   - `brief` with `${seed}` placeholders
   - `checks` array with JavaScript expressions
   - `attachments` with data URIs
   - `round2` variants

Example:
```json
{
  "id": "my-new-task",
  "brief": "Create an app that does X with seed ${seed}",
  "checks": [
    "document.querySelector('#result').textContent.length > 0"
  ],
  "attachments": [],
  "round2": [...]
}
```

### Modifying LLM Prompts

Edit `src/student/llm_generator.js`:
- `buildPrompt()` - Constructs the LLM prompt
- Add context, examples, or constraints
- Adjust temperature and max_tokens

### Adding New Checks

**Static Checks** (`scripts/instructor/static_checks.py`):
```python
def check_my_feature(repo_url, commit_sha):
    # Your check logic
    return (score, reason, logs)
```

**Dynamic Checks** (`scripts/instructor/dynamic_checks.py`):
```python
def check_my_feature(page):
    # Playwright page interaction
    return {'check': 'name', 'score': 0.8, 'reason': '...', 'logs': '...'}
```

**LLM Checks** (`scripts/instructor/llm_checks.py`):
```python
def evaluate_my_feature(content):
    # LLM evaluation
    return (score, reason, logs)
```

### Database Schema Changes

1. Modify models in `scripts/instructor/db_models.py`
2. For development, drop and recreate:
   ```bash
   rm llm_deployment.db
   python scripts/instructor/init_db.py
   ```
3. For production, use migrations (Alembic)

## Testing

### Unit Tests

```bash
# Node.js tests
npm test

# Python tests
python -m pytest tests/
```

### Integration Testing

1. Start student API:
   ```bash
   npm start
   ```

2. Send test request:
   ```bash
   curl http://localhost:3000/api/submit \
     -H "Content-Type: application/json" \
     -d @sample_request.json
   ```

3. Check logs and verify:
   - GitHub repo created
   - Pages deployed
   - Submission sent

### Testing Evaluation System

1. Initialize database:
   ```bash
   python scripts/instructor/init_db.py
   ```

2. Create test submissions.csv
3. Send tasks:
   ```bash
   python scripts/instructor/round1.py
   ```

4. Start evaluation API:
   ```bash
   python scripts/instructor/evaluation_api.py
   ```

5. Run evaluations:
   ```bash
   python scripts/instructor/evaluate.py
   ```

## Debugging

### Student API Issues

Enable debug logging in `src/student/server.js`:
```javascript
console.log('Debug:', JSON.stringify(data, null, 2));
```

### GitHub API Issues

Check rate limits:
```javascript
const { Octokit } = require('octokit');
const octokit = new Octokit({ auth: token });
const { data } = await octokit.rest.rateLimit.get();
console.log(data);
```

### LLM Generation Issues

Test prompts directly:
```javascript
const prompt = buildPrompt(taskRequest, attachments);
console.log(prompt);
// Copy prompt and test in ChatGPT/Claude
```

### Playwright Issues

Run with headed browser:
```python
browser = p.chromium.launch(headless=False)
```

Take screenshots:
```python
page.screenshot(path='debug.png')
```

## Code Style

### JavaScript (Node.js)
- Use ES6+ features
- Async/await over callbacks
- Descriptive variable names
- JSDoc comments for functions

### Python
- PEP 8 style guide
- Type hints where appropriate
- Docstrings for all functions
- Use f-strings for formatting

## Common Patterns

### Error Handling (JavaScript)
```javascript
try {
  const result = await operation();
  console.log('✓ Success');
} catch (error) {
  console.error('✗ Error:', error.message);
  throw new Error(`Operation failed: ${error.message}`);
}
```

### Error Handling (Python)
```python
try:
    result = operation()
    print("✓ Success")
except Exception as e:
    print(f"✗ Error: {e}")
    return (0.0, f"Error: {str(e)}", "")
```

### Retry Logic
```javascript
for (let attempt = 1; attempt <= maxRetries; attempt++) {
  try {
    const result = await operation();
    return result;
  } catch (error) {
    if (attempt < maxRetries) {
      await sleep(delays[attempt - 1]);
    } else {
      throw error;
    }
  }
}
```

## Performance Optimization

### Rate Limiting
- Add delays between API calls
- Use exponential backoff
- Cache responses where possible

### Database Queries
- Use indexes on frequently queried fields
- Batch insert operations
- Close sessions properly

### Playwright
- Reuse browser contexts
- Set appropriate timeouts
- Use `networkidle` judiciously

## Security Considerations

### Secrets Management
- Never commit .env files
- Use environment variables
- Rotate tokens regularly
- Minimum required permissions

### Input Validation
- Validate all user input
- Sanitize before LLM calls
- Check URL formats
- Verify data types

### Generated Code
- Scan for secrets before commit
- Review LLM output
- Set content security policies
- Sandbox execution if needed

## Deployment

### Student API Deployment

Options:
- **Heroku**: Simple Node.js deployment
- **Vercel**: Serverless functions
- **AWS Lambda**: With API Gateway
- **DigitalOcean**: App Platform

### Instructor System Deployment

- **Database**: PostgreSQL (production) vs SQLite (dev)
- **API**: Uvicorn with Gunicorn
- **Scheduler**: Cron jobs for periodic tasks
- **Monitoring**: Log aggregation and alerts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Update documentation
5. Submit pull request

## Resources

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Playwright Documentation](https://playwright.dev/python/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Express.js Documentation](https://expressjs.com/)
