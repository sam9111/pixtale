from flask import Flask, redirect, render_template, request, url_for
import zipfile
import os
import json
from preprocess import *
from ai_utils import *
from utils import *
import shutil
from dotenv import load_dotenv
from time import time

# Load environment variables from a .env file
load_dotenv()


app = Flask(__name__)

public = "./static/public"

google_api_key = os.environ.get("GOOGLE_MAPS_KEY")


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/save", methods=["POST"])
def save_mediaitems():

    with open("data/mediaitems.json", "r") as file:
        mediaitems = json.load(file)

    item_filename = request.form.get("filename")
    for item in mediaitems:

        if item["filename"] == item_filename:

            item["date"] = request.form.get("date")
            item["time"] = request.form.get("time")
            item["place"] = request.form.get("place")
            item["description"] = request.form.get("description")
            item["narration_text"] = request.form.get("narration_text")

    # Write the updated mediaitems back to the JSON file
    with open("data/mediaitems.json", "w") as file:
        json.dump(mediaitems, file, indent=4)

    return redirect(url_for("get_video"))


@app.route("/regenerate_description", methods=["POST"])
def regenerate_description():

    print("regenerate_description")

    video_extensions = (".mov", ".mp4", ".avi", ".flv", ".wmv")

    item_filename = request.json.get("filename")

    with open("data/mediaitems.json", "r") as file:
        mediaitems = json.load(file)

    # Update the item in the mediaitems.json file
    for item in mediaitems:
        if item["filename"] == item_filename:

            file_path = os.path.join(public, item_filename)

            if file_path.lower().endswith(video_extensions):

                item["description"] = describe_video(file_path)

            else:

                item["description"] = describe_image(file_path)

            print(item["description"])

            break

    # Write the updated mediaitems back to the JSON file
    with open("data/mediaitems.json", "w") as file:
        json.dump(mediaitems, file, indent=4)

    return "Regeneration success"


@app.route("/result")
def get_video():

    with open("data/script.json", "r") as file:
        script = json.load(file)

    title = script["title"]
    caption = script["caption"]
    hashtags = " ".join(script["hashtags"])

    with open("data/mediaitems.json", "r") as file:
        mediaitems = json.load(file)

    audio_file = (
        "speedup_audio.mp3"
        if os.path.exists(os.path.join(public, "result", "speedup_audio.mp3"))
        else "final_audio.mp3"
    )

    return render_template(
        "result.html",
        mediaitems=mediaitems,
        google_api_key=google_api_key,
        audio_file=audio_file,
        voices_list=voices_list(),
        title=title,
        caption=caption,
        hashtags=hashtags,
    )


@app.route("/upload", methods=["POST"])
def generate_video():

    try:

        zip_file = request.files["zip_file"]
        zip_file.save(
            "./data/mediaitems.zip"
        )  # Save the uploaded zip file to a destination folder

        if os.path.exists(public):
            print(f"Removing existing directory: {public}")
            shutil.rmtree(public)
            print(f"Creating directory: {public}")
            os.makedirs(public)

        with zipfile.ZipFile("./data/mediaitems.zip", "r") as zip_ref:
            for member in zip_ref.infolist():
                # Check if the member is a file and not a directory
                if not member.is_dir() and not member.filename.startswith("__MACOSX/"):
                    # Extract the file to data_dir with the same name
                    zip_ref.extract(member, public)
                    # Move the file to the root of public if it was in a subfolder
                    source_path = os.path.join(public, member.filename)
                    target_path = os.path.join(
                        public, os.path.basename(member.filename)
                    )
                    shutil.move(source_path, target_path)

        for root, dirs, files in os.walk(public):
            for name in files:
                if name.startswith(".") or not os.path.isfile(os.path.join(root, name)):
                    os.remove(os.path.join(root, name))
            if not os.listdir(root):
                os.rmdir(root)

        mediaitems = extract_metadata(public)

        mediaitems = update_places(mediaitems)

        mediaitems = generate_descriptions(public, mediaitems)

        mediaitems = get_script(mediaitems)

        with open("data/mediaitems.json", "r") as file:
            mediaitems = json.load(file)

        os.makedirs(os.path.join(public, "result"), exist_ok=True)

        create_video(mediaitems, public)

        return redirect("/result")

    except Exception as e:

        return render_template("index.html", error=e)


if __name__ == "__main__":
    app.run(debug=True)
