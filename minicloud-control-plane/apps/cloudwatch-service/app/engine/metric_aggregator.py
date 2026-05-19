def aggregate(values: list[float], statistic: str) -> float | None:
    if not values:
        return None
    if statistic == "Sum":
        return float(sum(values))
    if statistic == "Average":
        return float(sum(values) / len(values))
    if statistic == "Minimum":
        return float(min(values))
    if statistic == "Maximum":
        return float(max(values))
    if statistic == "Count":
        return float(len(values))
    raise ValueError(f"Unsupported statistic: {statistic}")


def compare(value: float, operator: str, threshold: float) -> bool:
    if operator == "GreaterThanThreshold":
        return value > threshold
    if operator == "GreaterThanOrEqualToThreshold":
        return value >= threshold
    if operator == "LessThanThreshold":
        return value < threshold
    if operator == "LessThanOrEqualToThreshold":
        return value <= threshold
    if operator == "EqualToThreshold":
        return value == threshold
    raise ValueError(f"Unsupported comparison operator: {operator}")

