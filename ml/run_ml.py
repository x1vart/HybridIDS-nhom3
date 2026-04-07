from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml import predict
from shared.utils import load_json


if __name__ == "__main__":
    features = load_json("shared/mock/mock_features.json")
    result = predict(features)
    print(result)
