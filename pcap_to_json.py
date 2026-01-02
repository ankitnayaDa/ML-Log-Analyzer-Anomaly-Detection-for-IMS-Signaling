import pyshark
from collections import defaultdict
import json
from typing import Dict, Any, Optional

LATENCY_THRESHOLD_MS = 150  # example anomaly threshold
OUTPUT_DIR = "data"

def pcap_to_json(pcap_file, output_file):
    cap = pyshark.FileCapture(pcap_file, keep_packets=False,decode_as={"udp.port==5062": "sip"})
    call_state: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"invite_time": None, "responses": {}})

    # ---------- PARSE PCAP ----------
    for packet in cap:
        if not hasattr(packet, "sip"):
            continue

        sip = packet.sip
        timestamp = packet.sniff_time
        call_id = sip.get_field("call_id")

        if not call_id:
            continue

        # SIP REQUEST
        method = sip.get_field("method")
        if method == "INVITE":
            if call_state[call_id]["invite_time"] is None:
                call_state[call_id]["invite_time"] = timestamp

        # SIP RESPONSE
        status_code = sip.get_field("status_code")
        if status_code:
            code = int(status_code)
            call_state[call_id]["responses"][code] = timestamp

    # ---------- BUILD JSON ----------
    output = []
    for call_id, data in call_state.items():
        invite_time = data["invite_time"]
        responses = data["responses"]
        if not invite_time:
            continue

        response_times_ms = {}
        latency_ms = None
        final_status = None

        for code, ts in responses.items():
            delta_ms = int((ts - invite_time).total_seconds() * 1000)
            response_times_ms[str(code)] = delta_ms

        if "200" in response_times_ms:
            latency_ms = response_times_ms["200"]
            final_status = "200 OK"

        anomaly = latency_ms is not None and latency_ms > LATENCY_THRESHOLD_MS
        output.append({
            "call_id": call_id,
            "method": "INVITE",
            "invite_time": invite_time.isoformat() if invite_time else None,
            "response_times_ms": response_times_ms,
            "final_status": final_status,
            "latency_ms": latency_ms,
            "anomaly": anomaly
        })

    # ---------- WRITE JSON ----------
    with open(f"{OUTPUT_DIR}/{output_file}", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"[+] JSON written to {output_file}")


if __name__ == "__main__":
    pcap_to_json("IMS.pcap", "ims_calls.json")