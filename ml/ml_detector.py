import os
import joblib
from datetime import datetime

class MLDetector:
    def __init__(self):
        # Đường dẫn tìm file model AI chuẩn hợp đồng
        base_path = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_path, 'model', 'ids_model.pkl')
        
        self.is_ready = False
        try:
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.is_ready = True
                print("[ML] Đã load model thật thành công!")
            else:
                print("[ML] Cảnh báo: Chưa có file .pkl.")
        except Exception as e:
            print(f"[ML] Lỗi load model: {e}")

    def predict(self, features_dict: dict) -> dict:
        """Nhận đặc trưng (features) và trả về chuẩn MLResult."""
        src_ip = features_dict.get("src_ip", "0.0.0.0")

        if not features_dict:
            return self._format_response("Normal", 0.0, src_ip)

        if self.is_ready:
            try:
                # Trích xuất ĐÚNG 4 biến số đã học từ file JSON của Kiên
                dst_port = features_dict.get("dst_port", 0)
                packet_count = features_dict.get("packet_count", 0)
                conn_duration = features_dict.get("connection_duration", 0.0)
                avg_size = features_dict.get("avg_packet_size", 0.0)
                
                features_list = [dst_port, packet_count, conn_duration, avg_size]
                
                prediction_num = self.model.predict([features_list])[0]
                
                if prediction_num == 1:
                    return self._format_response("DoS", 0.95, src_ip)
                elif prediction_num == 2:
                    return self._format_response("Port Scan", 0.90, src_ip)
                elif prediction_num == 3:
                    return self._format_response("Brute Force", 0.88, src_ip)
                else:
                    return self._format_response("Normal", 0.99, src_ip)
                    
            except Exception as e:
                print(f"[ML] Lỗi lúc predict: {e}")
                return self._format_response("Unknown", 0.0, src_ip)
        else:
            return self._format_response("Normal", 0.99, src_ip)

    def _format_response(self, prediction: str, confidence: float, src_ip: str) -> dict:
        """Gói output chuẩn 100% theo class MLResult của nhóm trưởng."""
        return {
            "prediction": prediction,
            "confidence": confidence,
            "src_ip": src_ip,
            "timestamp": datetime.now().isoformat()
        }