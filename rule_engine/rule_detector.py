def detect(features):
    print("rule engine working")
    return {}


def detect_rule(features):
    # Backward-compatible alias.
    return detect(features)


def run_rule(features):
    # Alias used by some docs/scripts.
    return detect(features)