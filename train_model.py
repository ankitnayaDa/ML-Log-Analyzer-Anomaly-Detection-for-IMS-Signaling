import pandas as pd
#Unsupervised anomaly detection
from sklearn.ensemble import IsolationForest
import os
import json

# ---------- SIP call data extracted from PCAP ----------
INPUT_JSON = "data/ims_calls.json"
with open(INPUT_JSON, "r") as f:
    data = json.load(f)
#Convert into a DataFrame | 2-dimensional table of data, similar to a spreadsheet
df = pd.DataFrame(data)

# ---------- Feature Engineering: Convert SIP signaling into numbers ----------
# --- Flatten SIP response times ---
df['latency_100'] = df['response_times_ms'].apply(lambda x: x.get('100') if isinstance(x, dict) else None)
df['latency_180'] = df['response_times_ms'].apply(lambda x: x.get('180') if isinstance(x, dict) else None)
df['latency_200'] = df['response_times_ms'].apply(lambda x: x.get('200') if isinstance(x, dict) else None)

# --- Prepare ML DataFrame ---
#Numeric-only DataFrame for ML model
df_ml = df.drop(columns=[
    'call_id',
    'invite_time',
    'final_status',
    'response_times_ms',
    'anomaly'
], errors='ignore')

# Encode categorical fields
df_ml = pd.get_dummies(df_ml, columns=['method'], drop_first=True)

# Handle missing values
df_ml = df_ml.fillna(-1)
df_ml['invite_to_180_gap'] = df_ml['latency_180'] - df_ml['latency_100']
#Indexer Row/column selection
df.loc[df['latency_200'].isna(), 'Anomaly_Flag'] = -1

# --- Train Isolation Forest AL Model ---
#Learns what normal IMS calls look like | Flags calls that don’t fit the pattern 
#“I expect ~15% of calls to be problematic” as contamination parameter set as 0.15
model = IsolationForest(contamination=0.15, random_state=42)
#Predict anomalies
df['Anomaly_Flag'] = model.fit_predict(df_ml)

# --- Results ---
print("--- LOG ANALYSIS RESULTS ---")
#print(df[['call_id', 'latency_200', 'Anomaly_Flag']])

anomalies = df[df['Anomaly_Flag'] == -1]
print("\n--- DETECTED ANOMALIES ---")
print(anomalies[['call_id', 'latency_200']])