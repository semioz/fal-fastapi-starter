import os
import tempfile

import fal_client
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse

from core.schemas import ImageToVideoRequest, TextToVideoRequest
from core.utils import handle_fal_error

router = APIRouter()


@router.post("/generate-video-from-text")
async def generate_video_from_text(
    request: TextToVideoRequest,
):
    try:
        print(f"Generating video with prompt: {request.prompt}")
        print(f"Using model: {request.model}")

        arguments = {
            k: v
            for k, v in {
                "model": request.model,
                "prompt": request.prompt,
                "aspect_ratio": request.aspect_ratio,
                "duration": request.duration,
                "negative_prompt": request.negative_prompt,
                "enhance_prompt": request.enhance_prompt,
                "seed": request.seed,
                "resolution": request.resolution,
                "generate_audio": request.generate_audio,
            }.items()
            if v is not None
        }

        print(f"Fal AI video arguments: {arguments}")

        handler = await fal_client.submit_async(
            request.model,
            arguments=arguments,
        )
        output = await handler.get()

        print(f"Raw output from Fal (type={type(output)}): {repr(output)}")

        video_url = None
        video_data = output.get("video")
        if isinstance(video_data, dict):
            video_url = video_data.get("url")
            if video_url:
                print(f"Found video URL: {video_url}")

        if not video_url:
            raise HTTPException(
                status_code=500,
                detail="No video URL found in response from the FAL API!",
            )

        return JSONResponse(content={"video_url": video_url})

    except HTTPException:
        raise
    except Exception as e:
        print(f"Video generation error: {str(e)}")
        raise handle_fal_error(e)


@router.post("/generate-video-from-image")
async def generate_video_from_image(
    data: ImageToVideoRequest = Form(),
):
    try:
        contents = await data.image.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name

        print(f"Uploading image to Fal: {temp_file_path}")
        image_url = fal_client.upload_file(temp_file_path)
        print(f"Uploaded image URL: {image_url}")

        arguments = {
            k: v
            for k, v in {
                "prompt": data.prompt,
                "image_url": image_url,
                "duration": data.duration,
                "prompt_optimizer": data.prompt_optimizer,
            }.items()
            if v is not None
        }

        print(f"Fal AI image-to-video arguments: {arguments}")

        handler = await fal_client.submit_async(
            "fal-ai/kling-video/v2.1/master/image-to-video",
            arguments=arguments,
        )
        output = await handler.get()

        print(f"Raw output from Fal (type={type(output)}): {repr(output)}")

        video_url = None
        if "video" in output and isinstance(output["video"], dict):
            video_url = output["video"]["url"]

        if not video_url:
            raise HTTPException(status_code=500, detail="No video URL in response")

        print(f"Successfully extracted video URL: {video_url}")
        return JSONResponse(content={"video_url": video_url})

    except HTTPException:
        raise
    except Exception as e:
        print(f"Image to video generation error: {str(e)}")
        raise handle_fal_error(e)
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
