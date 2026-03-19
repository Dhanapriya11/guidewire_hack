import random, uuid
from datetime import datetime

class PayoutEngine:
    SEVERITY_MULTIPLIER = {'low': 0.25, 'medium': 0.50, 'high': 0.75}
    PAYOUT_LOG = []

    def calculate_payout(self, daily_payout, severity, duration_hours):
        mult   = self.SEVERITY_MULTIPLIER.get(severity, 0.5)
        hrs    = min(duration_hours, 10) / 10
        amount = round(daily_payout * mult * (0.5 + hrs * 0.5))
        return max(50, min(amount, daily_payout))

    def process_payout(self, phone, amount):
        ref = f'GS{uuid.uuid4().hex[:8].upper()}'
        success = random.random() > 0.02   # 98% success
        result  = {
            'status':    'success' if success else 'pending',
            'reference': ref,
            'amount':    amount,
            'phone':     phone[-4:].rjust(10, '*'),
            'channel':   random.choice(['UPI', 'IMPS']),
            'timestamp': datetime.now().isoformat()
        }
        self.PAYOUT_LOG.append(result)
        return result


class DataStore:
    """In-memory store. Replace with PostgreSQL/Redis in production."""
    def __init__(self):
        self._workers  = {}
        self._pool     = {'balance': 5000.0, 'total_in': 5000.0, 'total_out': 0.0}
        self._weekly   = {}

    def save_worker(self, wid, data):
        self._workers[wid] = data

    def get_worker(self, wid):
        return self._workers.get(wid)

    def get_all_workers(self):
        return list(self._workers.values())

    def get_workers_by_district(self, district):
        return [w for w in self._workers.values() if w.get('district') == district]

    def add_to_pool(self, amount):
        self._pool['balance']  += amount
        self._pool['total_in'] += amount
        week = datetime.now().strftime('%Y-W%W')
        self._weekly.setdefault(week, {'in': 0, 'out': 0})
        self._weekly[week]['in'] += amount

    def deduct_from_pool(self, amount):
        self._pool['balance']   = max(0, self._pool['balance'] - amount)
        self._pool['total_out'] += amount
        week = datetime.now().strftime('%Y-W%W')
        self._weekly.setdefault(week, {'in': 0, 'out': 0})
        self._weekly[week]['out'] += amount

    def get_pool_status(self):
        b = self._pool
        return {
            'balance':   round(b['balance'], 2),
            'total_in':  round(b['total_in'], 2),
            'total_out': round(b['total_out'], 2),
            'health':    'healthy' if b['balance'] > b['total_out'] * 0.5 else 'low'
        }

    def get_weekly_trend(self):
        return [{'week': k, 'premium_in': v['in'], 'payout_out': v['out']}
                for k, v in sorted(self._weekly.items())]
