import json
import time
import requests
from dataclasses import dataclass
from validate_email import validate_email
import phonenumbers
from geopy.geocoders import Nominatim
from meshapi.exceptions import AddressError, AddressAPIError
from meshapi.zips import NYCZipCodes
from meshdb.utils.spreadsheet_import.building.constants import INVALID_BIN_NUMBERS
from meshdb.utils.spreadsheet_import.building.pelias import humanify_street_address


def validate_email_address(email_address):
    return validate_email(
        email_address=email_address,
        check_format=True,
        check_blacklist=True,
        check_dns=True,
        dns_timeout=5,
        check_smtp=False,
    )


# Expects country code!!!!
def validate_phone_number(phone_number):
    try:
        parsed = phonenumbers.parse(phone_number, None)
        if not phonenumbers.is_possible_number(parsed):
            return False
    except phonenumbers.NumberParseException:
        return False
    return True


# Used to obtain info about addresses within NYC. Uses a pair of APIs
# hosted by the city with all kinds of good info. Unfortunately, there's
# not a solid way to check if an address is actually _within_ NYC, so this
# is gated by OSMAddressInfo.
@dataclass
class NYCAddressInfo:
    street_address: str
    city: str
    state: str
    zip: int
    longitude: float
    latitude: float
    altitude: float
    bin: int | None

    def __init__(self, street_address: str, city: str, state: str, zip: int):
        if state != "New York" and state != "NY":
            raise ValueError(f"(NYC) State '{state}' is not New York.")

        self.address = f"{street_address}, {city}, {state} {zip}"

        try:
            # Look up BIN in NYC Planning's Authoritative Search
            # This one always returns a "best effort" search
            query_params = {
                "text": self.address,
                "size": 1,
            }
            nyc_planning_req = requests.get(f"https://geosearch.planninglabs.nyc/v2/search", params=query_params)
            nyc_planning_resp = json.loads(nyc_planning_req.content.decode("utf-8"))
        except Exception as e:
            print(f"Got exception querying geosearch.planninglabs.nyc: {e}")
            raise AddressAPIError

        if len(nyc_planning_resp["features"]) == 0:
            raise AddressError(f"(NYC) Address '{self.address}' not found in geosearch.planninglabs.nyc.")

        # If we enter something not within NYC, the API will still give us
        # the closest matching street address it can find, so check that
        # the ZIP of what we entered matches what we got.

        # FIXME (willnilges): Found an edge case where if you enter an address
        # that's not in the Zip code, it will print the "not within city limits"
        # error. Either the error message needs to be re-worked, or additional
        # validation is required to figure out exactly what is wrong.
        found_zip = int(nyc_planning_resp["features"][0]["properties"]["postalcode"])
        if found_zip != zip:
            raise AddressError(
                f"(NYC) Could not find address '{street_address}, {city}, {state} {zip}'. Zip code ({zip}) is probably not within city limits"
            )

        addr_props = nyc_planning_resp["features"][0]["properties"]

        # Get the rest of the address info
        self.street_address = humanify_street_address(f"{addr_props['housenumber']} {addr_props['street']}")

        self.city = addr_props["borough"].replace("Manhattan", "New York")
        self.state = addr_props["region_a"]
        self.zip = int(addr_props["postalcode"])

        # TODO (willnilges): Bail if no BIN. Given that we're guaranteeing this is NYC, if
        # there is no BIN, then we've really foweled something up
        self.bin = addr_props["addendum"]["pad"]["bin"]
        if int(self.bin) in INVALID_BIN_NUMBERS:
            raise AddressAPIError
        self.longitude, self.latitude = nyc_planning_resp["features"][0]["geometry"]["coordinates"]

        # Now that we have the bin, we can definitively get the height from
        # NYC OpenData
        query_params = {
            "$where": f"bin={self.bin}",
            "$select": "heightroof,groundelev",
            "$limit": 1,
        }
        nyc_dataset_req = requests.get(f"https://data.cityofnewyork.us/resource/qb5r-6dgf.json", params=query_params)
        nyc_dataset_resp = json.loads(nyc_dataset_req.content.decode("utf-8"))

        if len(nyc_dataset_resp) == 0:
            raise AddressAPIError(
                f"(NYC) DOB BIN ({self.bin}) not found in NYC OpenData while trying to query for altitude information"
            )

        self.altitude = float(nyc_dataset_resp[0]["heightroof"]) + float(nyc_dataset_resp[0]["groundelev"])
