import re
from datetime import datetime, timedelta
from config import OPENAI_API_KEY

def parse_text_request(text):
    if OPENAI_API_KEY:
        result = _parse_with_openai(text)
        if result:
            return result
    return _parse_with_regex(text)

def _parse_with_openai(text):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'system', 'content': 'Extract ride parameters as JSON: start_point, end_point, time (HH:MM), seats (int), flexibility (int minutes).'},
                {'role': 'user', 'content': text}],
            max_tokens=100, temperature=0)
        import json
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        return _normalize_result(result)
    except Exception:
        return None

def _parse_with_regex(text):
    result = {'start_point': '', 'end_point': '', 'time': '', 'seats': 1, 'flexibility': 15, 'raw': text}
    time_match = re.search(r'(\d{1,2}:\d{2})', text)
    if time_match:
        result['time'] = time_match.group(1)
    seats_match = re.search(r'(\d+)\s*(?:мест|человек|пассажир)', text, re.IGNORECASE)
    if seats_match:
        result['seats'] = int(seats_match.group(1))
    take_match = re.search(r'могу\s+взять\s+(\d+)', text, re.IGNORECASE)
    if take_match:
        result['seats'] = int(take_match.group(1))
    route_match = re.search(r'от\s+([^.]+?)\s+(?:до|в|на)\s+([^.]+?)(?:\s*,|\s*$|\s+в\s+\d)', text, re.IGNORECASE)
    if route_match:
        result['start_point'] = route_match.group(1).strip().rstrip(',').strip()
        result['end_point'] = route_match.group(2).strip().rstrip(',').strip()
    return result

def _normalize_result(result):
    normalized = {'start_point': result.get('start_point', ''), 'end_point': result.get('end_point', ''),
        'time': result.get('time', ''), 'seats': int(result.get('seats', 1)),
        'flexibility': int(result.get('flexibility', 15)), 'raw': ''}
    if normalized['time']:
        try:
            h, m = map(int, normalized['time'].split(':'))
            now = datetime.now()
            target = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if target < now:
                target += timedelta(days=1)
            normalized['time'] = target.strftime('%Y-%m-%dT%H:%M')
        except (ValueError, TypeError):
            normalized['time'] = ''
    return normalized
