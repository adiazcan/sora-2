"""
SORA-2 Video Generator Library

This module provides functions to generate videos using the SORA-2 model
deployed in Azure AI Foundry. It supports both text-to-video and image-to-video
generation.
"""

import datetime
import os
import shutil
import time
from openai import OpenAI
from dotenv import load_dotenv


# Load environment variables
load_dotenv(".env")

# Initialize OpenAI client for Azure
api_key = os.getenv("AZURE_OPENAI_API_KEY")
client = OpenAI(
    base_url=f"{os.getenv('AZURE_OPENAI_ENDPOINT')}/openai/v1/",
    api_key=api_key,
    default_headers={"api-key": api_key}
)

# Video directory setup
VIDEO_DIR = "videos"

os.makedirs(VIDEO_DIR, exist_ok=True)

def text_to_video_sora2(prompt: str, size: str = "1280x720", seconds: int = 8) -> str:
    """
    Generate a video using the SORA-2 model deployed in Azure AI Foundry.

    This function sends a video generation request to the Azure AI Foundry client,
    polls for the job status until completion (or failure), and downloads the
    resulting video file locally.

    Args:
        prompt (str): A detailed text description of the video scene to generate.
                      Example: "A professional two-person interview about Microsoft Azure..."
        size (str, optional): The resolution of the output video. Defaults to "1280x720".
                              Supported values: "1280x720" (landscape) or "720x1280" (portrait).
        seconds (int, optional): Duration of the generated video in seconds.
                                 Supported values: 4, 8, or 12. Defaults to 8.

    Returns:
        str: The local file path of the downloaded video if generation succeeds.
        bool: False if the generation fails or is cancelled.
    """
    start = time.time()

    # Create video with custom parameters
    print(f"===== 🎨 Creating SORA-2 video using Azure AI Foundry =====\n")
    print(f"Prompt: {prompt}")

    try:
        video = client.videos.create(
            model="sora-2",  # The name of your sora2 deployed model in Azure AI Foundry
            prompt=prompt,  # text prompt
            size=size,  # 1280x720 or 720x1280
            seconds=seconds  # 4 or 8 or 12 seconds
        )

        print(f"📹 Video ID: {video.id}")
        print(f"⏳ Initial Status: {video.status}\n")

        # Poll for completion
        while video.status not in ["completed", "failed", "cancelled"]:
            now = datetime.datetime.now().strftime('%d-%b-%Y %H:%M:%S')
            print(f"[{now}] ⏱️ Status: {video.status}")
            time.sleep(10)  # Pause
            video = client.videos.retrieve(video.id)

        # Handle final status
        if video.status == "completed":
            print("\n✨ Video generation completed!")
            print("📥 Downloading video")
            content = client.videos.download_content(video.id, variant="video")
            sora2_videofile = os.path.join(
                VIDEO_DIR,
                f"sora2_video_{datetime.datetime.now().strftime('%d%b%Y_%H%M%S')}.mp4"
            )
            content.write_to_file(sora2_videofile)
            minutes, seconds = divmod((time.time() - start), 60)
            print(f"⏱️ Done in {minutes:.0f} minutes and {seconds:.0f} seconds")
            print(f"\n✅ Video saved to: {sora2_videofile}")
            return sora2_videofile

        elif video.status == "failed":
            print("\n❌ Video generation failed!")
            return False

        elif video.status == "cancelled":
            print("\n⚠️ Video generation was cancelled")
            return False

    except Exception as e:
        print(f"\n🚨 Error occurred: {str(e)}")
        return False


def image_to_video_sora2(prompt: str, image_file: str, size: str = "1280x720", seconds: int = 8) -> str:
    """
    Generate a video from an image using the SORA-2 model via Azure AI Foundry.

    This function takes a text prompt and an input image, then uses the SORA-2 video generation
    model to create a video clip. The process includes polling the job status until completion
    and saving the resulting video file locally.

    Args:
        prompt (str): The text description guiding the video generation.
        image_file (str): Path to the input image file (JPEG, PNG, etc.).
        size (str, optional): Output video resolution in "WIDTHxHEIGHT" format. Defaults to "1280x720".
        seconds (int, optional): Duration of the generated video in seconds. Defaults to 8.

    Returns:
        str: The local file path of the generated video if successful.
        bool: Returns False if the generation fails or is cancelled.

    Raises:
        Exception: Captures and logs any unexpected errors during the process.
    """
    start = time.time()

    print(f"===== 🎨 Creating SORA-2 video using Azure AI Foundry =====\n")
    print(f"Input image: {image_file}")
    print(f"Prompt: {prompt}")

    try:
        with open(image_file, "rb") as image_file:
            video = client.videos.create(
                model="sora-2",
                prompt=prompt,
                input_reference=image_file,
                size=size,
                seconds=seconds,
            )

        print(f"📹 Video ID: {video.id}")
        print(f"⏳ Initial Status: {video.status}\n")

        while video.status not in ["completed", "failed", "cancelled"]:
            now = datetime.datetime.now().strftime('%d-%b-%Y %H:%M:%S')
            print(f"[{now}] ⏱️ Status: {video.status}")
            time.sleep(10)
            video = client.videos.retrieve(video.id)

        if video.status == "completed":
            content = client.videos.download_content(video.id, variant="video")

            sora2_videofile = os.path.join(
                VIDEO_DIR,
                f"sora2_video_{datetime.datetime.now().strftime('%d%b%Y_%H%M%S')}.mp4"
            )
            content.write_to_file(sora2_videofile)
            minutes, seconds = divmod((time.time() - start), 60)
            print(f"⏱️ Done in {minutes:.0f} minutes and {seconds:.0f} seconds")
            print(f"\n✅ Video saved to: {sora2_videofile}")
            return sora2_videofile

        elif video.status == "failed":
            print("\n❌ Video generation failed!")
            return False

        elif video.status == "cancelled":
            print("\n⚠️ Video generation was cancelled")
            return False

    except Exception as e:
        print(f"\n🚨 Error occurred: {str(e)}")
        return False
