import os
import re

def adapt_event(data: dict) -> dict:
    t = data.get('type')
    content = data.get('content', '')
    result_data = data.get('data', '')
    stage_map = {
        'thought': 'plan',
        'thought_stream': 'plan',
        'execution': 'run',
        'error': 'run',
        'result': 'done'
    }
    progress_map = {
        'thought': 0.1,
        'thought_stream': 0.2,
        'execution': 0.5,
        'error': 0.6,
        'result': 1.0
    }
    attachments = []
    if t == 'result':
        paths = re.findall(r'([A-Za-z]:\\[^:\n]*\.(?:xlsx|csv|png)|workspace[\\/][^:\n]*\.(?:xlsx|csv|png))', result_data)
        for p in paths:
            ap = os.path.abspath(p.strip())
            if os.path.exists(ap) and ap not in attachments:
                attachments.append(ap)
    return {
        'type': t,
        'stage': stage_map.get(t, ''),
        'progress': progress_map.get(t, 0.0),
        'content': content if t != 'result' else result_data,
        'success': True if (t == 'result' and data.get('success')) else (False if t == 'result' else None),
        'attachments': attachments
    }
