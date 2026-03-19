import random
from datetime import datetime, timedelta

class FraudDetector:
    """
    AI-powered fraud detection for parametric insurance claims.
    Detects: GPS spoofing, duplicate claims, fake disruption reports,
             claim velocity abuse, and location mismatches.
    """

    FRAUD_FLAGS = []
    FRAUD_STATS = {
        'total_analyzed': 0,
        'flagged':         0,
        'approved':        0,
        'flag_reasons':    {}
    }

    def analyze(self, worker, claim_data):
        """Full fraud analysis for a claim."""
        self.FRAUD_STATS['total_analyzed'] += 1
        flags  = []
        score  = 0.0   # 0 = clean, 1 = definite fraud

        # ── 1. Duplicate claim check ───────────────────────────────────────
        recent_claims = [
            c for c in worker.get('claims', [])
            if self._hours_ago(c.get('timestamp', '')) < 24
        ]
        if len(recent_claims) >= 2:
            flags.append('Multiple claims within 24 hours')
            score += 0.4

        # ── 2. GPS/Location validation ────────────────────────────────────
        claimed_district = claim_data.get('district', '')
        worker_district  = worker.get('district', '')
        if claimed_district and claimed_district != worker_district:
            flags.append(f'Location mismatch: registered in {worker_district}, claiming from {claimed_district}')
            score += 0.35

        # ── 3. Claim velocity check ───────────────────────────────────────
        total_claims = len(worker.get('claims', []))
        weeks_active = max(1, (datetime.now() - datetime.fromisoformat(
            worker.get('joined_date', datetime.now().isoformat())
        )).days // 7)
        weekly_claim_rate = total_claims / weeks_active
        if weekly_claim_rate > 3:
            flags.append(f'Unusually high claim rate: {weekly_claim_rate:.1f}/week')
            score += 0.25

        # ── 4. Payout vs premium ratio ────────────────────────────────────
        total_received   = worker.get('total_received', 0)
        total_contributed = worker.get('total_contributed', 1)
        if total_received > total_contributed * 5:
            flags.append('Payout-to-premium ratio exceeds 5x threshold')
            score += 0.3

        # ── 5. Platform activity check (simulated) ────────────────────────
        platform_active = self._check_platform_activity(worker)
        if not platform_active and claim_data.get('disruption', {}).get('severity') == 'low':
            flags.append('No platform activity gap detected during claimed disruption period')
            score += 0.2

        # ── 6. Simulated GPS spoofing detection ───────────────────────────
        gps_spoof_prob = random.random()
        if gps_spoof_prob < 0.05:   # 5% chance of GPS spoof
            flags.append('GPS coordinates show stationary position during claimed work hours')
            score += 0.45

        is_fraud   = score >= 0.5
        fraud_score = round(min(score, 1.0), 2)

        if is_fraud:
            self.FRAUD_STATS['flagged'] += 1
            reason = flags[0] if flags else 'Anomaly detected'
            self.FRAUD_FLAGS.append({
                'worker_id':  worker.get('worker_id'),
                'name':       worker.get('name'),
                'fraud_score': fraud_score,
                'flags':      flags,
                'timestamp':  datetime.now().isoformat()
            })
            for f in flags:
                self.FRAUD_STATS['flag_reasons'][f] = self.FRAUD_STATS['flag_reasons'].get(f, 0) + 1
            return {'is_fraud': True,  'fraud_score': fraud_score, 'flags': flags, 'reason': reason}

        self.FRAUD_STATS['approved'] += 1
        return {'is_fraud': False, 'fraud_score': fraud_score, 'flags': [], 'reason': None}

    def quick_check(self, worker):
        """Fast check for auto-triggered parametric payouts."""
        score = 0.0
        flags = []
        recent = [c for c in worker.get('claims', []) if self._hours_ago(c.get('timestamp','')) < 6]
        if len(recent) >= 1:
            score += 0.6
            flags.append('Already received payout in last 6 hours')
        return {'is_fraud': score >= 0.5, 'fraud_score': score, 'flags': flags, 'reason': flags[0] if flags else None}

    def _check_platform_activity(self, worker):
        """Simulate checking platform API for activity gaps."""
        return random.random() > 0.1   # 90% of time, activity gap found

    def _hours_ago(self, ts_string):
        if not ts_string:
            return 999
        try:
            ts = datetime.fromisoformat(ts_string)
            return (datetime.now() - ts).total_seconds() / 3600
        except:
            return 999

    def get_analytics(self):
        return {
            'stats':         self.FRAUD_STATS,
            'recent_flags':  self.FRAUD_FLAGS[-10:],
            'fraud_rate':    round(
                self.FRAUD_STATS['flagged'] / max(1, self.FRAUD_STATS['total_analyzed']) * 100, 1
            ),
            'detection_methods': [
                'Duplicate claim detection (24h window)',
                'GPS location validation',
                'Claim velocity analysis',
                'Payout-to-premium ratio check',
                'Platform activity gap verification',
                'GPS spoofing detection'
            ]
        }
