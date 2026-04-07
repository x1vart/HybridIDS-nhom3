def predict(features):
    print("ml module working")
    return {}


def detect_ml(features):
    # Backward-compatible alias.
    return predict(features)


def run_ml(features):
    # Alias used by some docs/scripts.
    return predict(features)