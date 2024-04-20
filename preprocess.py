from imagededup.methods import CNN
from datetime import datetime
from google.cloud import storage
import os
import os
import pandas as pd
import piexif
from geopy.geocoders import Nominatim
from PIL import Image
import random
import json
import pyexifinfo as pxi

from PIL import Image

from pillow_heif import register_heif_opener

register_heif_opener()


def extract_gps_from_video(video_path):
    metadata = pxi.get_json(video_path)

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

        return lat_decimal, lon_decimal
    except:

        print("No GPS Data on ", video_path)

        return None, None


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

    try:

        img = Image.open(image_path)

        exif_data = piexif.load(img.info["exif"])

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

        return gps_latitude_decimal, gps_longitude_decimal

    except:

        print("No GPS Data on ", image_path)

        return None, None


def get_place_name(latitude, longitude):

    geolocator = Nominatim(user_agent="exif_location")
    location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
    if location is None:
        return None
    else:
        return location.address


def update_places(mediaitems):

    for item in mediaitems:

        if item["latitude"] or item["longitude"]:
            item["place"] = get_place_name(item["latitude"], item["longitude"])

    with open("./data/mediaitems.json", "w") as json_file:
        json.dump(mediaitems, json_file)

    return mediaitems


def extract_datetime_video(video_path):

    try:

        metadata = pxi.get_json(video_path)

        datetime = (
            metadata[0]["QuickTime:CreateDate"]
            or metadata[0]["QuickTime:MediaCreateDate"]
        )

        return datetime

    except:

        return None


def extract_datetime_image(image_path):

    try:
        img = Image.open(image_path)

        exif_data = piexif.load(img.info["exif"])

        datetime = exif_data["Exif"][piexif.ExifIFD.DateTimeOriginal]

        return datetime

    except:

        return None


def extract_metadata(dir_path):

    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".heic")
    video_extensions = (".mov", ".mp4", ".avi", ".flv", ".wmv")

    remove_duplicates(dir_path)

    metadata_list = []
    for file in os.listdir(dir_path):

        file = file.lower()
        print("Processing {}".format(file))

        print("Extracting metadata from {}".format(file))

        if file.lower().endswith(video_extensions):
            type = "video"
            print("{} is a video file".format(file))
            video_path = os.path.join(dir_path, file)
            lat, lon = extract_gps_from_video(video_path)

            date_time = extract_datetime_video(video_path)

        elif file.lower().endswith(image_extensions):

            type = "image"

            image_path = os.path.join(dir_path, file)

            lat, lon = extract_gps_from_image(image_path)

            date_time = extract_datetime_image(image_path)

            if file.lower().endswith(".heic"):
                print("{} is a HEIC file".format(file))
                heic_path = os.path.join(dir_path, file)
                img = Image.open(heic_path)
                rgb_img = img.convert("RGB")

                jpeg_path = os.path.join(dir_path, file.replace(".heic", ".jpeg"))
                rgb_img.save(jpeg_path, "JPEG", quality=80)
                print("Saved {} to JPEG".format(file))
                file = file.replace(".heic", ".jpeg")

                os.remove(heic_path)
                print("Removed {} from directory".format(file))

        else:
            continue

        metadata = {
            "filename": file,
            "latitude": lat,
            "longitude": lon,
            "datetime": date_time,
            "type": type,
        }

        try:
            # Check if datetime is a binary string
            if isinstance(metadata["datetime"], bytes):
                # Decode the binary string and convert to datetime object
                metadata["datetime"] = datetime.strptime(
                    metadata["datetime"].decode(), "%Y:%m:%d %H:%M:%S"
                )
            elif isinstance(metadata["datetime"], str):
                # Convert string to datetime object
                metadata["datetime"] = datetime.strptime(
                    metadata["datetime"], "%Y:%m:%d %H:%M:%S"
                )

            else:
                metadata["datetime"] = datetime.min
        except ValueError:
            metadata["datetime"] = datetime.min
            print(f"Invalid date-time string: {date_time}")

        metadata_list.append(metadata)

    # Sort mediaitems by datetime
    metadata_list.sort(key=lambda item: item["datetime"])

    for item in metadata_list:
        item["datetime"] = item["datetime"].isoformat()

    with open("./data/mediaitems.json", "w") as json_file:
        json.dump(metadata_list, json_file)

    return metadata_list


# def remove_duplicates(dir_path, mediaitems):
#     cnn_encoder = CNN()
#     duplicates_list_cnn = cnn_encoder.find_duplicates_to_remove(image_dir=dir_path)

#     for item in mediaitems:

#         if item["filename"] in duplicates_list_cnn:

#             os.remove(os.path.join(dir_path, item["filename"]))
#             print("Deleted " + item["filename"])

#             mediaitems.remove(item)


def remove_duplicates(dir_path):

    # Create a set to keep track of unique filenames without extensions
    unique_filenames = set()

    # List all files in the directory and filter out heic images
    for filename in os.listdir(dir_path):
        if filename.lower().endswith(".heic"):
            # Add the filename without extension to the set
            unique_filenames.add(os.path.splitext(filename)[0])

    # Now, remove files that are not heic images but have the same name as those in the set
    for filename in os.listdir(dir_path):
        # Check if the filename without extension is in the set but the file is not a heic image
        if os.path.splitext(filename)[
            0
        ] in unique_filenames and not filename.lower().endswith(".heic"):
            # Remove the file
            os.remove(os.path.join(dir_path, filename))
            print(
                f"Deleted {filename} as it's not a HEIC image but has a duplicate name."
            )
