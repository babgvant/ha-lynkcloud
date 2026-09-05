"""Constants for the Discover Energy LYNK Cloud integration."""

from datetime import timedelta

DOMAIN = "lynk_cloud"
DEFAULT_HOST = "https://mylynkcloud.com"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)
PLATFORMS = ["sensor", "binary_sensor"]

CONF_HOST = "host"

