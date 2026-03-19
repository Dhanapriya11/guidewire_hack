"""
Run this FIRST to generate district_risk_profile.csv from your dataset.
Usage: python analysis.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def run_analysis(input_file='indian_weather.xlsx'):
    print("📊 GigShield Risk Analysis Starting...")

    # ── Load ────────────────────────────────────────────────────────────────
    if input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    else:
        df = pd.read_csv(input_file)

    print(f"✅ Loaded {len(df)} rows")
    print(f"   Columns: {list(df.columns)}")

    # ── Parse dates ─────────────────────────────────────────────────────────
    if 'date_of_record' in df.columns:
        df['date_of_record'] = pd.to_datetime(df['date_of_record'], errors='coerce')

    # ── Clean ───────────────────────────────────────────────────────────────
    df.dropna(subset=['rainfall', 'avg_temp', 'wind_speed'], inplace=True)

    # ── Disruption flags ────────────────────────────────────────────────────
    HEAVY_RAIN   = 50
    EXTREME_HEAT = 40
    HIGH_WIND    = 30

    df['rain_disruption'] = (df['rainfall']   >= HEAVY_RAIN).astype(int)
    df['heat_disruption'] = (df['max_temp']   >= EXTREME_HEAT).astype(int)
    df['wind_disruption'] = (df['wind_speed'] >= HIGH_WIND).astype(int)
    df['disruption_day']  = (
        df['rain_disruption'] | df['heat_disruption'] | df['wind_disruption']
    ).astype(int)

    # ── District-level aggregation ───────────────────────────────────────────
    grp_cols = ['state', 'district'] if 'district' in df.columns else ['state', 'station_name']
    district_col = 'district' if 'district' in df.columns else 'station_name'

    district_risk = df.groupby(grp_cols).agg(
        total_days      = ('date_of_record', 'count') if 'date_of_record' in df.columns else ('rainfall','count'),
        disruption_days = ('disruption_day', 'sum'),
        avg_rainfall    = ('rainfall',       'mean'),
        max_rainfall    = ('rainfall',       'max'),
        avg_temp        = ('avg_temp',        'mean'),
        max_temp        = ('max_temp',        'max'),
        avg_wind        = ('wind_speed',      'mean'),
    ).reset_index()

    district_risk['disruption_rate'] = (
        district_risk['disruption_days'] / district_risk['total_days'] * 100
    ).round(1)

    district_risk['risk_score'] = (
        district_risk['avg_rainfall']    * 0.40 +
        district_risk['max_rainfall']    * 0.25 +
        district_risk['avg_wind']        * 0.20 +
        district_risk['disruption_rate'] * 0.15
    ).round(2)

    # ── Adjusted thresholds ──────────────────────────────────────────────────
    def assign_risk(score):
        if score >= 100: return 'High Risk',   60   # ₹60/week
        elif score >= 70: return 'Medium Risk', 40  # ₹40/week
        else:             return 'Low Risk',    20  # ₹20/week

    district_risk[['risk_level', 'weekly_premium']] = district_risk['risk_score'].apply(
        lambda s: pd.Series(assign_risk(s))
    )

    # Rename for consistency
    if district_col == 'station_name':
        district_risk = district_risk.rename(columns={'station_name': 'district'})

    result = district_risk[['state','district','disruption_days','disruption_rate',
                             'risk_score','risk_level','weekly_premium',
                             'avg_rainfall','avg_wind','avg_temp']]\
             .sort_values('risk_score', ascending=False)

    # ── Save ────────────────────────────────────────────────────────────────
    result.to_csv('district_risk_profile.csv', index=False)
    print(f"\n✅ Saved district_risk_profile.csv ({len(result)} districts)")

    # ── Print summary ────────────────────────────────────────────────────────
    print("\n🔴 TOP 10 HIGH RISK DISTRICTS:")
    high = result[result['risk_level'] == 'High Risk'].head(10)
    print(high[['state','district','risk_score','weekly_premium']].to_string(index=False))

    print("\n🟡 SAMPLE MEDIUM RISK DISTRICTS:")
    med = result[result['risk_level'] == 'Medium Risk'].head(5)
    print(med[['state','district','risk_score','weekly_premium']].to_string(index=False))

    print("\n🟢 SAMPLE LOW RISK DISTRICTS:")
    low = result[result['risk_level'] == 'Low Risk'].head(5)
    print(low[['state','district','risk_score','weekly_premium']].to_string(index=False))

    # ── Chart ────────────────────────────────────────────────────────────────
    top20  = result.head(20)
    colors = top20['risk_level'].map({'High Risk':'red','Medium Risk':'orange','Low Risk':'green'})

    plt.figure(figsize=(16, 6))
    plt.bar(top20['district'], top20['risk_score'], color=colors)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.title('Top 20 Districts by Risk Score - GigShield Analysis', fontsize=13)
    plt.ylabel('Risk Score')
    plt.tight_layout()

    from matplotlib.patches import Patch
    legend = [Patch(color='red',label='High Risk (₹60/wk)'),
              Patch(color='orange',label='Medium Risk (₹40/wk)'),
              Patch(color='green',label='Low Risk (₹20/wk)')]
    plt.legend(handles=legend)
    plt.savefig('district_risk_chart.png', dpi=150)
    print("\n✅ Chart saved: district_risk_chart.png")
    plt.show()

    return result

if __name__ == '__main__':
    run_analysis()
