from flask import Flask, redirect, render_template, request, url_for
import zipfile
import os
import json
from preprocess import *
from ai_utils import *
from utils import *
import shutil

app = Flask(__name__)

public = "./static/public"


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/regenerate_description", methods=["POST"])
def regenerate_description():

    video_extensions = (".mov", ".mp4", ".avi", ".flv", ".wmv")

    item_filename = request.form.get("item_filename")

    print(item_filename)

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

    return redirect("/result")


@app.route("/result")
def get_video():

    with open("data/mediaitems.json", "r") as file:
        mediaitems = json.load(file)

    return render_template("result.html", mediaitems=mediaitems)


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
