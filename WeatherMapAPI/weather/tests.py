from unittest.mock import patch
import requests
from django.test import TestCase, Client
from django.urls import reverse

class WeatherAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('weather:index')
        
        # Sample response matching OpenWeather JSON format
        self.mock_success_response = {
            "coord": {"lon": 70.803, "lat": 22.3039},
            "weather": [{"id": 803, "main": "Clouds", "description": "scattered clouds", "icon": "03d"}],
            "base": "stations",
            "main": {
                "temp": 32.5,
                "feels_like": 35.2,
                "temp_min": 32.5,
                "temp_max": 32.5,
                "pressure": 1008,
                "humidity": 55,
                "sea_level": 1008,
                "grnd_level": 998
            },
            "visibility": 10000,
            "wind": {"speed": 4.12, "deg": 240, "gust": 5.2},
            "clouds": {"all": 40},
            "dt": 1685860000,
            "sys": {"type": 1, "id": 9070, "country": "IN", "sunrise": 1685838000, "sunset": 1685886000},
            "timezone": 19800,
            "id": 1258526,
            "name": "Rajkot",
            "cod": 200
        }

    @patch('requests.get')
    def test_default_city_on_get(self, mock_get):
        """Verify that opening the home page via GET queries for the default city (Rajkot)."""
        # Mock requests.get to return status 200 with mock JSON
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.mock_success_response
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')
        
        # Verify the context contains weather data
        self.assertIsNotNone(response.context['weather'])
        self.assertEqual(response.context['weather']['city_name'], 'Rajkot')
        self.assertEqual(response.context['weather']['country'], 'IN')
        self.assertEqual(response.context['weather']['temp_c'], 32.5)
        # 32.5 * 9/5 + 32 = 90.5
        self.assertEqual(response.context['weather']['temp_f'], 90.5)
        self.assertEqual(response.context['weather']['weather_desc'], 'Scattered Clouds')
        
        # Verify API request parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['q'], 'Rajkot')

    @patch('requests.get')
    def test_search_city_on_post(self, mock_get):
        """Verify that searching a city via POST queries the API for that city."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.mock_success_response
        
        response = self.client.post(self.url, {'city': 'Rajkot'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['weather'])
        self.assertEqual(response.context['weather']['city_name'], 'Rajkot')
        
        # Verify API request parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['q'], 'Rajkot')

    @patch('requests.get')
    def test_city_not_found_error(self, mock_get):
        """Verify the app displays a proper error message when a city is not found (404)."""
        mock_get.return_value.status_code = 404
        
        response = self.client.post(self.url, {'city': 'InvalidCityName'})
        
        self.assertEqual(response.status_code, 200)
        self.assertNil = response.context['weather']
        self.assertIsNone(response.context['weather'])
        self.assertIn("City 'InvalidCityName' not found. Please try again.", response.context['error_message'])
        self.assertContains(response, "City &#x27;InvalidCityName&#x27; not found")

    @patch('requests.get')
    def test_connection_error_handling(self, mock_get):
        """Verify that request connection errors are caught and shown gracefully."""
        mock_get.side_effect = requests.RequestException("Connection timed out")
        
        response = self.client.post(self.url, {'city': 'London'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['weather'])
        self.assertIn("Connection error. Please check your internet connectivity.", response.context['error_message'])
        self.assertContains(response, "Connection error")
