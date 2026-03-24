from typing import Dict


class AnalyticsService:
    """
    Handles ML analysis, GeoIP enrichment, and statistics.
    """

    # Function 181: Initializes the class instance and its attributes.
    def __init__(self, config: Dict, logger, session_mgr=None):
        self.config = config
        self.logger = logger
        self.session_mgr = session_mgr
        self.logger.log_event(
            "system",
            "service_init",
            {"service": "AnalyticsService", "message": "Starting AnalyticsService"},
        )

        try:
            from cyanide.core.geoip import GeoIP
            from cyanide.core.stats import StatsManager

            self.stats = StatsManager()
            self.geoip = GeoIP()
            self.logger.log_event(
                "system",
                "service_init_status",
                {"service": "AnalyticsService", "message": "Components initialized successfully"},
            )
        except Exception as e:
            self.logger.log_event(
                "system", "service_init_error", {"service": "AnalyticsService", "error": str(e)}
            )

        self.ml_enabled = config.get("ml", {}).get("enabled", False)
        self.ml_online_learning = config.get("ml", {}).get("online_learning", False)
        self.ml_pipeline = None
        self.kb = None

        if self.ml_enabled:
            self._init_ml()

    # Function 182: Performs operations related to init ml.
    def _init_ml(self):
        try:
            from pathlib import Path

            from cyanide.ml import CyanideML

            config_path = self.config.get("ml", {}).get(
                "model_path", "src/cyanide/ml/cyanideML.pkl"
            )
            model_path = Path(config_path).parent

            if (model_path / "cyanideML.pkl").exists():
                self.logger.log_event(
                    "system",
                    "system_status",
                    {"message": f"Loading CyanideML pipeline from {model_path}..."},
                )
                self.ml_pipeline = CyanideML(str(model_path))
            else:
                self.logger.log_event(
                    "system",
                    "system_warning",
                    {"message": "ML models not found. Analysis will be skipped."},
                )
                self.ml_enabled = False
                return

        except ImportError as e:
            self.logger.log_event(
                "system", "error", {"message": f"ML Module could not be loaded: {e}"}
            )
            self.ml_enabled = False
        except Exception as e:
            self.logger.log_event("system", "error", {"message": f"Failed to init ML model: {e}"})
            self.ml_enabled = False

    # Function 183: Performs operations related to analyze command.
    def analyze_command(self, cmd: str, src_ip: str, session_id: str, is_bot: bool = False):
        """Analyze a command string for tools and anomalies."""
        # Record command in session stats
        if self.session_mgr:
            self.session_mgr.record_command(session_id)

        # Automated Tool Detection
        automated_tools = ["wget", "curl", "python ", "perl ", "ruby ", "gcc ", "chmod +x"]
        detected_tool = next((tool.strip() for tool in automated_tools if tool in cmd), None)
        if detected_tool:
            self.logger.log_event(
                session_id,
                "tool_detection",
                {"src_ip": src_ip, "tool": detected_tool, "command": cmd},
            )

        # ML Anomaly Detection
        if not self.ml_enabled or self.ml_pipeline is None:
            return

        try:
            result = self.ml_pipeline.analyze_command(cmd)
            is_anomaly = result["is_anomaly"]
            source_type = "bot" if is_bot else "human"

            self.logger.log_event(
                session_id,
                "ml_thought",
                {
                    "src_ip": src_ip,
                    "verdict": "anomaly" if is_anomaly else "clean",
                    "source_type": source_type,
                    "score": result["anomaly_score"],
                    "error": result["reconstruction_error"],
                    "command": cmd,
                    "classification": result.get("classification"),
                    "severity": result.get("severity"),
                },
            )

            if is_anomaly:
                self.logger.log_event(
                    session_id,
                    "ml_anomaly",
                    {
                        "score": result["anomaly_score"],
                        "error": result["reconstruction_error"],
                        "source_type": source_type,
                        "cmd": cmd,
                        "classification": result.get("classification"),
                        "severity": result.get("severity"),
                    },
                )

        except Exception as e:
            self.logger.log_event(session_id, "error", {"message": f"ML Error: {e}"})

    # Function 184: Performs operations related to analyze file.
    def analyze_file(self, filename: str, content: bytes, session_id: str, src_ip: str):
        """Analyze uploaded file content and filename via ML."""
        if not self.ml_enabled or self.ml_pipeline is None:
            return

        try:
            sample_len = 100
            content_snippet = content[:sample_len].decode("utf-8", "ignore")
            analysis_str = f"FILE_UPLOAD: {filename} CONTENT: {content_snippet}"

            result = self.ml_pipeline.analyze_command(analysis_str)
            is_anomaly = result["is_anomaly"]

            self.logger.log_event(
                session_id,
                "ml_thought",
                {
                    "src_ip": src_ip,
                    "verdict": "anomaly" if is_anomaly else "clean",
                    "score": result["anomaly_score"],
                    "error": result["reconstruction_error"],
                    "file": filename,
                    "type": "file_upload",
                    "classification": result.get("classification"),
                    "severity": result.get("severity"),
                },
            )

            if is_anomaly:
                self.logger.log_event(
                    session_id,
                    "ml_file_anomaly",
                    {
                        "score": result["anomaly_score"],
                        "filename": filename,
                        "classification": result.get("classification"),
                        "severity": result.get("severity"),
                    },
                )
        except Exception as e:
            self.logger.log_event(session_id, "error", {"message": f"ML File Analysis Error: {e}"})

    # Function 185: Handles event logging and telemetry.
    async def log_geoip(self, session_id: str, ip: str, protocol: str):
        """Async GeoIP enrichment logging."""
        geo_data = await self.geoip.lookup(ip)
        ptr_data = await self.geoip.lookup_ptr(ip)

        threat_intel = []
        if ptr_data:
            low_ptr = ptr_data.lower()
            if "shodan" in low_ptr:
                threat_intel.append("Shodan Scanner")
            if "censys" in low_ptr:
                threat_intel.append("Censys Scanner")
            if "shadowserver" in low_ptr:
                threat_intel.append("Shadowserver Scanner")
            if "bolt" in low_ptr or "crawl" in low_ptr:
                threat_intel.append("Bot/Crawler")

        if geo_data:
            # Populate logger cache for automatic enrichment of future events
            if hasattr(self.logger, "geoip_cache"):
                # Also include PTR and Threat Intel in the cache
                enriched_geo = geo_data.copy()
                enriched_geo["ptr"] = ptr_data
                if threat_intel:
                    enriched_geo["threat_intel"] = threat_intel
                self.logger.geoip_cache[ip] = enriched_geo
