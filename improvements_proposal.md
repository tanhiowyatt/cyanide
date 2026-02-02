# Future Improvements

Based on the current state of Cyanide, here are the recommended next steps:

## 1. Deployment & Infrastructure
- **Docker Compose**: Currently, we have a `Dockerfile` but no `docker-compose.yml`. Adding this would allow easy deployment alongside ELK (Elasticsearch/Logstash/Kibana) or Splunk for real-time log visualization.
- **Port Binding**: Ensure ports 2222 (SSH) and 2223 (Telnet) are easily configurable via environment variables in Compose.

## 2. Network Realism
- **Async Execution**: The `wget` command logic suggests a need to refactor `ShellEmulator` to fully support asynchronous execution. Currently, `wget` might block or fail if not handled correctly.
- **SCP/SFTP**: Add support for file transfers via SSH. AsyncSSH supports this, but we need to map it to our FakeFilesystem (and Quarantine).

## 3. Visualization
- **Dashboard**: A simple web dashboard (e.g., standard Python/React app) to view:
    - Active sessions.
    - Top attacker IPs.
    - Recent commands.
- **TTY Player**: A web-based player to replay the recorded TTY logs visually.

## 4. Monitoring
- **Prometheus Metrics**: Export metrics (sessions count, commands per minute) for Grafana.

## Recommendation
I suggest starting with **Docker Compose and ELK Integration** to verify the JSON logs value immediately, or fixing the **Async Shell** architecture to make `wget` robust.
