import sys
import os
import json  # Dùng luôn thư viện gốc của Python, không thèm dùng utils của nhóm trưởng

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

if __name__ == "__main__":
    main()