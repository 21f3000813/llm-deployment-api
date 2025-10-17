const axios = require('axios');

/**
 * Submit repo details to evaluation URL with exponential backoff retry
 */
async function submitWithRetry(evaluationUrl, submissionData, maxRetries = 5) {
  const delays = [1000, 2000, 4000, 8000, 16000]; // 1, 2, 4, 8, 16 seconds
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`Submission attempt ${attempt}/${maxRetries}...`);
      
      const response = await axios.post(evaluationUrl, submissionData, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000, // 30 second timeout
        validateStatus: (status) => status === 200
      });
      
      if (response.status === 200) {
        console.log(`✓ Submission successful (HTTP ${response.status})`);
        return response.data;
      }
      
    } catch (error) {
      const statusCode = error.response?.status;
      const errorMessage = error.response?.data?.error || error.message;
      
      console.error(`✗ Attempt ${attempt} failed:`, {
        status: statusCode,
        message: errorMessage
      });
      
      // If it's a client error (4xx), don't retry
      if (statusCode >= 400 && statusCode < 500) {
        throw new Error(`Client error (${statusCode}): ${errorMessage}`);
      }
      
      // If we have more attempts, wait before retrying
      if (attempt < maxRetries) {
        const delay = delays[attempt - 1] || delays[delays.length - 1];
        console.log(`Waiting ${delay}ms before retry...`);
        await sleep(delay);
      } else {
        throw new Error(`Failed after ${maxRetries} attempts: ${errorMessage}`);
      }
    }
  }
  
  throw new Error('Maximum retry attempts reached');
}

/**
 * Check if submission was within time limit
 */
function checkTimeLimit(requestTime, limitMinutes = 10) {
  const now = Date.now();
  const elapsed = (now - requestTime) / 1000 / 60; // minutes
  
  if (elapsed > limitMinutes) {
    console.warn(`⚠ Submission took ${elapsed.toFixed(2)} minutes (limit: ${limitMinutes})`);
    return false;
  }
  
  console.log(`✓ Submission within time limit (${elapsed.toFixed(2)}/${limitMinutes} minutes)`);
  return true;
}

/**
 * Validate submission data before sending
 */
function validateSubmissionData(data) {
  const required = ['email', 'task', 'round', 'nonce', 'repo_url', 'commit_sha', 'pages_url'];
  
  for (const field of required) {
    if (!data[field]) {
      throw new Error(`Missing required submission field: ${field}`);
    }
  }
  
  // Validate URLs
  try {
    new URL(data.repo_url);
    new URL(data.pages_url);
  } catch (e) {
    throw new Error('Invalid URL format in submission data');
  }
  
  // Validate commit SHA format (40 hex characters)
  if (!/^[a-f0-9]{40}$/i.test(data.commit_sha)) {
    throw new Error('Invalid commit SHA format');
  }
  
  return true;
}

/**
 * Sleep utility
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = {
  submitWithRetry,
  checkTimeLimit,
  validateSubmissionData
};
