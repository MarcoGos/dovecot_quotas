"""Constants for the Dovecot quotas integration."""

NAME = "Dovecot Quotas"
DOMAIN = "dovecot_quotas"
MODEL = 'Quota'
MANUFACTURER = "Dovecot"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

DEFAULT_SYNC_INTERVAL = 3600  # seconds

CONF_HOSTNAME = "hostname"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

CONF_ACCOUNTS = "accounts"
