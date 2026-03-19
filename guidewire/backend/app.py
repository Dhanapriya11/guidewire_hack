from flask import Flask, request, jsonify
from flask_cors import CORS
import json, random, uuid
from datetime import datetime, timedelta
from risk_engine import RiskEngine
from fraud_detector import FraudDetector
from payout_engine import PayoutEngine
from data_store import DataStore

app = Flask(__name__)
CORS(app)

risk_engine   = RiskEngine()
fraud_detector = FraudDetector()
payout_engine  = PayoutEngine()
db            = DataStore()

# ─── ONBOARDING ───────────────────────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    required = ['name','phone','district','state','platform','vehicle_type','avg_weekly_earnings']
    for f in required:
        if f not in data:
            return jsonify({'error': f'Missing field: {f}'}), 400

    worker_id = str(uuid.uuid4())[:8].upper()
    risk      = risk_engine.get_district_risk(data['district'], data['state'])
    premium   = risk_engine.calculate_weekly_premium(
        risk['risk_score'], data['avg_weekly_earnings'], data['platform']
    )
    payout    = risk_engine.calculate_payout(data['avg_weekly_earnings'])

    worker = {
        'worker_id':           worker_id,
        'name':                data['name'],
        'phone':               data['phone'],
        'district':            data['district'],
        'state':               data['state'],
        'platform':            data['platform'],
        'vehicle_type':        data['vehicle_type'],
        'avg_weekly_earnings': data['avg_weekly_earnings'],
        'risk_level':          risk['risk_level'],
        'risk_score':          risk['risk_score'],
        'weekly_premium':      premium,
        'daily_payout':        payout,
        'pool_balance':        0,
        'joined_date':         datetime.now().isoformat(),
        'status':              'active',
        'total_contributed':   0,
        'total_received':      0,
        'claims':              []
    }
    db.save_worker(worker_id, worker)

    # Add to chit pool
    db.add_to_pool(premium)

    return jsonify({
        'success':        True,
        'worker_id':      worker_id,
        'risk_level':     risk['risk_level'],
        'risk_score':     round(risk['risk_score'], 1),
        'weekly_premium': premium,
        'daily_payout':   payout,
        'message':        f'Welcome to GigShield! Weekly premium ₹{premium} will be auto-deducted.'
    })

# ─── WORKER PROFILE ───────────────────────────────────────────────────────────
@app.route('/api/worker/<worker_id>', methods=['GET'])
def get_worker(worker_id):
    worker = db.get_worker(worker_id)
    if not worker:
        return jsonify({'error': 'Worker not found'}), 404
    return jsonify(worker)

# ─── POLICY MANAGEMENT ────────────────────────────────────────────────────────
@app.route('/api/policy/<worker_id>', methods=['GET'])
def get_policy(worker_id):
    worker = db.get_worker(worker_id)
    if not worker:
        return jsonify({'error': 'Worker not found'}), 404

    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_end   = week_start + timedelta(days=6)

    return jsonify({
        'worker_id':      worker_id,
        'policy_number':  f'GS-{worker_id}-{datetime.now().strftime("%Y%W")}',
        'status':         'active',
        'coverage_week':  {
            'start': week_start.strftime('%Y-%m-%d'),
            'end':   week_end.strftime('%Y-%m-%d')
        },
        'weekly_premium': worker['weekly_premium'],
        'daily_payout':   worker['daily_payout'],
        'covered_events': [
            'Heavy Rainfall (>50mm)',
            'Extreme Heat (>40°C)',
            'High Winds (>30 km/h)',
            'Flood Warning',
            'Government Curfew',
            'Local Strike'
        ],
        'district':    worker['district'],
        'risk_level':  worker['risk_level'],
        'pool_status': db.get_pool_status()
    })

# ─── WEEKLY PREMIUM DEDUCTION ─────────────────────────────────────────────────
@app.route('/api/deduct-premium/<worker_id>', methods=['POST'])
def deduct_premium(worker_id):
    worker = db.get_worker(worker_id)
    if not worker:
        return jsonify({'error': 'Worker not found'}), 404

    premium = worker['weekly_premium']
    worker['total_contributed'] += premium
    worker['pool_balance']      += premium
    db.save_worker(worker_id, worker)
    db.add_to_pool(premium)

    return jsonify({
        'success':           True,
        'deducted':          premium,
        'total_contributed': worker['total_contributed'],
        'message':           f'₹{premium} deducted from your {worker["platform"]} earnings and added to community pool.'
    })

# ─── DISRUPTION MONITORING ────────────────────────────────────────────────────
@app.route('/api/check-disruption', methods=['POST'])
def check_disruption():
    data = request.json
    district = data.get('district')
    state    = data.get('state')

    disruption = risk_engine.simulate_disruption_check(district, state)
    return jsonify(disruption)

# ─── CLAIM PROCESSING ─────────────────────────────────────────────────────────
@app.route('/api/claim', methods=['POST'])
def process_claim():
    data      = request.json
    worker_id = data.get('worker_id')
    worker    = db.get_worker(worker_id)
    if not worker:
        return jsonify({'error': 'Worker not found'}), 404

    # Fraud detection
    fraud_result = fraud_detector.analyze(worker, data)
    if fraud_result['is_fraud']:
        return jsonify({
            'success':      False,
            'fraud_detected': True,
            'reason':       fraud_result['reason'],
            'message':      'Claim flagged for review.'
        }), 400

    disruption = data.get('disruption', {})
    payout_amt = payout_engine.calculate_payout(
        worker['daily_payout'],
        disruption.get('severity', 'medium'),
        disruption.get('duration_hours', 4)
    )

    claim_id = str(uuid.uuid4())[:8].upper()
    claim = {
        'claim_id':     claim_id,
        'worker_id':    worker_id,
        'disruption':   disruption,
        'payout_amount': payout_amt,
        'status':       'approved',
        'timestamp':    datetime.now().isoformat(),
        'fraud_score':  fraud_result['fraud_score'],
        'auto_approved': True
    }

    worker['claims'].append(claim)
    worker['total_received'] += payout_amt
    db.save_worker(worker_id, worker)
    db.deduct_from_pool(payout_amt)

    # Simulate payout
    payout_result = payout_engine.process_payout(worker['phone'], payout_amt)

    return jsonify({
        'success':       True,
        'claim_id':      claim_id,
        'payout_amount': payout_amt,
        'payout_status': payout_result['status'],
        'upi_ref':       payout_result['reference'],
        'message':       f'₹{payout_amt} approved and sent to your UPI!'
    })

# ─── AUTO TRIGGER (parametric) ────────────────────────────────────────────────
@app.route('/api/auto-trigger', methods=['POST'])
def auto_trigger():
    data     = request.json
    district = data.get('district')
    state    = data.get('state')

    disruption = risk_engine.simulate_disruption_check(district, state)
    if not disruption.get('disruption_detected'):
        return jsonify({'message': 'No disruption detected. All clear!', 'triggered': False})

    # Find all workers in district
    all_workers = db.get_workers_by_district(district)
    payouts_processed = []

    for worker in all_workers:
        fraud_result = fraud_detector.quick_check(worker)
        if fraud_result['is_fraud']:
            continue

        payout_amt    = payout_engine.calculate_payout(
            worker['daily_payout'],
            disruption['severity'],
            disruption['duration_hours']
        )
        payout_result = payout_engine.process_payout(worker['phone'], payout_amt)

        claim = {
            'claim_id':      str(uuid.uuid4())[:8].upper(),
            'worker_id':     worker['worker_id'],
            'disruption':    disruption,
            'payout_amount': payout_amt,
            'status':        'auto_approved',
            'timestamp':     datetime.now().isoformat(),
            'auto_triggered': True
        }
        worker['claims'].append(claim)
        worker['total_received'] += payout_amt
        db.save_worker(worker['worker_id'], worker)
        db.deduct_from_pool(payout_amt)

        payouts_processed.append({
            'worker_id': worker['worker_id'],
            'name':      worker['name'],
            'payout':    payout_amt,
            'upi_ref':   payout_result['reference']
        })

    return jsonify({
        'triggered':         True,
        'disruption':        disruption,
        'workers_paid':      len(payouts_processed),
        'total_payout':      sum(p['payout'] for p in payouts_processed),
        'payouts':           payouts_processed
    })

# ─── ANALYTICS DASHBOARD ──────────────────────────────────────────────────────
@app.route('/api/analytics', methods=['GET'])
def analytics():
    all_workers  = db.get_all_workers()
    pool_status  = db.get_pool_status()
    risk_dist    = {}
    platform_dist = {}
    total_claims = 0
    total_payout = 0

    for w in all_workers:
        rl = w.get('risk_level', 'Unknown')
        risk_dist[rl] = risk_dist.get(rl, 0) + 1
        pl = w.get('platform', 'Unknown')
        platform_dist[pl] = platform_dist.get(pl, 0) + 1
        total_claims += len(w.get('claims', []))
        total_payout += w.get('total_received', 0)

    total_premium = sum(w.get('total_contributed', 0) for w in all_workers)
    loss_ratio    = round((total_payout / total_premium * 100), 1) if total_premium else 0

    return jsonify({
        'total_workers':    len(all_workers),
        'pool_status':      pool_status,
        'total_claims':     total_claims,
        'total_payout':     total_payout,
        'total_premium':    total_premium,
        'loss_ratio':       loss_ratio,
        'risk_distribution': risk_dist,
        'platform_distribution': platform_dist,
        'high_risk_districts': risk_engine.get_top_risk_districts(5),
        'weekly_trend':     db.get_weekly_trend()
    })

# ─── FRAUD ANALYTICS ──────────────────────────────────────────────────────────
@app.route('/api/fraud-analytics', methods=['GET'])
def fraud_analytics():
    return jsonify(fraud_detector.get_analytics())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
