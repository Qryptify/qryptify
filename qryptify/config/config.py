import os


class TimescaleDBConfig:
    CONNECTION_URL = os.getenv("TIMESCALEDB_HOST", "localhost")
    DATABASE = os.getenv("TIMESCALEDB_DATABASE", "qryptify")
    USER = os.getenv("TIMESCALEDB_USER", "postgres")
    PASSWORD = os.getenv("TIMESCALEDB_PASSWORD", "password")


class MonitoringConfig:
    MONITOR_ROOT_PATH = os.getenv("MONITOR_ROOT_PATH", "/home/monitor/.log/")
