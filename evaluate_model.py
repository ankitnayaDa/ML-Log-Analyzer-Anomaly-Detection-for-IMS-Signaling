import pandas as pd
import joblib
import os

# ---------- Paths ----------
MODEL_PATH = "output/ims_isolation_forest.pkl"
EVAL_DATA_PATH = "data/ims_calls.json"
OUTPUT_EVAL_REPORT = "output/evaluation_summary.csv"

def evaluate_model():
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # ---------- Load evaluation data ----------
    df = pd.read_json(EVAL_DATA_PATH)

    # ---------- Feature Engineering (must match training) ----------
    df["latency_100"] = df["response_times_ms"].apply(lambda x: x.get("100") if isinstance(x, dict) else None)
    df["latency_180"] = df["response_times_ms"].apply(lambda x: x.get("180") if isinstance(x, dict) else None)
    df["latency_200"] = df["response_times_ms"].apply(lambda x: x.get("200") if isinstance(x, dict) else None)
    df["invite_to_180_gap"] = df["latency_180"] - df["latency_100"]

    df_ml = df.drop(columns=["call_id","invite_time","final_status","response_times_ms","anomaly"],errors="ignore")
    df_ml = pd.get_dummies(df_ml, columns=["method"], drop_first=True)
    df_ml = df_ml.fillna(-1)

    # ---------- Load model ----------
    model = joblib.load(MODEL_PATH)

    # ---------- Predict ----------
    df["anomaly_flag"] = model.predict(df_ml)

    # ---------- Evaluation Metrics ----------
    total_calls = len(df)
    anomaly_count = (df["anomaly_flag"] == -1).sum()
    anomaly_rate = anomaly_count / total_calls

    # ---------- Print evaluation ----------
    print("\n--- IMS LOG ANOMALY EVALUATION ---")
    print(f"Total calls analyzed : {total_calls}")
    print(f"Anomalies detected   : {anomaly_count}")
    print(f"Anomaly rate         : {anomaly_rate:.2%}")

    # ---------- Save evaluation summary ----------
    summary = pd.DataFrame({"total_calls": [total_calls],"anomalies_detected": [anomaly_count],"anomaly_rate": [anomaly_rate],})

    summary.to_csv(OUTPUT_EVAL_REPORT, index=False)

    print(f"\n📄 Evaluation summary saved to: {OUTPUT_EVAL_REPORT}")
    print("----------------------------------\n")