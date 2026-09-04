import re
from datetime import datetime, timedelta
from config import OPENAI_API_KEY


def parse_text_request(text):
    """
    Распознать параметры поездки из текстового запроса.
    Использует regex или OpenAI API.
    Возвращает dict с полями: start_point, end_point, time, seats, flexibility
    """
    # Try OpenAI first if key is available
    if OPENAI_API_KEY:
        result = _parse_with_openai(text)
        if result:
            return result

    # Fallback to regex
    return _parse_with_regex(text)


def _parse_with_openai(text):
    """Парсинг через OpenAI API."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant that extracts ride parameters from text. Return only JSON with fields: start_point, end_point, time (HH:MM), seats (integer), flexibility (integer minutes).'},
                {'role': 'user', 'content': text}
            ],
            max_tokens=100,
            temperature=0,
        )
        import json
        content = response.choices[0].message.content.strip()
        # Try to parse as JSON
        result = json.loads(content)
        return _normalize_result(result)
    except Exception:
        return None


def _parse_with_regex(text):
    """Парсинг через регулярные выражения."""
    result = {
        'start_point': '',
        'end_point': '',
        'time': '',
        'seats': 1,
        'flexibility': 15,
        'raw': text,
    }

    # Time: find HH:MM pattern
    time_match = re.search(r'(\d{1,2}:\d{2})', text)
    if time_match:
        result['time'] = time_match.group(1)

    # Seats: "N мест", "могу взять N", "N человек"
    seats_match = re.search(r'(\d+)\s*(?:мест|человек|пассажир)', text, re.IGNORECASE)
    if seats_match:
        result['seats'] = int(seats_match.group(1))
    # Also check "могу взять N"
    take_match = re.search(r'могу\s+взять\s+(\d+)', text, re.IGNORECASE)
    if take_match:
        result['seats'] = int(take_match.group(1))

    # Flexibility: "гибкость N", "±N", "плюс-минус N"
    flex_match = re.search(r'(?:гибкость|гибкость|±|\+?[-–]?)\s*[-–]?\s*(\d+)', text, re.IGNORECASE)
    if flex_match:
        result['flexibility'] = int(flex_match.group(1))

    # Points: after "от" and "до"/"в"/"на"
    # "от X до Y", "от X в Y", "от X на Y"
    route_match = re.search(r'от\s+([^.]+?)\s+(?:до|в|на)\s+([^.]+?)(?:\s*,|\s*$|\s+в\s+\d)', text, re.IGNORECASE)
    if route_match:
        result['start_point'] = route_match.group(1).strip().rstrip(',').strip()
        result['end_point'] = route_match.group(2).strip().rstrip(',').strip()
    else:
        # Try simpler: first "от X" and then "в/до/на Y"
        from_match = re.search(r'от\s+([^.]+?)(?:\s*,|\s*$|\s+до|\s+в|\s+на)', text, re.IGNORECASE)
        if from_match:
            result['start_point'] = from_match.group(1).strip().rstrip(',').strip()

        to_match = re.search(r'(?:до|в|на)\s+([^.]+?)(?:\s*,|\s*$|\s+в\s+\d)', text, re.IGNORECASE)
        if to_match:
            result['end_point'] = to_match.group(1).strip().rstrip(',').strip()

    return result


def _normalize_result(result):
    """Нормализовать результат парсинга."""
    normalized = {
        'start_point': result.get('start_point', ''),
        'end_point': result.get('end_point', ''),
        'time': result.get('time', ''),
        'seats': int(result.get('seats', 1)),
        'flexibility': int(result.get('flexibility', 15)),
        'raw': '',
    }

    # Convert time string to datetime
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
