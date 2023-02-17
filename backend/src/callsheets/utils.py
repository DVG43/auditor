import json
from callsheets.wmo_codes import WMO_codes
import requests


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_location(ip: str) -> dict:
    url = f'http://ru.sxgeo.city/json/{ip}'

    try:
        res = requests.get(url)
        data = json.loads(res.text)
        lat = data['city']['lat']
        lng = data['city']['lon']
        city = data['city']['name_ru']
    except:
        lat, lng = 0, 0
        city = ''

    locaition = {
        'lat': lat,
        'lng': lng,
        'city': city

    }
    return locaition


def get_weather(loc: dict, date: str) -> dict:
    lat = loc['lat']
    lng = loc['lng']
    url = f'https://api.open-meteo.com/v1/forecast?' \
          f'latitude={lat}&longitude={lng}&' \
          f'daily=temperature_2m_max,temperature_2m_min,weathercode,sunrise,sunset&' \
          f'timezone=auto&start_date={date}&end_date={date}'

    try:
        res = requests.get(url)
        data = json.loads(res.text)
        max_temp = round(float(data['daily']['temperature_2m_max'][0]))
        min_temp = round(float(data['daily']['temperature_2m_min'][0]))
        temp = round(float('%.1f' % ((max_temp + min_temp) / 2)))
        wmo_c = data['daily']['weathercode'][0]
        weather = WMO_codes[wmo_c]
        sunset = data['daily']['sunset'][0].split('T')[1]
        sunrise = data['daily']['sunrise'][0].split('T')[1]
    except:
        max_temp, min_temp, temp = 0, 0, 0
        sunset, sunrise = '00:00', '00:00'
        weather = ''
    weather = {
        'sunrise': sunrise,
        'sunset': sunset,
        'temp': temp,
        'max_temp': max_temp,
        'min_temp': min_temp,
        'weather': weather,
    }
    return weather
