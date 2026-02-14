# Observability Guide 📊

Cyanide Honeypot supports modern observability standards including **OpenTelemetry** for distributed tracing and **Prometheus** for metrics.

## 📈 Prometheus Metrics

The honeypot exposes a metrics server (default port `9090`) with the following endpoints:

*   `/metrics`: Standard Prometheus metrics.
*   `/stats`: Human-readable JSON summary of honeypot activity.
*   `/health`: System health check (JSON). Returns version, uptime, and service status.

### Key Metrics
| Metric | Type | Description |
|--------|------|-------------|
| `cyanide_active_sessions` | Gauge | Current number of active SSH/Telnet sessions. |
| `cyanide_total_sessions_total` | Counter | Total connections received. |
| `cyanide_uptime_seconds` | Counter | Honeypot uptime in seconds. |
| `cyanide_protocols_total{protocol="..."}` | Counter | Connections broken down by protocol (ssh, telnet). |
| `cyanide_honeytoken_hits_total{path="..."}` | Counter | Hits on specific honeytoken files. |
| `cyanide_malware_scans_total` | Counter | Total files scanned for malware. |
| `cyanide_malicious_files_total` | Counter | Number of files flagged as malicious by VirusTotal. |
| `cyanide_dns_cache_hits_total` | Counter | Number of successful DNS cache lookups. |
| `cyanide_dns_cache_misses_total` | Counter | Number of DNS lookups that required resolution. |

### Alerts
We provide a pre-configured Prometheus alerting rules file:
[prometheus-alerts.yml](../data/observability/prometheus-alerts.yml)

To use it, add the following to your `prometheus.yml`:
```yaml
rule_files:
  - "prometheus-alerts.yml"
```

---

## 🕵️ OpenTelemetry Tracing

Cyanide uses OpenTelemetry to trace internal operations such as command execution, filesystem access, and network requests.

### Jaeger Setup (Recommended)
The easiest way to view traces is using **Jaeger**.

1.  **Run Jaeger via Docker**:
    ```bash
    docker run --name jaeger \
      -e COLLECTOR_OTLP_ENABLED=true \
      -p 16686:16686 \
      -p 4317:4317 \
      -p 4318:4318 \
      jaegertracing/all-in-one:latest
    ```

2.  **Enable Tracing in `cyanide.cfg`**:
    Configure the OTLP exporter to point to your Jaeger instance:
    ```ini
    [otel]
    enabled = true
    exporter = otlp
    endpoint = http://localhost:4318/v1/traces
    ```

3.  **Environment Variables**:
    You can also use standard OpenTelemetry environment variables:
    ```bash
    export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
    export OTEL_SERVICE_NAME="cyanide-honeypot"
    ```

### Exporting Traces
Traces are automatically exported via OTLP over HTTP or gRPC. In a production Docker setup, ensure the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable is set to your collector/backend address.

---

## 📊 Dashboards

We provide a ready-to-use Grafana dashboard:
[grafana-dashboard.json](../data/observability/grafana-dashboard.json)

### Importing to Grafana:
1.  Open Grafana and go to **Dashboards** > **Import**.
2.  Upload the `grafana-dashboard.json` file.
3.  Select your Prometheus data source.
4.  Click **Import**.

---

## 🛠️ Debugging Observability

If metrics or traces are not appearing:
1.  Check that `[metrics] enabled = true` is set in the configuration.
2.  Verify connectivity to the Jaeger/Collector endpoint (e.g., `curl http://localhost:4318/v1/traces`).
3.  Check the honeypot logs for `otel_error` or `metrics_error` events.
4.  Run with `CYANIDE_DEBUG_TRACE=1` to see spans in the console.
