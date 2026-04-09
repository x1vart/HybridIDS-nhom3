import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

def create_synthetic_data(num_samples=2000):
    print("[1] 🛠️ Đang tạo data giả lập KHỚP VỚI SCHEMA CỦA KIÊN...")
    np.random.seed(42)
    # Tự tạo dữ liệu số y hệt như các key trong file mock_features.json
    data = {
        'dst_port': np.random.choice([80, 443, 22, 21, 3306], num_samples),
        'packet_count': np.random.randint(1, 500, num_samples),
        'connection_duration': np.random.uniform(0.1, 10.0, num_samples),
        'avg_packet_size': np.random.uniform(40.0, 1500.0, num_samples),
        'label': np.random.choice([0, 1, 2, 3], num_samples, p=[0.7, 0.1, 0.1, 0.1]) 
    }
    return pd.DataFrame(data)

def main():
    print("=== 🚀 BẮT ĐẦU HUẤN LUYỆN BỘ NÃO AI ===")
    df = create_synthetic_data()
    X = df.drop('label', axis=1) 
    y = df['label']              
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("[2] 🧠 Đang cho AI học (Training)...")
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')
    os.makedirs(model_dir, exist_ok=True) 
    model_path = os.path.join(model_dir, 'ids_model.pkl')
    joblib.dump(model, model_path)
    
    print(f"--- ✅ Đã lưu bộ não chuẩn tại: {model_path} ---")

if __name__ == "__main__":
    main()