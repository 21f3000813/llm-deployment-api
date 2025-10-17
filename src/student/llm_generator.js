const axios = require('axios');
const requestHandler = require('./request_handler');
require('dotenv').config();

/**
 * Generate app code using LLM based on task brief
 */
async function generateApp(taskRequest) {
  const provider = process.env.LLM_PROVIDER || 'openai';
  
  console.log(`Using LLM provider: ${provider}`);
  
  // Parse attachments
  const attachments = requestHandler.parseAttachments(taskRequest);
  
  // Build prompt
  const prompt = buildPrompt(taskRequest, attachments);
  
  // Call LLM
  let generatedCode;
  if (provider === 'openai') {
    generatedCode = await generateWithOpenAI(prompt);
  } else if (provider === 'anthropic') {
    generatedCode = await generateWithAnthropic(prompt);
  } else {
    throw new Error(`Unsupported LLM provider: ${provider}`);
  }
  
  // Parse and structure the generated code
  return structureGeneratedCode(generatedCode, attachments);
}

/**
 * Build comprehensive prompt for LLM
 */
function buildPrompt(taskRequest, attachments) {
  const attachmentInfo = attachments.map(att => 
    `File: ${att.name}\nContent:\n${att.content}\n`
  ).join('\n---\n');

  const checksInfo = taskRequest.checks.map((check, i) => 
    `${i + 1}. ${check}`
  ).join('\n');

  return `You are an expert web developer. Generate a complete, production-ready single-page web application based on the following requirements.

## Task Requirements
${taskRequest.brief}

## Validation Checks
The application will be tested with the following checks:
${checksInfo}

${attachments.length > 0 ? `## Provided Files\n${attachmentInfo}` : ''}

## Technical Requirements
- Create a single HTML file with embedded CSS and JavaScript
- Use modern ES6+ JavaScript
- Include Bootstrap 5 from CDN (https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css)
- Ensure all required DOM elements have the correct IDs as specified
- Handle errors gracefully with user-friendly messages
- Make the UI professional and responsive
- Add proper ARIA attributes for accessibility
- Include comments explaining key functionality
- Ensure code is production-ready and follows best practices

## Output Format
Provide ONLY the complete HTML file content. Start with <!DOCTYPE html> and include everything needed in a single file.

Generate the complete application now:`;
}

/**
 * Generate code using OpenAI API
 */
async function generateWithOpenAI(prompt) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY not configured');
  }

  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-4-turbo-preview',
        messages: [
          {
            role: 'system',
            content: 'You are an expert web developer who creates clean, efficient, production-ready code.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 4000
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data.choices[0].message.content;
  } catch (error) {
    console.error('OpenAI API error:', error.response?.data || error.message);
    throw new Error(`OpenAI generation failed: ${error.message}`);
  }
}

/**
 * Generate code using Anthropic API
 */
async function generateWithAnthropic(prompt) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY not configured');
  }

  try {
    const response = await axios.post(
      'https://api.anthropic.com/v1/messages',
      {
        model: 'claude-3-opus-20240229',
        max_tokens: 4000,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ]
      },
      {
        headers: {
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01',
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data.content[0].text;
  } catch (error) {
    console.error('Anthropic API error:', error.response?.data || error.message);
    throw new Error(`Anthropic generation failed: ${error.message}`);
  }
}

/**
 * Structure generated code into files
 */
function structureGeneratedCode(generatedCode, attachments) {
  // Extract HTML from markdown code blocks if present
  let htmlContent = generatedCode;
  const codeBlockMatch = generatedCode.match(/```html\n([\s\S]*?)\n```/);
  if (codeBlockMatch) {
    htmlContent = codeBlockMatch[1];
  } else {
    // Try without language specifier
    const genericBlockMatch = generatedCode.match(/```\n([\s\S]*?)\n```/);
    if (genericBlockMatch) {
      htmlContent = genericBlockMatch[1];
    }
  }

  // Ensure proper HTML structure
  if (!htmlContent.trim().startsWith('<!DOCTYPE') && !htmlContent.trim().startsWith('<html')) {
    htmlContent = `<!DOCTYPE html>\n${htmlContent}`;
  }

  const files = [
    {
      path: 'index.html',
      content: htmlContent
    }
  ];

  // Add LICENSE
  files.push({
    path: 'LICENSE',
    content: `MIT License

Copyright (c) ${new Date().getFullYear()}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.`
  });

  // Add attachment files to the repo
  for (const attachment of attachments) {
    files.push({
      path: attachment.name,
      content: attachment.content
    });
  }

  return files;
}

module.exports = {
  generateApp,
  buildPrompt,
  generateWithOpenAI,
  generateWithAnthropic
};
