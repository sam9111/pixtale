from flask import Flask, render_template, request
import zipfile
import os
import json

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/result")
def get_video():

    with open("mediaitems.json", "r") as file:
        items = json.load(file)

    for item in items:
        item["filename"] = "public/" + item["filename"]
        type = item["filename"].split(".")[-1]

        if type.lower() in ["mp4", "mov"]:
            item["type"] = "video"
        else:
            item["type"] = "image"

    return render_template("result.html", items=items)


@app.route("/upload", methods=["POST"])
def get_mediaitems():
    if "zip_file" in request.files:
        zip_file = request.files["zip_file"]
        zip_file.save(
            "mediaitems.zip"
        )  # Save the uploaded zip file to a destination folder
        with zipfile.ZipFile("mediaitems.zip", "r") as zip_ref:
            zip_ref.extractall(
                "./mediaitems"
            )  # Extract the contents of the zip file to a destination folder
        return "File uploaded and extracted successfully"
    else:
        return "No zip file found in the request"


if __name__ == "__main__":
    app.run(debug=True)
