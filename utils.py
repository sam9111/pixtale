import os

import pandas as pd
import piexif
from geopy.geocoders import Nominatim
from PIL import Image


import pyexifinfo as pxi

from PIL import Image

from pillow_heif import register_heif_opener

register_heif_opener()

# Define the directory containing the image files
dir_path = "data/2023"


def extract_gps_from_video(video_path):
    metadata = pxi.get_json(video_path)

    datetime = metadata[0]["QuickTime:MediaCreateDate"]

    try:

        coordinates = metadata[0]["QuickTime:GPSCoordinates"]
        lat, lon, _ = coordinates.split(", ")

        # Remove the 'deg' and other non-numeric characters from the latitude and longitude
        lat = lat.replace(" deg", "").replace("'", "").replace('" N', "")
        lon = lon.replace(" deg", "").replace("'", "").replace('" E', "")

        # Split the latitude and longitude into degrees, minutes, and seconds
        lat_deg, lat_min, lat_sec = map(float, lat.split(" "))
        lon_deg, lon_min, lon_sec = map(float, lon.split(" "))

        # Convert the latitude and longitude to decimal format
        lat_decimal = lat_deg + lat_min / 60 + lat_sec / 3600
        lon_decimal = lon_deg + lon_min / 60 + lon_sec / 3600

        return lat_decimal, lon_decimal, datetime
    except:

        print("No GPS Data on ", video_path)

        return None, None, datetime


def gps_to_decimal(coord, ref):

    decimal = (
        coord[0][0] / coord[0][1]
        + coord[1][0] / (60 * coord[1][1])
        + coord[2][0] / (3600 * coord[2][1])
    )
    if ref in ["S", "W"]:
        decimal *= -1
    return decimal


def extract_gps_from_image(image_path):

    img = Image.open(image_path)

    exif_data = piexif.load(img.info["exif"])

    datetime = exif_data["Exif"][piexif.ExifIFD.DateTimeOriginal]

    try:

        # Extract GPS latitude, longitude, and altitude data
        gps_latitude = exif_data["GPS"][piexif.GPSIFD.GPSLatitude]
        gps_latitude_ref = exif_data["GPS"][piexif.GPSIFD.GPSLatitudeRef]
        gps_longitude = exif_data["GPS"][piexif.GPSIFD.GPSLongitude]
        gps_longitude_ref = exif_data["GPS"][piexif.GPSIFD.GPSLongitudeRef]
        gps_altitude = exif_data["GPS"][piexif.GPSIFD.GPSAltitude]
        gps_altitude_ref = exif_data["GPS"][piexif.GPSIFD.GPSAltitudeRef]

        # Convert GPS latitude and longitude data to decimal degrees
        gps_latitude_decimal = gps_to_decimal(gps_latitude, gps_latitude_ref)
        gps_longitude_decimal = gps_to_decimal(gps_longitude, gps_longitude_ref)

        return gps_latitude_decimal, gps_longitude_decimal, datetime

    except:

        print("No GPS Data on ", image_path)

        return None, None, datetime


def get_place_name(latitude, longitude):

    geolocator = Nominatim(user_agent="exif_location")
    location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
    if location is None:
        return None
    else:
        return location.address


def extract_metadata(dir_path):

    metadata_list = []
    for file in os.listdir(dir_path):
        print("[+] Processing {}".format(file))

        print("[+] Extracting metadata from {}".format(file))

        if file.lower().endswith((".mov", ".mp4", ".avi", ".flv", ".wmv")):
            print("[+] {} is a video file".format(file))
            video_path = os.path.join(dir_path, file)
            lat, lon, datetime = extract_gps_from_video(video_path)

        else:

            image_path = os.path.join(dir_path, file)

            lat, lon, datetime = extract_gps_from_image(image_path)

        place_name = ""
        if lat or lon is not None:

            place_name = get_place_name(lat, lon)

        metadata = {
            "filename": file,
            "place_name": place_name,
            "datetime": str(datetime),
        }

        metadata_list.append(metadata)

    # Convert the metadata list to a pandas dataframe
    metadata_df = pd.DataFrame(metadata_list)

    return metadata_df


# Extract the metadata from the image files
metadata_df = extract_metadata(dir_path)

# Convert the DataFrame to JSON
mediaitems = metadata_df.to_json(orient="records")

mediaitems
with open("mediaitems.json", "w") as json_file:
    json_file.write(mediaitems)
