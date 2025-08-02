import os


class MongoDBConfig:
    DATABASE = "Qryptify_database"


class MonitoringConfig:
    MONITOR_ROOT_PATH = os.getenv("MONITOR_ROOT_PATH", "/home/monitor/.log/")
