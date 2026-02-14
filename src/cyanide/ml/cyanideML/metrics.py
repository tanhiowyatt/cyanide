try:
    from prometheus_client import Counter, Histogram, REGISTRY
except ImportError:
    # Fallback if library not present
    class MockMetric:
        def labels(self, **kwargs): return self
        def inc(self, amount=1): pass
        def observe(self, amount): pass
        def __init__(self, *args, **kwargs): pass
        
    Counter = MockMetric
    Histogram = MockMetric
    REGISTRY = None

def get_safe_metric(metric_class, name, documentation, labelnames=None, **kwargs):
    """Safely register or retrieve a metric from the global registry."""
    if REGISTRY:
        # Check if metric already exists in the global registry
        # prometheus_client stores them in _names_to_collectors
        existing = REGISTRY._names_to_collectors.get(name)
        if existing:
            return existing
            
    return metric_class(name, documentation, labelnames=labelnames or [], **kwargs)

_metrics = None

def get_metrics():
    """Get or create singleton metrics."""
    global _metrics
    if _metrics is None:
        _metrics = {
            'logs_processed': get_safe_metric(
                Counter,
                'honeypot_logs_processed_total', 
                'Total number of logs processed by ML filter',
                ['status'] # 'anomaly' or 'clean'
            ),
            'latency': get_safe_metric(
                Histogram,
                'honeypot_processing_latency_seconds',
                'Time taken to process a single log',
                buckets=[0.0005, 0.001, 0.002, 0.005, 0.01, 0.05, 0.1]
            ),
            'distance': get_safe_metric(
                Histogram,
                'honeypot_distance_score',
                'Distance score of logs from nearest cluster',
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
            )
        }
    return _metrics

# For backward compatibility / ease of use
def get_processed_metric(): return get_metrics()['logs_processed']
def get_latency_metric(): return get_metrics()['latency']
def get_distance_metric(): return get_metrics()['distance']
