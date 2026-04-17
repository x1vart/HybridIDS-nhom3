import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Import tool đường dẫn chuẩn của nhóm trưởng
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.utils import get_mock_path

def prepare_cic_ids_2017(csv_path):
    """Hàm nhai và tiêu hóa dữ liệu thô của Canada thành data chuẩn hợp đồng nhóm 3"""
    print(f"[+] 📂 Đang đọc và ép kiểu dữ liệu từ: {os.path.basename(csv_path)}...")
    df = pd.read_csv(csv_path)
    
    # Chuẩn hóa tên cột gốc (xóa khoảng trắng thừa cho chắc ăn)
    df.columns = df.columns.str.strip()
    
    # Chuyển đổi thành ĐÚNG 4 cột theo Contract
    mapped_data = pd.DataFrame()
    mapped_data['dst_port'] = df['Destination Port']
    mapped_data['packet_count'] = df['Total Fwd Packets'] + df['Total Backward Packets']
    mapped_data['connection_duration'] = df['Flow Duration'] / 1e6 # Đổi micro-giây ra giây
    mapped_data['avg_packet_size'] = df['Packet Length Mean']
    
    # Hàm phiên dịch Nhãn (Label) của Canada sang mã số của nhóm
    # 0: Normal, 1: DoS, 2: Port Scan, 3: Brute Force
    def map_label(label_str):
        label_str = str(label_str).upper()
        if 'BENIGN' in label_str: return 0
        if 'DOS' in label_str or 'HULK' in label_str or 'GOLDENEYE' in label_str or 'SLOWLORIS' in label_str: return 1
        if 'PORTSCAN' in label_str or 'PORT SCAN' in label_str: return 2
        if 'PATATOR' in label_str or 'BRUTE' in label_str: return 3
        return 0 # Mặc định nếu tịt thì cho là Normal
        
    mapped_data['label'] = df['Label'].apply(map_label)
    
    # Dọn rác (NaN, Infinity) hay gặp trong data thực tế
    mapped_data = mapped_data.replace([np.inf, -np.inf], np.nan).dropna()
    return mapped_data

def main():
    print("=== 🚀 BẮT ĐẦU HUẤN LUYỆN AI VỚI DATA CIC-IDS-2017 (CANADA) ===")
    
    # 1. Khai báo 3 file thi đấu
    files_to_train = [
        "Wednesday-workingHours.pcap_ISCX.csv",               # Học môn DoS
        "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv", # Học môn Port Scan
        "Tuesday-WorkingHours.pcap_ISCX.csv"                  # Học môn Brute Force
    ]
    
    all_dataframes = []
    
    # 2. Vòng lặp thu thập data
    for file_name in files_to_train:
        csv_path = get_mock_path(file_name) 
        if os.path.exists(csv_path):
            df = prepare_cic_ids_2017(csv_path)
            all_dataframes.append(df)
        else:
            print(f"[-] CẢNH BÁO: Không tìm thấy file {file_name} trong shared/mock/")
            
    if not all_dataframes:
        print("[-] LỖI CHÍ MẠNG: Không đọc được file dữ liệu nào. Hãy check lại thư mục shared/mock!")
        return

    # 3. Trộn data làm 1
    print("[+] 🔄 Đang nhào lộn và trộn dữ liệu từ 3 file...")
    final_df = pd.concat(all_dataframes, ignore_index=True)
    
    X = final_df.drop('label', axis=1)
    y = final_df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"[+] 📊 Tổng lượng data học: {X_train.shape[0]:,} gói tin.")
    
    # 4. Triệu hồi và Huấn luyện AI
    print("[+] 🧠 Đang bơm kiến thức cho Random Forest (Máy sẽ chạy hết công suất khoảng 1-2 phút)...")
    model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # 5. Chấm thi
    print("\n[+] 📝 BẢNG ĐIỂM TỔNG KẾT (Classification Report):")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=['Normal', 'DoS', 'Port Scan', 'Brute Force'], zero_division=0))
    
    # 6. Đóng gói xuất xưởng
    print("\n[+] 💾 Đang kết xuất bộ não AI ra file...")
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')
    os.makedirs(model_dir, exist_ok=True) 
    model_path = os.path.join(model_dir, 'ids_model.pkl')
    joblib.dump(model, model_path)
    
    print(f"--- ✅ NGHIỆM THU THÀNH CÔNG!  {model_path} ---")

if __name__ == "__main__":
    main()