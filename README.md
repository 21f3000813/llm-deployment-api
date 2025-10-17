# LLM Code Deployment System

An automated system for building, deploying, and evaluating student-submitted web applications using LLMs and GitHub Pages.

## Overview

This project implements a complete workflow for:
- **Students**: Receiving app specifications, generating code with LLMs, deploying to GitHub Pages
- **Instructors**: Sending automated tasks, evaluating submissions with static/dynamic checks, and publishing results

## Architecture

### Student System (`src/student/`)
- **API Endpoint**: Receives task requests via POST
- **LLM Generator**: Uses OpenAI/Anthropic to generate app code
- **GitHub Integration**: Creates repos, pushes code, enables Pages
- **Evaluation Notifier**: Submits repo details with retry logic

### Instructor System (`scripts/instructor/`)
- **round1.py**: Sends initial task requests to students
- **round2.py**: Sends revision tasks based on Round 1 submissions
- **evaluate.py**: Runs static, dynamic, and LLM-based checks
- **evaluation_api.py**: Accepts and queues student submissions

### Database Schema
- **tasks**: Tracks sent requests (email, task, round, nonce, brief, checks)
- **repos**: Stores submitted repo details (repo_url, commit_sha, pages_url)
- **results**: Evaluation outcomes (check, score, reason, logs)

## Setup

### Prerequisites
- Node.js 18+ and Python 3.9+
- PostgreSQL database
- GitHub account with Personal Access Token
- OpenAI or Anthropic API key

### Installation

1. **Clone and install dependencies**:
```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Initialize database**:
```bash
python scripts/instructor/init_db.py
```

## Usage

### For Students

1. **Start the student API**:
```bash
npm start
# API runs on http://localhost:3000/api/submit
```

2. **Test with a sample request**:
```bash
curl http://localhost:3000/api/submit \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

The system will:
- Verify the secret
- Generate app code using LLM
- Create a GitHub repo
- Deploy to GitHub Pages
- Notify the evaluation URL

### For Instructors

1. **Prepare submissions.csv**:
```csv
timestamp,email,endpoint,secret
2025-10-16T10:00:00Z,student@example.com,https://example.com/api,secret123
```

2. **Send Round 1 tasks**:
```bash
npm run instructor:round1
```

3. **Start evaluation API** (receives submissions):
```bash
npm run instructor:api
# API runs on http://localhost:8000
```

4. **Evaluate submissions**:
```bash
npm run instructor:evaluate
```

5. **Send Round 2 tasks** (after evaluation):
```bash
npm run instructor:round2
```

## Task Templates

Located in `config/task_templates.json`, includes:
- **sum-of-sales**: CSV data aggregation
- **markdown-to-html**: Markdown rendering with syntax highlighting
- **github-user-created**: GitHub API integration

Each template includes:
- Brief description with seed variables
- Attachments (base64-encoded)
- JavaScript-based checks
- Round 2 variants

## Evaluation Checks

### Static Checks
- LICENSE file validation (MIT)
- README.md quality assessment
- Code quality analysis
- Security scan (no secrets in git history)

### Dynamic Checks (Playwright)
- Page loads successfully (HTTP 200)
- Required DOM elements exist
- JavaScript functionality works
- Data displays correctly

### LLM Checks
- Documentation completeness
- Code structure and patterns
- Best practices adherence

## API Endpoints

### Student API
- `POST /api/submit` - Receives task requests

**Request**:
```json
{
  "email": "student@example.com",
  "secret": "...",
  "task": "sum-of-sales-a1b2c",
  "round": 1,
  "nonce": "uuid-here",
  "brief": "Create a sales summary app...",
  "checks": ["...", "..."],
  "evaluation_url": "https://instructor.com/notify",
  "attachments": [{"name": "data.csv", "url": "data:..."}]
}
```

**Response**: `200 OK`

### Evaluation API
- `POST /api/notify` - Receives student submissions

**Request**:
```json
{
  "email": "student@example.com",
  "task": "sum-of-sales-a1b2c",
  "round": 1,
  "nonce": "uuid-here",
  "repo_url": "https://github.com/user/repo",
  "commit_sha": "abc123",
  "pages_url": "https://user.github.io/repo/"
}
```

**Response**: `200 OK` or `400 Bad Request`

## Configuration

### LLM Provider
Edit `src/student/llm_generator.js` to switch between OpenAI and Anthropic:
```javascript
const provider = 'openai'; // or 'anthropic'
```

### Task Templates
Edit `config/task_templates.json` to add custom tasks with:
- Unique IDs
- Brief descriptions
- Attachments
- Validation checks
- Round 2 variations

### Retry Logic
Configure in `.env`:
```
MAX_RETRIES=5
RETRY_DELAYS=1,2,4,8,16
```

## Project Structure

```
llm-code-deployment/
├── src/
│   └── student/
│       ├── server.js              # Express API server
│       ├── request_handler.js     # Validates requests
│       ├── llm_generator.js       # Generates code with LLM
│       ├── github_manager.js      # GitHub repo operations
│       └── evaluation_notifier.js # Submits to evaluation API
├── scripts/
│   └── instructor/
│       ├── init_db.py            # Database initialization
│       ├── round1.py             # Send Round 1 tasks
│       ├── round2.py             # Send Round 2 tasks
│       ├── evaluate.py           # Run all checks
│       ├── evaluation_api.py     # FastAPI submission endpoint
│       ├── db_models.py          # SQLAlchemy models
│       ├── task_generator.py     # Generate tasks from templates
│       ├── static_checks.py      # LICENSE, README, code checks
│       ├── dynamic_checks.py     # Playwright tests
│       └── llm_checks.py         # LLM-based evaluation
├── config/
│   └── task_templates.json       # Task definitions
├── tests/
│   ├── student/                  # Student system tests
│   └── instructor/               # Instructor system tests
├── package.json
├── requirements.txt
├── .env.example
└── README.md
```

## Security Considerations

- Never commit `.env` file or secrets
- Use GitHub tokens with minimal required permissions
- Validate all incoming requests
- Sanitize LLM-generated code before deployment
- Use trufflehog/gitleaks to scan for leaked secrets

## Troubleshooting

### GitHub Pages not deploying
- Ensure repo is public
- Check GitHub Pages settings in repo
- Verify branch and folder configuration

### LLM generation fails
- Check API key validity
- Monitor rate limits
- Verify prompt structure

### Evaluation API not receiving submissions
- Confirm endpoint URL is reachable
- Check firewall/network settings
- Verify JSON payload format

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open a GitHub issue.
