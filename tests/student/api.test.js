const request = require('supertest');
const express = require('express');

describe('Student API Tests', () => {
  let app;

  beforeAll(() => {
    // Setup test app
    app = express();
    app.use(express.json());
  });

  test('Health check endpoint', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('status', 'ok');
  });

  test('Request validation - missing fields', () => {
    const requestHandler = require('../src/student/request_handler');
    
    const result = requestHandler.validateRequest({
      email: 'test@example.com'
      // Missing other required fields
    });
    
    expect(result.valid).toBe(false);
    expect(result.error).toContain('Missing required field');
  });

  test('Request validation - invalid email', () => {
    const requestHandler = require('../src/student/request_handler');
    
    const result = requestHandler.validateRequest({
      email: 'invalid-email',
      secret: 'test',
      task: 'test-task',
      round: 1,
      nonce: 'test-nonce',
      brief: 'Test brief',
      checks: ['check1'],
      evaluation_url: 'http://example.com'
    });
    
    expect(result.valid).toBe(false);
    expect(result.error).toContain('Invalid email format');
  });

  test('Parse attachment - valid data URI', () => {
    const requestHandler = require('../src/student/request_handler');
    
    const attachment = {
      name: 'test.txt',
      url: 'data:text/plain;base64,SGVsbG8gV29ybGQ='
    };
    
    const result = requestHandler.parseAttachment(attachment);
    
    expect(result.name).toBe('test.txt');
    expect(result.mimeType).toBe('text/plain');
    expect(result.content).toBe('Hello World');
  });
});
