import json
import hashlib
import random
import base64
from datetime import datetime
from typing import Dict, List, Any


class TaskGenerator:
    """Generate tasks from templates with parametrization"""
    
    def __init__(self, templates_path: str):
        with open(templates_path, 'r') as f:
            self.templates = json.load(f)
    
    def generate_task(self, template_id: str, email: str, round_num: int = 1) -> Dict[str, Any]:
        """Generate a task from template with seed-based randomization"""
        
        template = self._get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Generate seed from email and current hour
        seed = self._generate_seed(email)
        
        # Get round-specific brief and checks
        if round_num == 1:
            brief = template['brief']
            checks = template['checks']
            attachments = template.get('attachments', [])
        else:
            # For round 2, pick a random variant
            if 'round2' not in template or not template['round2']:
                raise ValueError(f"Template {template_id} has no round 2 variants")
            
            variant = random.choice(template['round2'])
            brief = variant['brief']
            checks = variant['checks']
            attachments = variant.get('attachments', template.get('attachments', []))
        
        # Parametrize brief and checks
        brief = self._parametrize_string(brief, seed, template_id)
        checks = [self._parametrize_string(check, seed, template_id) for check in checks]
        
        # Generate attachments with seed
        processed_attachments = []
        for att in attachments:
            processed_attachments.append({
                'name': att['name'],
                'url': self._parametrize_string(att['url'], seed, template_id)
            })
        
        # Generate task ID
        task_id = self._generate_task_id(template_id, brief, attachments)
        
        return {
            'task_id': task_id,
            'brief': brief,
            'checks': checks,
            'attachments': processed_attachments,
            'template_id': template_id,
            'seed': seed
        }
    
    def _get_template(self, template_id: str) -> Dict:
        """Get template by ID"""
        for template in self.templates:
            if template['id'] == template_id:
                return template
        return None
    
    def _generate_seed(self, email: str) -> str:
        """Generate seed from email and current date-hour"""
        now = datetime.utcnow()
        date_hour = now.strftime('%Y-%m-%d-%H')
        seed_str = f"{email}-{date_hour}"
        return hashlib.sha256(seed_str.encode()).hexdigest()[:8]
    
    def _generate_task_id(self, template_id: str, brief: str, attachments: List) -> str:
        """Generate unique task ID"""
        content = f"{brief}{json.dumps(attachments)}"
        hash_part = hashlib.sha256(content.encode()).hexdigest()[:5]
        return f"{template_id}-{hash_part}"
    
    def _parametrize_string(self, text: str, seed: str, template_id: str) -> str:
        """Replace ${seed} and ${result} in strings"""
        text = text.replace('${seed}', seed)
        
        # Generate result based on template
        if template_id == 'sum-of-sales':
            result = self._generate_sales_data(seed)
            text = text.replace('${result}', str(result['total']))
        elif template_id == 'github-user-created':
            text = text.replace('${seed}', seed)
        
        return text
    
    def _generate_sales_data(self, seed: str) -> Dict:
        """Generate sales data CSV"""
        random.seed(seed)
        
        products = ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard', 
                   'Mouse', 'Headphones', 'Webcam', 'Speakers', 'Printer']
        
        data = []
        total = 0
        
        for product in products:
            sales = round(random.uniform(50, 1500), 2)
            data.append({'product': product, 'sales': sales})
            total += sales
        
        # Generate CSV
        csv_lines = ['product,sales']
        csv_lines.extend([f"{row['product']},{row['sales']}" for row in data])
        csv_content = '\n'.join(csv_lines)
        
        return {
            'csv': csv_content,
            'total': round(total, 2)
        }
    
    def _generate_markdown_content(self, seed: str) -> str:
        """Generate markdown content"""
        random.seed(seed)
        
        sections = [
            f"# Document {seed}\n\n",
            "## Introduction\n\nThis is a sample markdown document.\n\n",
            "## Code Example\n\n```python\nprint('Hello, World!')\n```\n\n",
            f"## Data Section\n\nSeed: {seed}\n\n"
        ]
        
        return ''.join(sections)
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template IDs"""
        return [t['id'] for t in self.templates]


def encode_to_data_uri(content: str, mime_type: str) -> str:
    """Encode content to data URI"""
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    return f"data:{mime_type};base64,{encoded}"
