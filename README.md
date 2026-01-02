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

## Technical Stack

- Language: Python 3.9+
- ML Libraries: Scikit-learn, Pandas, NumPy
- Telecom Interfaces: Wireshark (pcap export), SIP, Diameter

## Repository layout

- `IMS.pcap`, `siminv.pcap` — example PCAP files (raw traces)
- `pcap_to_json.py` — PCAP → structured JSON conversion script
- `train_model.py` — training and evaluation script for anomaly detection
- `data/ims_calls.json` — example structured dataset produced from PCAPs

## Quickstart

1. Prepare a Python environment (recommended: Python 3.8+).

2. Install required packages (add or update this project `requirements.txt` as needed):

```bash
python -m pip install pandas scikit-learn pyshark
```

3. Convert PCAP to JSON (example):

```bash
python pcap_to_json.py
```

4. Train the model (example):

```bash
python train_model.py
```

Note: The exact script arguments can be inspected in `pcap_to_json.py` and `train_model.py` — adapt flags as implemented.

## Data format

The converter produces a JSON array of call-flow records. Each record should contain timestamped protocol messages (SIP/Diameter/etc.) and minimal meta fields (call id, from/to, message type). This structured format lets the ML stage extract sequences, timing, and feature vectors for clustering or sequence-alignment.

## Approach (high level)

- Data ingestion: convert PCAPs into structured JSON call-flows using `pcap_to_json.py`.
- Feature extraction: build sequence/timing features from the structured call flows.
- Modeling: use unsupervised methods (K-Means, clustering, or sequence-alignment) to learn typical call-flow behavior.
- Detection: flag deviations from the learned baseline and surface the specific message(s) where divergence occurs.

## Integration ideas

- Create a Robot Framework listener that calls the analyzer on test failure and attaches a short report describing the divergent message and similarity scores to a "golden" trace.
- Wrap the analyzer in a small HTTP service or CLI for CI integration.

## License

Add a license file or header if you plan to open-source this repository.