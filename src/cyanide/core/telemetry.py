from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
import os

def setup_telemetry(service_name: str, version: str = "1.0.0"):
    """Initialize OpenTelemetry."""
    resource = Resource.create({
        "service.name": service_name,
        "service.version": version,
    })

    provider = TracerProvider(resource=resource)
    
    # Check if OTLP endpoint is configured
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    
    if otlp_endpoint:
        exporter = OTLPSpanExporter()
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        print(f"[*] Telemetry: OTLP Exporter enabled ({otlp_endpoint})")
    elif os.getenv("CYANIDE_DEBUG_TRACE"):
        # Fallback to Console for debugging if env var set
        exporter = ConsoleSpanExporter()
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        print("[*] Telemetry: Console Exporter enabled")
    else:
        # No-op or just provider without processors implies no export
        # But we still set the provider so instrumentation works (just doesn't go anywhere)
        pass

    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
