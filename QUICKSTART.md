# Quick Start Guide

## For Students

### 1. Setup

```powershell
# Clone or download the project
cd "TDS-1 Project"

# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium

# Copy environment template
copy .env.example .env

# Edit .env with your credentials
notepad .env
```

### 2. Configure .env

Edit `.env` and set:
```
STUDENT_EMAIL=your-email@example.com
STUDENT_SECRET=your-secret-key
GITHUB_TOKEN=ghp_your_github_token
GITHUB_USERNAME=your-github-username
OPENAI_API_KEY=sk-your-openai-key
```

### 3. Run Student API

```powershell
npm start
```

The API will run on `http://localhost:3000/api/submit`

### 4. Test with Sample Request

```powershell
curl http://localhost:3000/api/submit -H "Content-Type: application/json" -d "@sample_request.json"
```

## For Instructors

### 1. Initialize Database

```powershell
python scripts/instructor/init_db.py
```

### 2. Prepare Submissions

Create `submissions.csv`:
```csv
timestamp,email,endpoint,secret
2025-10-16T10:00:00Z,student@example.com,https://student-api.com/api/submit,secret123
```

### 3. Send Round 1 Tasks

```powershell
npm run instructor:round1
```

### 4. Start Evaluation API

```powershell
npm run instructor:api
```

### 5. Evaluate Submissions

```powershell
npm run instructor:evaluate
```

### 6. Send Round 2 Tasks

```powershell
npm run instructor:round2
```

## Common Issues

### GitHub Token Permissions

Your GitHub token needs:
- `repo` (Full control of private repositories)
- `workflow` (Update GitHub Action workflows)

### OpenAI Rate Limits

If you hit rate limits, consider:
- Using gpt-3.5-turbo instead of gpt-4
- Adding delays between requests
- Increasing `max_tokens` budget

### Playwright Issues

If Playwright fails:
```powershell
python -m playwright install --with-deps chromium
```

## Testing

Test the student API locally:

1. Start the API: `npm start`
2. Send a test request: Use `sample_request.json`
3. Check logs for errors
4. Verify repo is created on GitHub
5. Verify GitHub Pages is live

## Architecture

```
Student receives task → LLM generates code → GitHub repo created → 
Pages deployed → Submission sent → Instructor evaluates → 
Round 2 task sent → Student updates → Re-evaluated
```

## Support

- Check logs for detailed error messages
- Ensure all API keys are valid
- Verify network connectivity
- Check GitHub rate limits
