import pandas as pd
import joblib
import os

# ---------- Paths ----------
MODEL_PATH = "output/ims_isolation_forest.pkl"
INPUT_LOGS_PATH = "data/ims_calls_new.json"
OUTPUT_REPORT_PATH = "output/anomaly_report.csv"

os.makedirs("output", exist_ok=True)

def detect_anomalies():
    # ---------- Load new IMS call logs ----------
    pd.set_option('future.no_silent_downcasting', True)
    df = pd.read_json(INPUT_LOGS_PATH)

    # ---------- Feature Engineering (MUST match training) ----------
    df["latency_100"] = df["response_times_ms"].apply(lambda x: x.get("100") if isinstance(x, dict) else None)
    df["latency_180"] = df["response_times_ms"].apply(lambda x: x.get("180") if isinstance(x, dict) else None)
    df["latency_200"] = df["response_times_ms"].apply(lambda x: x.get("200") if isinstance(x, dict) else None)
    df["invite_to_180_gap"] = df["latency_180"] - df["latency_100"]

    # ---------- Prepare ML features ----------
    df_ml = df.drop(columns=["call_id","invite_time","final_status","response_times_ms","anomaly"],errors="ignore")
    df_ml = pd.get_dummies(df_ml, columns=["method"], drop_first=True)
    df_ml = df_ml.fillna(-1)

    # ---------- Load trained model ----------
    model = joblib.load(MODEL_PATH)

    # ---------- Predict anomalies ----------
    df["anomaly_flag"] = model.predict(df_ml)

    # ---------- Filter anomalies ----------
    anomalies = df[df["anomaly_flag"] == -1]

    # ---------- Save anomaly report ----------
    anomalies.to_csv(OUTPUT_REPORT_PATH, index=False)

    # ---------- Console summary ----------
    print("\n--- IMS LOG ANOMALY DETECTION ---")
    print(f"Total calls analyzed : {len(df)}")
    print(f"Anomalies detected   : {len(anomalies)}")
    print(f"Report saved to      : {OUTPUT_REPORT_PATH}")

    # Optional: show top anomalies
    if not anomalies.empty:
        print("\nSample anomalous calls:")
        print(anomalies[["call_id", "latency_200", "final_status"]].head())