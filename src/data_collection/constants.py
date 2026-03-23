# CONSTANTS

import json
from os import environ
from pathlib import Path

project_src = Path(__file__, "..").resolve()

# ------------------------------------------------------------------------
# KVG stop-id mapping
_kvg_mapping_filepath = project_src / "mapping_kvg.json"

kvg_stop_mapping = json.load(open(_kvg_mapping_filepath))

# ------------------------------------------------------------------------
# KVG URL definitions
kvg_base_url = "https://kvg-internetservice-proxy.p.networkteam.com"

# Services
_services_path = "/internetservice/services"
kvg_stop_url = kvg_base_url + _services_path + "/passageInfo/stopPassages/stop"
kvg_platform_url = kvg_base_url + _services_path + "/passageInfo/stopPassages/stopPoint"
kvg_trip_url = kvg_base_url + _services_path + "/tripInfo/tripPassages"

# Geoservices
_geoservice_path = "/internetservice/geoserviceDispatcher"
kvg_tripPath_url = kvg_base_url + _geoservice_path + "/services/pathinfo/trip"
kvg_vehicles_url = kvg_base_url + _geoservice_path + "/services/vehicleinfo/vehicles"
kvg_stops_url = kvg_base_url + _geoservice_path + "/services/stopinfo/stops"
kvg_platforms_url = kvg_base_url + _geoservice_path + "/services/stopinfo/stopPoints"

# ------------------------------------------------------------------------
# Fetching Loop Variables

FECTH_DELAY = int(environ.get("DC__FECTH__DELAY", default=5))
