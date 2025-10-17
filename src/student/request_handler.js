require('dotenv').config();

/**
 * Validates incoming task request
 */
function validateRequest(body) {
  // Check required fields
  const requiredFields = ['email', 'secret', 'task', 'round', 'nonce', 'brief', 'checks', 'evaluation_url'];
  
  for (const field of requiredFields) {
    if (!body[field]) {
      return {
        valid: false,
        error: `Missing required field: ${field}`
      };
    }
  }

  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(body.email)) {
    return {
      valid: false,
      error: 'Invalid email format'
    };
  }

  // Validate secret
  const expectedSecret = process.env.STUDENT_SECRET;
  if (!expectedSecret) {
    return {
      valid: false,
      error: 'Server configuration error: STUDENT_SECRET not set'
    };
  }

  if (body.secret !== expectedSecret) {
    return {
      valid: false,
      error: 'Invalid secret'
    };
  }

  // Validate round
  if (![1, 2].includes(body.round)) {
    return {
      valid: false,
      error: 'Round must be 1 or 2'
    };
  }

  // Validate evaluation_url format
  try {
    new URL(body.evaluation_url);
  } catch (e) {
    return {
      valid: false,
      error: 'Invalid evaluation_url format'
    };
  }

  // Validate checks array
  if (!Array.isArray(body.checks) || body.checks.length === 0) {
    return {
      valid: false,
      error: 'Checks must be a non-empty array'
    };
  }

  // Validate attachments if present
  if (body.attachments) {
    if (!Array.isArray(body.attachments)) {
      return {
        valid: false,
        error: 'Attachments must be an array'
      };
    }

    for (const attachment of body.attachments) {
      if (!attachment.name || !attachment.url) {
        return {
          valid: false,
          error: 'Each attachment must have name and url'
        };
      }

      // Validate data URI format
      if (!attachment.url.startsWith('data:')) {
        return {
          valid: false,
          error: 'Attachment URL must be a data URI'
        };
      }
    }
  }

  return { valid: true };
}

/**
 * Parse data URI attachment
 */
function parseAttachment(attachment) {
  const match = attachment.url.match(/^data:([^;]+);base64,(.+)$/);
  if (!match) {
    throw new Error(`Invalid data URI format for ${attachment.name}`);
  }

  return {
    name: attachment.name,
    mimeType: match[1],
    content: Buffer.from(match[2], 'base64').toString('utf-8')
  };
}

/**
 * Parse all attachments in request
 */
function parseAttachments(taskRequest) {
  if (!taskRequest.attachments) {
    return [];
  }

  return taskRequest.attachments.map(parseAttachment);
}

module.exports = {
  validateRequest,
  parseAttachment,
  parseAttachments
};
