"""Konstanter för Friidrottskollen."""
from datetime import timedelta

DOMAIN = "friidrottskollen"
CONF_ATHLETE = "atlet"
DEFAULT_ATHLETE = "Daniel Ståhl"

KOLLEN_URL = "https://www.friidrott.se/tavling-landslag/elit-landslag/friidrottskollen-vem-tavlar-nar-och-var/"
TV_URL = "https://www.friidrott.se/tavling-landslag/friidrott-pa-tv/tv-tabla/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Home Assistant Friidrottskollen)"}

SCAN_INTERVAL = timedelta(hours=2)
