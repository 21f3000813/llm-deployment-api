#!/usr/bin/env python3
"""
LLM-based checks: Code quality, README quality
"""

import os
import openai
from typing import Dict, Tuple
from dotenv import load_dotenv

load_dotenv()


def evaluate_readme_quality(readme_content: str) -> Tuple[float, str, str]:
    """Use LLM to evaluate README quality"""
    
    if not readme_content or len(readme_content) < 50:
        return (0.0, "README is too short or empty", "")
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return (0.5, "LLM evaluation skipped (no API key)", "")
        
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""Evaluate the quality of this README.md documentation for a student project. 

Rate it on a scale of 0.0 to 1.0 based on:
- Clarity and completeness
- Professional presentation
- Proper structure (overview, setup, usage, etc.)
- Code examples and explanations
- Grammar and formatting

README Content:
{readme_content[:3000]}

Respond ONLY with a JSON object in this format:
{{"score": 0.85, "reason": "Well-structured with clear examples but missing installation details"}}"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a technical documentation evaluator. Respond only with JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        import json
        result = json.loads(result_text)
        
        score = float(result.get('score', 0.5))
        reason = result.get('reason', 'LLM evaluation completed')
        
        return (score, reason, result_text)
        
    except Exception as e:
        print(f"  ⚠ LLM README evaluation error: {e}")
        return (0.5, f"LLM evaluation error: {str(e)}", "")


def evaluate_code_quality(code_content: str, language: str = 'javascript') -> Tuple[float, str, str]:
    """Use LLM to evaluate code quality"""
    
    if not code_content or len(code_content) < 50:
        return (0.0, "Code is too short or empty", "")
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return (0.5, "LLM evaluation skipped (no API key)", "")
        
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""Evaluate the quality of this {language} code for a student web application project.

Rate it on a scale of 0.0 to 1.0 based on:
- Code structure and organization
- Best practices and modern patterns
- Error handling
- Comments and documentation
- Security considerations
- Performance

Code Content:
{code_content[:4000]}

Respond ONLY with a JSON object in this format:
{{"score": 0.75, "reason": "Clean code with good structure but lacks error handling in fetch calls"}}"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a code quality evaluator. Respond only with JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        import json
        result = json.loads(result_text)
        
        score = float(result.get('score', 0.5))
        reason = result.get('reason', 'LLM evaluation completed')
        
        return (score, reason, result_text)
        
    except Exception as e:
        print(f"  ⚠ LLM code evaluation error: {e}")
        return (0.5, f"LLM evaluation error: {str(e)}", "")


def check_code_completeness(code_content: str, brief: str) -> Tuple[float, str, str]:
    """Check if code implements the requirements from the brief"""
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return (0.5, "LLM evaluation skipped (no API key)", "")
        
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""Does this code implementation meet the requirements specified in the brief?

Brief Requirements:
{brief}

Code Implementation:
{code_content[:3000]}

Respond ONLY with a JSON object in this format:
{{"score": 0.9, "reason": "Implements all core requirements but missing optional error messages"}}

Score should be 1.0 if all requirements are met, lower if missing features."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a requirements verification expert. Respond only with JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        import json
        result = json.loads(result_text)
        
        score = float(result.get('score', 0.5))
        reason = result.get('reason', 'Requirements check completed')
        
        return (score, reason, result_text)
        
    except Exception as e:
        print(f"  ⚠ LLM completeness check error: {e}")
        return (0.5, f"LLM evaluation error: {str(e)}", "")
