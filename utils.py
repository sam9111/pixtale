import shutil
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    concatenate_audioclips,
    AudioFileClip,
)
from moviepy.video.fx.resize import resize
import os
from moviepy.video import fx as vfx
from moviepy.video.fx import speedx
from ai_utils import *

clips = []

# Define a standard resolution
standard_resolution = (1080, 1920)  # Width x Height


def create_video(mediaitems, dir_path):

    os.makedirs("./audio", exist_ok=True)

    audio_clips = []
    # Process each scene
    for i in range(len(mediaitems)):

        item = mediaitems[i]
        text = item["narration_text"]

        filepath = os.path.join(dir_path, item["filename"]).lower()

        if os.path.exists(filepath):

            if not os.path.exists("./audio/" + str(i) + ".mp3"):

                synthesize_text(text, "./audio/" + str(i))

            audio_clip = AudioFileClip("./audio/" + str(i) + ".mp3")

            duration = audio_clip.duration

            if filepath.endswith((".mp4", ".mov")):
                clip = VideoFileClip(filepath)

                if duration < clip.duration:

                    clip = clip.subclip(0, duration)

                clip = clip.resize(
                    newsize=(standard_resolution[0], standard_resolution[1])
                )

            else:
                clip = ImageClip(filepath).set_duration(duration)

            # txt_clip = (
            #     TextClip(
            #         scene["narration"]["text"],
            #         color="white",
            #         font="Arial",
            #         fontsize=50,
            #         method="caption",
            #         stroke_width=2,
            #     )
            #     .set_position("bottom")
            #     .set_duration(float(duration))
            # )
            # clip = CompositeVideoClip([clip, txt_clip])
            clips.append(clip)

            audio_clips.append(audio_clip)

    shutil.rmtree("./audio")

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips, method="compose")

    final_audio_clip = concatenate_audioclips(audio_clips)

    final_audio_path = os.path.join(dir_path, "result/final_audio.mp3")

    final_audio_clip.write_audiofile(final_audio_path)

    final_video_path = os.path.join(dir_path, "result/final_video.mp4")

    final_clip.write_videofile(final_video_path)

    combined_video_path = os.path.join(dir_path, "result/combined_video.mp4")

    if final_clip.duration != final_audio_clip.duration:

        if final_clip.duration > final_audio_clip.duration:
            # Speed up the video clip to match the audio clip's duration
            speed_factor = final_clip.duration / final_audio_clip.duration
            final_clip = final_clip.fx(vfx.speedx, speed_factor)

            # Write the result to a file

            new_video_path = os.path.join(dir_path, "result/speedup_video.mp4")

            final_clip.write_videofile(new_video_path)

            cmd = "ffmpeg -y -i {} -i {} -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac {}".format(
                new_video_path, final_audio_path, combined_video_path
            )
            os.system(cmd)

        else:
            # Speed up the audio clip to match the video clip's duration

            speed_factor = final_audio_clip.duration / final_clip.duration

            new_audio_path = os.path.join(dir_path, "result/speedup_audio.mp3")

            cmd = 'ffmpeg -y -i {} -filter:a "atempo={}" {}'.format(
                final_audio_path, speed_factor, new_audio_path
            )

            os.system(cmd)

            cmd = "ffmpeg -y -i {} -i {} -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac {}".format(
                final_video_path, new_audio_path, combined_video_path
            )
            os.system(cmd)

    else:

        cmd = (
            "ffmpeg -y -i {} -i {} -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac {}".format(
                final_video_path, final_audio_path, combined_video_path
            )
        )
        os.system(cmd)


def voices_list():

    return [
        {
            "language_codes": "en-AU",
            "ssml_gender": "FEMALE",
            "name": "en-AU-Neural2-A",
            "voice": "en-AU-Neural2-A-FEMALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "MALE",
            "name": "en-AU-Neural2-B",
            "voice": "en-AU-Neural2-B-MALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "FEMALE",
            "name": "en-AU-Neural2-C",
            "voice": "en-AU-Neural2-C-FEMALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "MALE",
            "name": "en-AU-Neural2-D",
            "voice": "en-AU-Neural2-D-MALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "FEMALE",
            "name": "en-AU-News-E",
            "voice": "en-AU-News-E-FEMALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "FEMALE",
            "name": "en-AU-News-F",
            "voice": "en-AU-News-F-FEMALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "MALE",
            "name": "en-AU-News-G",
            "voice": "en-AU-News-G-MALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "MALE",
            "name": "en-AU-Polyglot-1",
            "voice": "en-AU-Polyglot-1-MALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "FEMALE",
            "name": "en-AU-Standard-A",
            "voice": "en-AU-Standard-A-FEMALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "MALE",
            "name": "en-AU-Standard-B",
            "voice": "en-AU-Standard-B-MALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "FEMALE",
            "name": "en-AU-Standard-C",
            "voice": "en-AU-Standard-C-FEMALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "MALE",
            "name": "en-AU-Standard-D",
            "voice": "en-AU-Standard-D-MALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "FEMALE",
            "name": "en-AU-Wavenet-A",
            "voice": "en-AU-Wavenet-A-FEMALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "MALE",
            "name": "en-AU-Wavenet-B",
            "voice": "en-AU-Wavenet-B-MALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "FEMALE",
            "name": "en-AU-Wavenet-C",
            "voice": "en-AU-Wavenet-C-FEMALE",
        },
        {
            "language_codes": "en-AU",
            "ssml_gender": "MALE",
            "name": "en-AU-Wavenet-D",
            "voice": "en-AU-Wavenet-D-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-Neural2-A",
            "voice": "en-GB-Neural2-A-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-Neural2-B",
            "voice": "en-GB-Neural2-B-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-Neural2-C",
            "voice": "en-GB-Neural2-C-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-Neural2-D",
            "voice": "en-GB-Neural2-D-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-Neural2-F",
            "voice": "en-GB-Neural2-F-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-News-G",
            "voice": "en-GB-News-G-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-News-H",
            "voice": "en-GB-News-H-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-News-I",
            "voice": "en-GB-News-I-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-News-J",
            "voice": "en-GB-News-J-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-News-K",
            "voice": "en-GB-News-K-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-News-L",
            "voice": "en-GB-News-L-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-News-M",
            "voice": "en-GB-News-M-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-Standard-A",
            "voice": "en-GB-Standard-A-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-Standard-B",
            "voice": "en-GB-Standard-B-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-Standard-C",
            "voice": "en-GB-Standard-C-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-Standard-D",
            "voice": "en-GB-Standard-D-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-Standard-F",
            "voice": "en-GB-Standard-F-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-Studio-B",
            "voice": "en-GB-Studio-B-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-Studio-C",
            "voice": "en-GB-Studio-C-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-Wavenet-A",
            "voice": "en-GB-Wavenet-A-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-Wavenet-B",
            "voice": "en-GB-Wavenet-B-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-Wavenet-C",
            "voice": "en-GB-Wavenet-C-FEMALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "MALE",
            "name": "en-GB-Wavenet-D",
            "voice": "en-GB-Wavenet-D-MALE",
        },
        {
            "language_codes": "en-GB",
            "ssml_gender": "FEMALE",
            "name": "en-GB-Wavenet-F",
            "voice": "en-GB-Wavenet-F-FEMALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "FEMALE",
            "name": "en-IN-Neural2-A",
            "voice": "en-IN-Neural2-A-FEMALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "MALE",
            "name": "en-IN-Neural2-B",
            "voice": "en-IN-Neural2-B-MALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "MALE",
            "name": "en-IN-Neural2-C",
            "voice": "en-IN-Neural2-C-MALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "FEMALE",
            "name": "en-IN-Neural2-D",
            "voice": "en-IN-Neural2-D-FEMALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "FEMALE",
            "name": "en-IN-Standard-A",
            "voice": "en-IN-Standard-A-FEMALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "MALE",
            "name": "en-IN-Standard-B",
            "voice": "en-IN-Standard-B-MALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "MALE",
            "name": "en-IN-Standard-C",
            "voice": "en-IN-Standard-C-MALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "FEMALE",
            "name": "en-IN-Standard-D",
            "voice": "en-IN-Standard-D-FEMALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "FEMALE",
            "name": "en-IN-Wavenet-A",
            "voice": "en-IN-Wavenet-A-FEMALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "MALE",
            "name": "en-IN-Wavenet-B",
            "voice": "en-IN-Wavenet-B-MALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "MALE",
            "name": "en-IN-Wavenet-C",
            "voice": "en-IN-Wavenet-C-MALE",
        },
        {
            "language_codes": "en-IN",
            "ssml_gender": "FEMALE",
            "name": "en-IN-Wavenet-D",
            "voice": "en-IN-Wavenet-D-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Casual-K",
            "voice": "en-US-Casual-K-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Journey-D",
            "voice": "en-US-Journey-D-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Journey-F",
            "voice": "en-US-Journey-F-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Neural2-A",
            "voice": "en-US-Neural2-A-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Neural2-C",
            "voice": "en-US-Neural2-C-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Neural2-D",
            "voice": "en-US-Neural2-D-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Neural2-E",
            "voice": "en-US-Neural2-E-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Neural2-F",
            "voice": "en-US-Neural2-F-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Neural2-G",
            "voice": "en-US-Neural2-G-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Neural2-H",
            "voice": "en-US-Neural2-H-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Neural2-I",
            "voice": "en-US-Neural2-I-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Neural2-J",
            "voice": "en-US-Neural2-J-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-News-K",
            "voice": "en-US-News-K-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-News-L",
            "voice": "en-US-News-L-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-News-N",
            "voice": "en-US-News-N-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Polyglot-1",
            "voice": "en-US-Polyglot-1-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Standard-A",
            "voice": "en-US-Standard-A-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Standard-B",
            "voice": "en-US-Standard-B-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Standard-C",
            "voice": "en-US-Standard-C-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Standard-D",
            "voice": "en-US-Standard-D-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Standard-E",
            "voice": "en-US-Standard-E-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Standard-F",
            "voice": "en-US-Standard-F-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Standard-G",
            "voice": "en-US-Standard-G-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Standard-H",
            "voice": "en-US-Standard-H-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Standard-I",
            "voice": "en-US-Standard-I-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Standard-J",
            "voice": "en-US-Standard-J-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Studio-O",
            "voice": "en-US-Studio-O-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Studio-Q",
            "voice": "en-US-Studio-Q-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Wavenet-A",
            "voice": "en-US-Wavenet-A-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Wavenet-B",
            "voice": "en-US-Wavenet-B-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Wavenet-C",
            "voice": "en-US-Wavenet-C-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Wavenet-D",
            "voice": "en-US-Wavenet-D-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Wavenet-E",
            "voice": "en-US-Wavenet-E-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Wavenet-F",
            "voice": "en-US-Wavenet-F-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Wavenet-G",
            "voice": "en-US-Wavenet-G-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "FEMALE",
            "name": "en-US-Wavenet-H",
            "voice": "en-US-Wavenet-H-FEMALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Wavenet-I",
            "voice": "en-US-Wavenet-I-MALE",
        },
        {
            "language_codes": "en-US",
            "ssml_gender": "MALE",
            "name": "en-US-Wavenet-J",
            "voice": "en-US-Wavenet-J-MALE",
        },
    ]
