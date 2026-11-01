import unittest
import json
from app import app, FEATURE_NAMES

class PrecipiCastTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def test_index_route(self):
        """Verify the main dashboard HTML serves successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PrecipiCast', response.data)
        self.assertIn(b'Rainwater Harvesting', response.data)

    def test_health_probe(self):
        """Verify the health check endpoint reports ready status."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertTrue(data.get('model_loaded'))
        self.assertEqual(data.get('features_count'), 11)

    def test_api_info_metadata(self):
        """Verify the API documentation endpoint exposes full schema."""
        response = self.client.get('/api/info')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get('algorithm'), 'XGBoost Regressor')
        self.assertIn('metrics', data)
        self.assertEqual(len(data.get('features', [])), 11)

    def test_prediction_default_scenario(self):
        """Verify prediction for normal tropical atmospheric input."""
        payload = {
            "sw_down": 18.5, "sw_direct": 10.2, "temp_avg": 27.5,
            "temp_dew": 24.1, "temp_wet": 25.8, "temp_max": 30.1,
            "temp_min": 25.0, "humidity_rel": 85.5, "humidity_spec": 19.1,
            "wind_speed": 2.5, "soil_wetness": 0.85
        }
        response = self.client.post('/predict',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('prediction_mm', data)
        self.assertGreaterEqual(data['prediction_mm'], 0.0)
        self.assertIn('category', data)

    def test_prediction_extreme_monsoon(self):
        """Verify prediction under saturated monsoon storm conditions."""
        payload = {
            "sw_down": 5.0, "sw_direct": 1.0, "temp_avg": 25.0,
            "temp_dew": 24.5, "temp_wet": 24.8, "temp_max": 26.0,
            "temp_min": 24.0, "humidity_rel": 98.0, "humidity_spec": 22.0,
            "wind_speed": 5.0, "soil_wetness": 0.98
        }
        response = self.client.post('/predict',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        # Wet storm scenario should yield rainfall > 10mm
        self.assertGreater(data['prediction_mm'], 10.0)

    def test_invalid_input_handling(self):
        """Verify 400 Bad Request on invalid parameter types."""
        payload = {
            "sw_down": "not-a-number",
            "soil_wetness": 0.85
        }
        response = self.client.post('/predict',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
