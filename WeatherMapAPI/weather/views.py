import requests
from datetime import datetime, timezone, timedelta
from django.shortcuts import render

def get_cardinal_direction(deg):
    try:
        deg = float(deg)
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = int((deg + 11.25) / 22.5) % 16
        return directions[index]
    except (ValueError, TypeError):
        return "N/A"

def index(request):
    api_key = '225af36405b8b0eea0ee5bb66e191958'
    city = request.POST.get('city', 'Rajkot').strip() if request.method == 'POST' else 'Rajkot'
    
    weather_data = None
    error_message = None
    
    if city:
        api_url = 'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Extract timezone offset in seconds
                tz_offset = data.get('timezone', 0)
                
                # Convert timestamps to local times of the target city
                def format_local_time(timestamp, fmt='%I:%M %p'):
                    utc_time = datetime.fromtimestamp(timestamp, timezone.utc)
                    local_time = utc_time + timedelta(seconds=tz_offset)
                    return local_time.strftime(fmt)
                
                # Temp conversions and values
                temp_c = data['main']['temp']
                temp_f = temp_c * 9/5 + 32
                
                feels_like_c = data['main']['feels_like']
                feels_like_f = feels_like_c * 9/5 + 32
                
                temp_min_c = data['main']['temp_min']
                temp_min_f = temp_min_c * 9/5 + 32
                
                temp_max_c = data['main']['temp_max']
                temp_max_f = temp_max_c * 9/5 + 32
                
                wind_speed_mps = data['wind'].get('speed', 0)
                wind_speed_kmh = wind_speed_mps * 3.6
                wind_speed_mph = wind_speed_mps * 2.23694
                
                wind_deg = data['wind'].get('deg', 0)
                wind_direction = get_cardinal_direction(wind_deg)
                
                sunrise_str = format_local_time(data['sys']['sunrise'])
                sunset_str = format_local_time(data['sys']['sunset'])
                
                # Measurement time
                dt_str = format_local_time(data['dt'], '%b %d, %Y %I:%M %p')
                
                visibility_m = data.get('visibility', 0)
                visibility_km = visibility_m / 1000.0
                visibility_mi = visibility_m * 0.000621371
                
                weather_data = {
                    'city_name': data['name'],
                    'country': data['sys'].get('country', ''),
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon'],
                    'temp_c': round(temp_c, 1),
                    'temp_f': round(temp_f, 1),
                    'feels_like_c': round(feels_like_c, 1),
                    'feels_like_f': round(feels_like_f, 1),
                    'temp_min_c': round(temp_min_c, 1),
                    'temp_min_f': round(temp_min_f, 1),
                    'temp_max_c': round(temp_max_c, 1),
                    'temp_max_f': round(temp_max_f, 1),
                    'pressure': data['main']['pressure'],
                    'humidity': data['main']['humidity'],
                    'weather_main': data['weather'][0]['main'],
                    'weather_desc': data['weather'][0]['description'].title(),
                    'weather_icon': data['weather'][0]['icon'],
                    'wind_speed_kmh': round(wind_speed_kmh, 1),
                    'wind_speed_mph': round(wind_speed_mph, 1),
                    'wind_direction': wind_direction,
                    'wind_deg': wind_deg,
                    'clouds': data['clouds'].get('all', 0),
                    'sunrise': sunrise_str,
                    'sunset': sunset_str,
                    'visibility_km': round(visibility_km, 1),
                    'visibility_mi': round(visibility_mi, 1),
                    'updated_at': dt_str,
                }
            elif response.status_code == 404:
                error_message = f"City '{city}' not found. Please try again."
            else:
                error_message = "Unable to fetch weather data. OpenWeather API error."
        except requests.RequestException:
            error_message = "Connection error. Please check your internet connectivity."
            
    context = {
        'weather': weather_data,
        'error_message': error_message,
        'searched_city': city,
    }
    
    return render(request, 'weather/index.html', context)
