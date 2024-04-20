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
