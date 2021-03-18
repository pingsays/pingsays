import requests
import pprint
import smtplib
from email.message import EmailMessage
import os
import time
import datetime

def main():
    #=====================#
    # declaring variables #
    #=====================#
    EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    EMAIL_TO = []

    pp = pprint.PrettyPrinter(indent=2)

    # use this link and enter your zipcode: https://vaccinefinder.nyc.gov/locations
    # use chrome devtools to grab the url for the api call
    # save the api uri in the variable url
    url = "https://services1.arcgis.com/oOUgp466Coyjcu6V/arcgis/rest/services/VaccineFinder_Production_View/FeatureServer/0/query?f=json&cacheHint=true&orderByFields=FacilityName%2CAddress&outFields=*&outSR=4326&returnGeometry=false&spatialRel=esriSpatialRelIntersects&where=AppointmentAvailability%20%3D%20%27Available%27"
    resp = requests.get(url).json()
    stores = resp["features"]

    filters = {
        "AgesServed": "",
        "Borough": "Queens",
        "AppointmentAvailability": "Available",
        "ServiceType_JohnsonAndJohnson": "No",
        "FacilityName": "Mass Vaccination Site - Citi Field"
    }

    # adhoc filter
    exclude_facilities = ["NYS-FEMA York College"]

    # {output_friendly_name: actual_key_from_api}
    output = {
        "FacilityName": "FacilityName",
        "FacilityType": "FacilityType",
        "Borough": "Borough",
        "Address": "Address",
        "Vaccine": "ServiceType",
        "  - Moderna": "ServiceType_Moderna",
        "  - Pfizer": "ServiceType_Pfizer",
        "  - JohnsonAndJohnson": "ServiceType_JohnsonAndJohnson",
        "Restrictions": "Vaccine_Restrictions",
        "Additional Info": "AdditionalInfo",
        "Website": "Website"
        # "Monday": "Hours_Monday",
        # "Tuesday": "Hours_Tuesday",
        # "Wednesday": "Hours_Wednesday",
        # "Thursday": "Hours_Thursday",
        # "Friday": "Hours_Friday",
        # "Saturday": "Hours_Saturday",
        # "Sunday": "Hours_Sunday",
    }

    store_matches = []
    msg_body = ""
    for store in stores:
        exact_match = 0
        store_data = store.get("attributes")

        # exclude facilities
        if store_data.get("FacilityName") in exclude_facilities:
            continue

        # filter
        for key, value in filters.items():
            if store_data[key] == filters[key]:
                continue
            else:
                exact_match += 1

        if exact_match == 0:
            store_matches.append(store_data)

    pp.pprint(store_matches)
    print(f"Number of Stores: {len(store_matches)}")
    print("=" * 200)

    if len(store_matches) > 0:
        for store in store_matches:
            for key, value in output.items():
                print(f"{key}: {store.get(value)}")
                msg_body += f"{key}: {store.get(value)}\n"
            print("-" * 200)
            msg_body += f"{'-' * 200}\n"

        #==============#
        # email config #
        #==============#
        msg = EmailMessage()
        msg['Subject'] = f'Covid-19 Vaccine'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_TO

        msg.add_alternative(f"""\
        <!DOCTYPE html>
        <html>
            <body>
                <pre style="font-family: sans-serif;">
{msg_body}
                </pre>
            </body>
        </html>
        """, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

if __name__ == '__main__':
    counter = 1
    while True:
        print(f"Run #{counter}")
        print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
        main()
        counter += 1
        time.sleep(600)
