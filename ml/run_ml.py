import sys
import argparse
import json

# Cho phép Python nhận diện thư mục gốc của đồ án
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.ml_detector import MLDetector

def main():
    print("--- 🚀 Khởi động Test Module ML ---")
    
    detector = MLDetector()
    
    # 1. Tự đọc file bằng code gốc
    input_path = os.path.join('shared', 'mock', 'mock_features.json')
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            features_data = json.load(f)
        print(f"[+] Đã đọc thông tin IP: {features_data.get('src_ip')}")
    except Exception as e:
        print(f"[-] LỖI đọc file: {e}")
        return

    # 2. Chạy AI dự đoán
    result = detector.predict(features_data)
    print(f"\n[+] Kết quả AI Trả về: \n{result}\n")
    
    # 3. Tự ghi file output luôn
    output_path = os.path.join('shared', 'output', 'ml_result.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
        
    print(f"[+] Đã lưu báo cáo thành công tại: {output_path}")
    print("--- ✅ Test hoàn tất! ---")

def _load_features(input_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        return raw
    raise ValueError(f"Unsupported JSON format in {input_path}. Expected dict or list of dict.")


def _extract_base_and_cases(payload: dict):
    base_features = {k: v for k, v in payload.items() if k != "__cases__"}
    cases = payload.get("__cases__", {})
    if not isinstance(cases, dict):
        cases = {}
    return base_features, cases


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run ML detector with mock features or converted CICIDS JSON features."
    )
    parser.add_argument(
        "--input",
        default="shared/mock/mock_features.json",
        help="Path to input JSON. Supports a single feature dict or list of feature dicts.",
    )
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="If input JSON is a list, choose which item to run.",
    )
    parser.add_argument(
        "--scenario",
        default="default",
        help="Scenario name from '__cases__' when input JSON is a dict. Use 'all' to run all scenarios.",
    )
    args = parser.parse_args()

    if args.input.endswith(".json"):
        if args.input == "shared/mock/mock_features.json":
            payload = load_json(args.input)
            if isinstance(payload, dict):
                base_features, cases = _extract_base_and_cases(payload)

                if args.scenario == "default":
                    features = base_features
                elif args.scenario == "all":
                    if not cases:
                        raise ValueError("No '__cases__' found in mock_features.json")
                    for scenario_name, overrides in cases.items():
                        scenario_features = dict(base_features)
                        scenario_features.update(overrides)
                        result = predict(scenario_features)
                        print(f"[run_ml] scenario={scenario_name}")
                        print(result)
                    raise SystemExit(0)
                else:
                    if args.scenario not in cases:
                        raise ValueError(
                            f"Unknown scenario '{args.scenario}'. Available: default, all, {', '.join(cases.keys())}"
                        )
                    features = dict(base_features)
                    features.update(cases[args.scenario])
            else:
                features = payload
        else:
            rows = _load_features(args.input)
            if not rows:
                raise ValueError(f"No feature rows found in {args.input}")
            if args.index < 0 or args.index >= len(rows):
                raise IndexError(
                    f"--index out of range. Got {args.index}, but input has {len(rows)} rows."
                )
            features = rows[args.index]
            print(f"[run_ml] Loaded {len(rows)} rows from {args.input}; using index {args.index}")
    else:
        raise ValueError("Only JSON input is currently supported.")

    result = predict(features)
    print(result)
