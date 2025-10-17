const express = require('express');
const requestHandler = require('./request_handler');
const llmGenerator = require('./llm_generator');
const githubManager = require('./github_manager');
const evaluationNotifier = require('./evaluation_notifier');
require('dotenv').config();

const app = express();
const PORT = process.env.STUDENT_API_PORT || 3000;

// Middleware
app.use(express.json({ limit: '50mb' })); // Support large attachments

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Main API endpoint for receiving task requests
app.post('/api/submit', async (req, res) => {
  console.log(`[${new Date().toISOString()}] Received request`);
  
  try {
    // Step 1: Validate request and secret
    const validation = requestHandler.validateRequest(req.body);
    if (!validation.valid) {
      console.error('Validation failed:', validation.error);
      return res.status(400).json({ error: validation.error });
    }

    const taskRequest = req.body;
    
    // Step 2: Send immediate 200 response as required
    res.status(200).json({ 
      message: 'Request received and processing',
      task: taskRequest.task,
      round: taskRequest.round 
    });

    // Step 3: Process asynchronously (don't block response)
    processTask(taskRequest).catch(error => {
      console.error('Error processing task:', error);
    });

  } catch (error) {
    console.error('Server error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

async function processTask(taskRequest) {
  const startTime = Date.now();
  console.log(`\n=== Processing Task: ${taskRequest.task} (Round ${taskRequest.round}) ===`);
  
  try {
    // Step 1: Generate app code using LLM
    console.log('Step 1: Generating code with LLM...');
    const generatedCode = await llmGenerator.generateApp(taskRequest);
    console.log('✓ Code generation complete');

    // Step 2: Create GitHub repo and push code
    console.log('Step 2: Creating GitHub repository...');
    const repoDetails = await githubManager.createAndDeploy({
      taskId: taskRequest.task,
      round: taskRequest.round,
      code: generatedCode,
      email: taskRequest.email
    });
    console.log(`✓ Repository created: ${repoDetails.repo_url}`);
    console.log(`✓ GitHub Pages URL: ${repoDetails.pages_url}`);

    // Step 3: Submit to evaluation URL
    console.log('Step 3: Submitting to evaluation API...');
    const submissionData = {
      email: taskRequest.email,
      task: taskRequest.task,
      round: taskRequest.round,
      nonce: taskRequest.nonce,
      repo_url: repoDetails.repo_url,
      commit_sha: repoDetails.commit_sha,
      pages_url: repoDetails.pages_url
    };

    await evaluationNotifier.submitWithRetry(
      taskRequest.evaluation_url,
      submissionData
    );
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`✓ Submission successful`);
    console.log(`=== Task completed in ${elapsedTime}s ===\n`);

  } catch (error) {
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    console.error(`✗ Task failed after ${elapsedTime}s:`, error.message);
    console.error(error.stack);
  }
}

// Start server
app.listen(PORT, () => {
  console.log(`\n🚀 Student API Server running on port ${PORT}`);
  console.log(`   Endpoint: http://localhost:${PORT}/api/submit`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`   Email: ${process.env.STUDENT_EMAIL}`);
  console.log(`\nWaiting for task requests...\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down gracefully...');
  process.exit(0);
});
