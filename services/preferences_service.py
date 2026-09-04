def calculate_compatibility(ride_or_driver_prefs, request_or_passenger_prefs):
    """
    Рассчитать совместимость между водителем и пассажиром.
    Возвращает значение от 0 до 1.
    """
    # Get preferences
    driver_prefs = {
        'music': getattr(ride_or_driver_prefs, 'music_pref', 'neutral'),
        'talk': getattr(ride_or_driver_prefs, 'talk_pref', 'neutral'),
        'ac': getattr(ride_or_driver_prefs, 'ac_pref', 'no_matter'),
        'smoking': getattr(ride_or_driver_prefs, 'smoking', False),
    }
    passenger_prefs = {
        'music': getattr(request_or_passenger_prefs, 'music_pref', 'neutral'),
        'talk': getattr(request_or_passenger_prefs, 'talk_pref', 'neutral'),
        'ac': getattr(request_or_passenger_prefs, 'ac_pref', 'no_matter'),
        'smoking': getattr(request_or_passenger_prefs, 'smoking', False),
    }

    score = 0
    total = 4  # 4 categories

    for key in ['music', 'talk', 'ac', 'smoking']:
        dp = driver_prefs[key]
        pp = passenger_prefs[key]
        if dp == pp:
            score += 1
        elif dp == 'neutral' or pp == 'neutral':
            score += 0.5
        # else 0

    return score / total
