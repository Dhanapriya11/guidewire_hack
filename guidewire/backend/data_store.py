from datetime import datetime

class DataStore:
    """In-memory data store. Replace with PostgreSQL in production."""

    def __init__(self):
        self._workers  = {}
        self._pool     = {
            'balance':  5000.0,
            'total_in': 5000.0,
            'total_out': 0.0
        }
        self._weekly = {}

    # ── WORKER ────────────────────────────────────────────
    def save_worker(self, wid, data):
        self._workers[wid] = data

    def get_worker(self, wid):
        return self._workers.get(wid)

    def get_all_workers(self):
        return list(self._workers.values())

    def get_workers_by_district(self, district):
        return [
            w for w in self._workers.values()
            if w.get('district') == district
        ]

    # ── POOL ──────────────────────────────────────────────
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
        return [
            {
                'week':        k,
                'premium_in':  v['in'],
                'payout_out':  v['out']
            }
            for k, v in sorted(self._weekly.items())
        ]
