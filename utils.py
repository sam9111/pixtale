import os
from utils import *
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


def get_audio_duration(filepath):
    """Get the duration of an audio file using ffprobe with os.system."""
    # Temporary file to store the output of ffprobe
    temp_file = "temp_duration.txt"
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filepath} > {temp_file}"
    os.system(cmd)

    # Read the duration from the temporary file
    with open(temp_file, "r") as file:
        duration = file.read().strip()

    # Remove the temporary file
    os.remove(temp_file)

    try:
        return float(duration)
    except ValueError:
        return None


def create_video(mediaitems, dir_path, global_voice):

    print("global voice", global_voice)
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".heic")
    video_extensions = (".mov", ".mp4", ".avi", ".flv", ".wmv")
    # Ensure the result directory exists
    result_dir = os.path.join(dir_path, "result")

    print("result directory: ", result_dir)

    os.makedirs(result_dir, exist_ok=True)

    audio_dir = os.path.join(dir_path, "result/audio")

    os.makedirs(audio_dir, exist_ok=True)

    # File to store list of files to concatenate

    filelist_path = os.path.join(result_dir, "filelist.txt")
    audio_clips = []
    video_clips = []
    with open(filelist_path, "w+") as filelist:
        for i, item in enumerate(mediaitems):
            filepath = os.path.join(dir_path, item["filename"]).lower()

            print("file: ", filepath)

            audio_path = os.path.join(audio_dir, str(i) + ".mp3")

            synthesize_text(
                item["narration_text"],
                os.path.join(audio_dir, str(i)),
                language_code=global_voice["language_codes"],
                name=global_voice["name"],
                gender=global_voice["ssml_gender"],
            )

            audio_duration = get_audio_duration(audio_path)
            audio_clip = AudioFileClip(audio_path)
            audio_clips.append(audio_clip)

            if filepath.lower().endswith(image_extensions):
                # Convert image to video clip
                video_clip_path = os.path.join(result_dir, f"clip_{i}.mp4")
                cmd = f'ffmpeg -y -loop 1 -i {filepath} -c:v libx264 -t {audio_duration} -pix_fmt yuv420p -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" {video_clip_path}'
                os.system(cmd)
            elif filepath.lower().endswith(video_extensions):
                # Ensure video clip is of the correct format and resolution
                video_clip_path = os.path.join(result_dir, f"clip_{i}.mp4")

                cmd = f"ffmpeg -y -i {filepath} -c:v libx264 -t {audio_duration} -pix_fmt yuv420p -vf scale=1080:1920 {video_clip_path}"
                os.system(cmd)

            output_clip_path = os.path.join(result_dir, f"output_clip_{i}.mp4")
            cmd = f"ffmpeg -y -i {video_clip_path} -i {audio_path} -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac {output_clip_path}"
            os.system(cmd)
            filelist.write(f"file 'output_clip_{i}.mp4'\n")
            video_clips.append(VideoFileClip(output_clip_path))

    concatenate_videoclips(video_clips).write_videofile(
        os.path.join(result_dir, "final_video.mp4")
    )


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
