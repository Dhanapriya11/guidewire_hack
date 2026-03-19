import pandas as pd
import numpy as np
import random
from datetime import datetime

class RiskEngine:
    PLATFORM_RISK_MULTIPLIER = {
        'Zomato':   1.1,
        'Swiggy':   1.1,
        'Zepto':    1.0,
        'Blinkit':  1.0,
        'Amazon':   0.9,
        'Flipkart': 0.9,
        'Dunzo':    1.05
    }

    SEASON_MULTIPLIER = {
        'Winter':  0.8,
        'Summer':  1.2,
        'Monsoon': 1.5,
        'Autumn':  0.9
    }

    DISRUPTION_EVENTS = [
        {
            'type':           'Heavy Rainfall',
            'severity':       'high',
            'duration_hours': 6,
            'description':    'Heavy rainfall exceeding 80mm detected',
            'trigger_param':  'rainfall > 80mm',
            'icon':           '🌧️'
        },
        {
            'type':           'Extreme Heat',
            'severity':       'medium',
            'duration_hours': 8,
            'description':    'Temperature exceeding 42°C - unsafe for outdoor work',
            'trigger_param':  'temp > 42°C',
            'icon':           '🌡️'
        },
        {
            'type':           'High Wind Speed',
            'severity':       'medium',
            'duration_hours': 4,
            'description':    'Wind speed exceeding 35 km/h affecting deliveries',
            'trigger_param':  'wind > 35 km/h',
            'icon':           '💨'
        },
        {
            'type':           'Flood Warning',
            'severity':       'high',
            'duration_hours': 12,
            'description':    'District flood warning issued by authorities',
            'trigger_param':  'flood_warning = true',
            'icon':           '🌊'
        },
        {
            'type':           'Government Curfew',
            'severity':       'high',
            'duration_hours': 10,
            'description':    'Unplanned curfew restricting movement',
            'trigger_param':  'curfew = true',
            'icon':           '🚫'
        },
        {
            'type':           'Local Strike',
            'severity':       'medium',
            'duration_hours': 5,
            'description':    'Transport strike blocking delivery zones',
            'trigger_param':  'strike = true',
            'icon':           '✊'
        }
    ]

    def __init__(self):
        self.risk_data = self._load_risk_data()
        self.current_season = self._get_current_season()

    def _load_risk_data(self):
        """Load pre-computed district risk profiles."""
        try:
            df = pd.read_csv('district_risk_profile.csv')

            # ── FIX: Remove duplicate districts ──────────────
            # Sort by risk_score descending so we keep the highest
            df = df.sort_values('risk_score', ascending=False)
            # Keep first occurrence (highest risk score) per district
            df = df.drop_duplicates(subset='district', keep='first')
            # Now safe to index by district
            return df.set_index('district').to_dict('index')

        except FileNotFoundError:
            # Fallback sample data if CSV not present
            return {
                'Nagapattinam': {'state': 'Tamil Nadu',  'risk_score': 83,  'risk_level': 'High Risk',   'disruption_rate': 28},
                'Chennai':      {'state': 'Tamil Nadu',  'risk_score': 75,  'risk_level': 'High Risk',   'disruption_rate': 22},
                'Coimbatore':   {'state': 'Tamil Nadu',  'risk_score': 55,  'risk_level': 'Medium Risk', 'disruption_rate': 15},
                'Madurai':      {'state': 'Tamil Nadu',  'risk_score': 50,  'risk_level': 'Medium Risk', 'disruption_rate': 12},
                'Salem':        {'state': 'Tamil Nadu',  'risk_score': 40,  'risk_level': 'Medium Risk', 'disruption_rate': 10},
                'Trichy':       {'state': 'Tamil Nadu',  'risk_score': 45,  'risk_level': 'Medium Risk', 'disruption_rate': 11},
                'Pollachi':     {'state': 'Tamil Nadu',  'risk_score': 35,  'risk_level': 'Low Risk',    'disruption_rate': 8},
                'Mumbai City':  {'state': 'Maharashtra', 'risk_score': 101, 'risk_level': 'High Risk',   'disruption_rate': 35},
                'Pune':         {'state': 'Maharashtra', 'risk_score': 121, 'risk_level': 'High Risk',   'disruption_rate': 40},
                'Delhi':        {'state': 'Delhi',       'risk_score': 65,  'risk_level': 'Medium Risk', 'disruption_rate': 18},
            }

    def _get_current_season(self):
        month = datetime.now().month
        if month in [12, 1, 2]:    return 'Winter'
        if month in [3, 4, 5]:     return 'Summer'
        if month in [6, 7, 8, 9]:  return 'Monsoon'
        return 'Autumn'

    def get_district_risk(self, district, state):
        """Get risk profile for a district."""
        if district in self.risk_data:
            d = self.risk_data[district]
            return {
                'district':        district,
                'state':           state,
                'risk_score':      d.get('risk_score', 50),
                'risk_level':      d.get('risk_level', 'Medium Risk'),
                'disruption_rate': d.get('disruption_rate', 15)
            }
        # Estimate from state average if district not found
        state_districts = {
            k: v for k, v in self.risk_data.items()
            if v.get('state') == state
        }
        if state_districts:
            avg_score = np.mean([v['risk_score'] for v in state_districts.values()])
            return {
                'district':        district,
                'state':           state,
                'risk_score':      avg_score,
                'risk_level':      self._score_to_level(avg_score),
                'disruption_rate': 15
            }
        return {
            'district':        district,
            'state':           state,
            'risk_score':      50,
            'risk_level':      'Medium Risk',
            'disruption_rate': 15
        }

    def _score_to_level(self, score):
        if score >= 100: return 'High Risk'
        if score >= 70:  return 'Medium Risk'
        return 'Low Risk'

    def calculate_weekly_premium(self, risk_score, avg_weekly_earnings, platform):
        """Dynamic premium calculation."""
        normalized_risk = min(risk_score / 130, 1.0)
        base_rate       = 0.02 + (normalized_risk * 0.03)
        plat_mult       = self.PLATFORM_RISK_MULTIPLIER.get(platform, 1.0)
        season_mult     = self.SEASON_MULTIPLIER.get(self.current_season, 1.0)
        premium         = avg_weekly_earnings * base_rate * plat_mult * season_mult
        # Round to nearest 5, min ₹20 max ₹60
        premium = max(20, min(60, round(premium / 5) * 5))
        return int(premium)

    def calculate_payout(self, avg_weekly_earnings):
        """Daily payout = roughly 1 day's earnings."""
        return round(avg_weekly_earnings / 6)

    def simulate_disruption_check(self, district, state):
        """Simulate real-time disruption check."""
        risk         = self.get_district_risk(district, state)
        disruption_prob = risk['disruption_rate'] / 100

        if random.random() < disruption_prob:
            event = random.choice(self.DISRUPTION_EVENTS)
            return {
                'disruption_detected': True,
                'district':            district,
                'state':               state,
                'event_type':          event['type'],
                'severity':            event['severity'],
                'duration_hours':      event['duration_hours'],
                'description':         event['description'],
                'trigger_param':       event['trigger_param'],
                'icon':                event['icon'],
                'data_source':         'OpenMeteo API + IMD + GDELT',
                'confidence':          round(random.uniform(0.82, 0.98), 2),
                'timestamp':           str(datetime.now())
            }
        return {
            'disruption_detected': False,
            'district':            district,
            'state':               state,
            'weather':             'Normal',
            'message':             'No disruption detected. All clear!'
        }

    def get_top_risk_districts(self, n=5):
        """Return top N high-risk districts."""
        sorted_d = sorted(
            self.risk_data.items(),
            key=lambda x: x[1].get('risk_score', 0),
            reverse=True
        )
        return [
            {
                'district':   k,
                'state':      v.get('state', ''),
                'risk_score': round(v.get('risk_score', 0), 1),
                'risk_level': v.get('risk_level', '')
            }
            for k, v in sorted_d[:n]
        ]
