#!/usr/bin/env python3
"""
Dynamic checks: Use Playwright to test deployed pages
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from typing import Dict, Tuple, List
import json


def run_dynamic_checks(pages_url: str, checks: List[str], timeout: int = 30000) -> List[Dict]:
    """
    Run JavaScript-based checks on deployed page using Playwright
    
    Args:
        pages_url: URL of the deployed GitHub Pages site
        checks: List of JavaScript expressions to evaluate
        timeout: Timeout in milliseconds
    
    Returns:
        List of check results with score, reason, and logs
    """
    results = []
    
    with sync_playwright() as p:
        try:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Set timeout
            page.set_default_timeout(timeout)
            
            # Navigate to page
            print(f"  → Loading {pages_url}")
            response = page.goto(pages_url)
            
            if not response or response.status != 200:
                return [{
                    'check': 'page_load',
                    'score': 0.0,
                    'reason': f'Page failed to load (HTTP {response.status if response else "N/A"})',
                    'logs': ''
                }]
            
            # Wait for page to be ready
            page.wait_for_load_state('networkidle', timeout=timeout)
            
            print(f"  ✓ Page loaded successfully")
            
            # Run each check
            for i, check in enumerate(checks, 1):
                print(f"  → Running check {i}/{len(checks)}")
                result = run_single_check(page, check, i)
                results.append(result)
            
            browser.close()
            
        except PlaywrightTimeout as e:
            results.append({
                'check': 'page_timeout',
                'score': 0.0,
                'reason': f'Page timeout: {str(e)}',
                'logs': str(e)
            })
        except Exception as e:
            results.append({
                'check': 'browser_error',
                'score': 0.0,
                'reason': f'Browser error: {str(e)}',
                'logs': str(e)
            })
    
    return results


def run_single_check(page, check_expr: str, check_num: int) -> Dict:
    """
    Run a single JavaScript check
    
    Args:
        page: Playwright page object
        check_expr: JavaScript expression to evaluate
        check_num: Check number for identification
    
    Returns:
        Dict with check results
    """
    try:
        # Evaluate the JavaScript expression
        result = page.evaluate(check_expr)
        
        # Check if result is truthy
        if result is True or (isinstance(result, bool) and result):
            return {
                'check': f'check_{check_num}',
                'score': 1.0,
                'reason': 'Check passed',
                'logs': f'Expression: {check_expr[:100]}'
            }
        else:
            return {
                'check': f'check_{check_num}',
                'score': 0.0,
                'reason': f'Check failed (returned: {result})',
                'logs': f'Expression: {check_expr[:100]}\nResult: {result}'
            }
            
    except Exception as e:
        return {
            'check': f'check_{check_num}',
            'score': 0.0,
            'reason': f'Check error: {str(e)}',
            'logs': f'Expression: {check_expr[:100]}\nError: {str(e)}'
        }


def check_page_accessibility(page) -> Dict:
    """Run basic accessibility checks"""
    try:
        # Check for page title
        title = page.title()
        
        # Check for ARIA landmarks
        landmarks = page.query_selector_all('[role="main"], [role="navigation"], [role="banner"]')
        
        # Check for alt text on images
        images = page.query_selector_all('img')
        images_without_alt = [img for img in images if not img.get_attribute('alt')]
        
        score = 1.0
        issues = []
        
        if not title or len(title) < 3:
            score -= 0.2
            issues.append("Missing or invalid page title")
        
        if len(landmarks) == 0:
            score -= 0.2
            issues.append("No ARIA landmarks found")
        
        if len(images_without_alt) > 0:
            score -= 0.2
            issues.append(f"{len(images_without_alt)} images missing alt text")
        
        return {
            'check': 'accessibility',
            'score': max(score, 0.0),
            'reason': '; '.join(issues) if issues else 'Basic accessibility checks passed',
            'logs': f'Title: {title}, Landmarks: {len(landmarks)}, Images: {len(images)}'
        }
        
    except Exception as e:
        return {
            'check': 'accessibility',
            'score': 0.5,
            'reason': f'Error checking accessibility: {str(e)}',
            'logs': str(e)
        }


def check_page_performance(page) -> Dict:
    """Check basic performance metrics"""
    try:
        # Get performance timing
        metrics = page.evaluate('''() => {
            const timing = performance.timing;
            return {
                loadTime: timing.loadEventEnd - timing.navigationStart,
                domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                resourcesLoaded: timing.loadEventEnd - timing.domContentLoadedEventEnd
            };
        }''')
        
        load_time = metrics['loadTime']
        
        if load_time < 3000:
            score = 1.0
            reason = f"Fast load time ({load_time}ms)"
        elif load_time < 5000:
            score = 0.8
            reason = f"Acceptable load time ({load_time}ms)"
        else:
            score = 0.5
            reason = f"Slow load time ({load_time}ms)"
        
        return {
            'check': 'performance',
            'score': score,
            'reason': reason,
            'logs': json.dumps(metrics)
        }
        
    except Exception as e:
        return {
            'check': 'performance',
            'score': 0.5,
            'reason': f'Error checking performance: {str(e)}',
            'logs': str(e)
        }


def take_screenshot(page, output_path: str) -> bool:
    """Take screenshot of the page"""
    try:
        page.screenshot(path=output_path)
        return True
    except Exception as e:
        print(f"  ✗ Screenshot failed: {e}")
        return False
