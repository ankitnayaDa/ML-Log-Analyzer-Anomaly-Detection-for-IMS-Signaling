import argparse
from pcap_to_json import Pcap_To_Json
from train_model import TrainIMSAnomalyModel
from evaluate_model import  evaluate_model
from detect_anomalies import detect_anomalies

def main():
    #if sys.platform.startswith("win"):
    #    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    #    loop = asyncio.new_event_loop()
    #    asyncio.set_event_loop(loop)
    #nest_asyncio.apply()
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap_to_train', nargs=1)
    parser.add_argument('--pcap_to_evaluate', nargs=1)
    args = parser.parse_args()

    #List To Strings
    pcap_to_train = ' '.join(args.pcap_to_train)
    pcap_to_evaluate = ' '.join(args.pcap_to_evaluate)

    Pcap_To_Json(pcap_to_train,"ims_calls.json")
    Pcap_To_Json(pcap_to_evaluate,"ims_calls_new.json")

    #Train model : This script teaches the ML model what normal IMS signaling looks like like, using a provided pcap file.
    TrainIMSAnomalyModel()
    # Evaluate model behavior
    evaluate_model()
    # Detect anomalies in new pcap
    detect_anomalies()

if __name__ == "__main__":
    main()