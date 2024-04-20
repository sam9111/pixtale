import json
import os
import vertexai

from vertexai.generative_models import GenerativeModel, Part, Image
import re

# Initialize Vertex AI
vertexai.init(project="pixtale-420019")


def describe_video(video_file_path):

    model = GenerativeModel("gemini-1.5-pro-preview-0409")

    prompt = """
    Provide a description of the video.
    The description should also contain anything important which people say in the video.
    """

    try:

        with open(video_file_path, "rb") as file:
            video_bytes = file.read()

        contents = [Part.from_data(video_bytes, "video/mp4"), prompt]

        response = model.generate_content(contents)

        return response.text

    except:

        return "Error getting description from Gemini"


def describe_image(image_path):

    model = GenerativeModel(model_name="gemini-pro-vision")

    try:
        image_content = Part.from_image(Image.load_from_file(image_path))

        response = model.generate_content(
            [
                image_content,
                """Describe the image.""",
            ]
        )

        return response.text

    except:
        return "Error getting description from Gemini"


def parse_json_from_gemini(json_str: str):

    try:
        # Remove potential leading/trailing whitespace
        json_str = json_str.strip()

        # Extract JSON content from triple backticks and "json" language specifier
        json_match = re.search(r"```json\s*(.*?)\s*```", json_str, re.DOTALL)

        if json_match:
            json_str = json_match.group(1)

        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        return None


def generate_descriptions(dir_path, mediaitems):

    video_extensions = (".mov", ".mp4", ".avi", ".flv", ".wmv")
    for item in mediaitems:

        if "description" in item and item["description"]:
            continue

        file_path = os.path.join(dir_path, item["filename"])

        if file_path.lower().endswith(video_extensions):

            item["description"] = describe_video(file_path)

        else:

            item["description"] = describe_image(file_path)

    mediaitems.sort(key=lambda item: item["datetime"])
    with open("./data/mediaitems.json", "w") as json_file:
        json.dump(mediaitems, json_file)

    return mediaitems


def get_script(mediaitems):
    model = GenerativeModel(model_name="gemini-1.5-pro-preview-0409")

    result = None
    while result is None:
        response = model.generate_content(
            """You excel at narrating short videos like Tiktok reels or Youtube shorts. You will be given a json list with objects. This list is a chronological list of photos and videos. Using the information about the place, datetime and description of the photo or video, come up with a short script to narrate the whole trip which can be used in a video merging all these photos and videos. If a particular media item has a missing datetime or place field, infer where it would fit in along with the context of the other items. Do not make any assumptions and strictly stick to describing the trip like a story in first person and past tense. Make the narration more continous and like a person describing the entire trip casually to their family and friends like a story. Include narration for every scene. Do not repeat any photo or video in the list. For videos ensure that the narration will not run over more than the video length given in duration field. Keep the sentences short for each scene and include all photos and videos. Output JSON only in the format like in the example below:
    \n{
  "title": "Our Grand Canyon Adventure",
  "description": "Join us on our unforgettable road trip to the Grand Canyon, as we explore stunning landscapes and experience the beauty of one of the world's natural wonders.",
  "scenes": [
    {
      "scene_number": 1,
      "media_type": "video",
      "media_source": "leaving_home.mp4",
      "text": "Hey everyone! We're hitting the road at the crack of dawn, super excited to start our adventure to the Grand Canyon. Everything's packed, and we're ready to go!"

    },
    {
      "scene_number": 2,
      "media_type": "photo",
      "media_source": "road_trip.jpg",
      "text": "Look at this view, folks! Miles of open road ahead of us. The landscapes are just stunning and the vibe in the car is just full of anticipation."
    },
    {
      "scene_number": 3,
      "media_type": "video",
      "media_source": "arriving_park.mp4",
      "text": "And we're here! Stepping into the Grand Canyon National Park now. I can't wait to show you all the incredible views we've been talking about."
    },
    {
      "scene_number": 4,
      "media_type": "photo",
      "media_source": "canyon_view.jpg",
      "text": "Here's our first stop. Just take in this breathtaking panorama of the canyon. The sheer size and beauty of it all is something you have to see to believe!"
    },
    {
      "scene_number": 5,
      "media_type": "video",
      "media_source": "sunset_watch.mp4",
      "text": "Nothing tops this, right? Watching the sunset over the Grand Canyon. The sky's turning into a canvas of oranges, pinks, and reds. It’s moments like these that make this trip unforgettable."
    },
    {
      "scene_number": 6,
      "media_type": "photo",
      "media_source": "campfire_night.jpg",
      "text": "Ending our day around the campfire, under the stars. Sharing stories, roasting marshmallows. It’s the perfect way to wrap up a perfect day. Thanks for joining us, and see you on the next adventure!"
    }
  ]
}
\nHere is the list: """
            + str(mediaitems)
        )
        result = parse_json_from_gemini(response.text)

        print(result)

        with open("data/mediaitems.json", "r") as file:
            mediaitems = json.load(file)

        for mediaitem in mediaitems:
            for script_item in result["scenes"]:
                if mediaitem["filename"] == script_item["media_source"]:

                    mediaitem["narration_text"] = script_item["text"]
                    mediaitem["scene_number"] = script_item["scene_number"]

        mediaitems.sort(key=lambda x: x["scene_number"])

        with open("./data/mediaitems.json", "w") as json_file:
            json.dump(mediaitems, json_file)

    return mediaitems


def synthesize_text(text, filename):
    """Synthesizes speech from the input string of text."""
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Journey-F",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open(filename + ".mp3", "wb") as out:
        out.write(response.audio_content)
        print("Audio content written to file " + filename)


def list_voices():
    """Lists the available voices."""
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()

    # Performs the list voices request
    voices = client.list_voices()

    english_voices = []

    for voice in voices.voices:

        for language_code in voice.language_codes:
            if "en" in language_code:

                english_voices.append(voice)

    return english_voices
