# AI-Powered Telecom Log Analyzer

As telecom networks transition to 5G and Cloud-Native architectures, manual log analysis of SIP/Diameter flows becomes a bottleneck. This project implements an Unsupervised Machine Learning approach to automatically identify anomalies in telecom signaling logs.
By using the Isolation Forest algorithm, this tool flags irregular latencies and unexpected protocol status codes without requiring manually labeled "failure" data, significantly reducing Root Cause Analysis (RCA) time in CI/CD pipelines..

## Key Goals

- Reduce manual debugging time for IMS/VoIP/telecom call flows
- Convert PCAP traces to structured data for ML and comparison
- Train a baseline model on successful (golden) traces and detect anomalies
- Integrate with Robot Framework or CI to run on test failures

## Key features

- Protocol-Aware Parsing: Extracts features from SIP, Diameter, and 3GPP-compliant logs using Python and Regex.
- Unsupervised Learning: Utilizes Scikit-learn’s IsolationForest to detect outliers in high-dimensional protocol data.
- Feature Engineering: Converts categorical telecom methods (INVITE, REGISTER, etc.) into numerical vectors via One-Hot Encoding.
- CI/CD Ready: Designed to be integrated into Jenkins/Robot Framework as a post-test diagnostic utility.

## Solution Approach

The solution uses unsupervised machine learning (Isolation Forest) to learn normal IMS call behavior from historical data and flag deviations as anomalies.

Why Isolation Forest?
- Telecom logs are often unlabeled
- Anomalies are rare
- Isolation Forest is efficient and explainable for such use cases

## End-to-End ML Workflow

      ```
      PCAP / SIP Logs
            ↓
      Structured IMS Call Data (JSON)
            ↓
      Feature Engineering (Latency & Call Flow Metrics)
            ↓
      Model Training (Isolation Forest)
            ↓
      Model Evaluation (Anomaly Rate & Sanity Checks)
            ↓
      Anomaly Detection on New pcap
            ↓
      CSV Anomaly Report for Debugging
      ```

## Dataset Description
Each IMS explanation represents a single SIP call flow, extracted from packet captures.
Example Fields:
- call_id – Unique call identifier
- method – SIP method (INVITE, ACK, etc.)
- response_times_ms – SIP response timing (100, 180, 200)
- final_status – Call result (SUCCESS, FAILED, TIMEOUT)
- invite_time – Call start timestamp
- The dataset is stored as structured JSON for easy processing.

## Feature Engineering
Key telecom-aware features extracted:
- latency_100 – Time to 100 Trying
- latency_180 – Time to 180 Ringing
- latency_200 – Time to 200 OK
- invite_to_180_gap – Call progress delay
- Encoded SIP method (categorical → numerical)
These features represent call setup health and signaling behavior.

## Model Training

This step learns what normal IMS call behavior looks like.
Process:
- Load historical IMS call data
- Apply feature engineering
- Train an Isolation Forest model
- Save the trained model
- Generate an initial anomaly report

Outputs:
- Trained model: ims_isolation_forest.pkl
- Initial anomaly report: ims_anomaly_report.csv

## Model Evaluation

Since labeled anomaly data is typically unavailable in telecom logs, evaluation is performed using unsupervised metrics and domain sanity checks.
Evaluation includes:
- Total calls analyzed
- Number of anomalies detected
- Anomaly rate (%)
Results are validated using telecom domain knowledge (e.g., missing 200 OK, abnormal latencies).

## Anomaly Detection

This script applies the trained model to new or unseen IMS logs.
Process:
- Load new IMS call data
- Apply the same feature engineering pipeline
- Detect anomalous calls
- Export anomaly report for debugging
Output:
- anomaly_report.csv – list of abnormal call flows

## Technical Stack

- Language: Python 3.9+
- ML Libraries: Scikit-learn, Pandas, NumPy
- Telecom Interfaces: Wireshark (pcap export), SIP

## Repository Structure
```
ML-Log-Analyzer-Anomaly-Detection-for-IMS-Signaling/
├── detect_anomalies.py
├── evaluate_model.py
├── pcap_to_json.py
├── pipeline.py
├── README.md
├── requirements.txt
├── train_model.py
├── data/
│   ├── ims_calls.json
│   └── ims_calls_new.json
└── output/
      ├── anomaly_report.csv
      ├── evaluation_summary.csv
      └── ims_anomaly_report.csv
```

## Setup & Usage

1. Clone the repository
```
git clone https://github.com/ankitnayaDa/ML-Log-Analyzer-Anomaly-Detection-for-IMS-Signaling.git
cd AI-powered-Test-Case-Generator
```
2. Create virtual environment
```
python -m venv venv
source venv/bin/activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Run script
```
python pipeline.py --pcap_to_train siminv.pcap --pcap_to_evaluate IMS1.pcap
```

## Example Output

Total calls analyzed : 500
Anomalies detected   : 62
Report saved to      : output/anomaly_report.csv

## CSV

call_id,latency_100,latency_180,latency_200,final_status,anomaly_flag
abc123,120,450,,TIMEOUT,-1
def456,100,300,2500,FAILED,-1