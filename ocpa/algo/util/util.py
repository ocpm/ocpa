import statistics

AGG_MAP = {
    'avg': statistics.mean,
    'med': statistics.median,
    'std': statistics.stdev,
    'sum': sum,
    'min': min,
    'max': max
}
