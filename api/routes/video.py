from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import fal_client
import tempfile
import os

from core.schemas import TextToVideoRequest

router = APIRouter()

@router.post("/generate-video-from-text")
async def generate_video_from_text(
    request: TextToVideoRequest,
):
    try:
        print(f"Generating video with prompt: {request.prompt}")
        print(f"Parameters: aspect_ratio={request.aspect_ratio}, duration={request.duration}, resolution={request.resolution}")

        arguments = {
            k: v for k, v in {
                "prompt": request.prompt,
                "aspect_ratio": request.aspect_ratio if request.aspect_ratio != "16:9" else None,
                "duration": request.duration if request.duration != "8s" else None,
                "negative_prompt": request.negative_prompt,
                "enhance_prompt": request.enhance_prompt if request.enhance_prompt != True else None,
                "seed": request.seed,
                "resolution": request.resolution if request.resolution != "720p" else None,
                "generate_audio": request.generate_audio if request.generate_audio != True else None,
            }.items() if v is not None
        }

        print(f"Fal AI video arguments: {arguments}")

        handler = await fal_client.submit_async(
            request.model,
            arguments=arguments,
        )
        output = await handler.get()

        print(f"Raw output from Fal (type={type(output)}): {repr(output)}")
        
        video_url = None

        if isinstance(output, dict):
            if "video" in output and isinstance(output["video"], dict):
                if "url" in output["video"]:
                    video_url = output["video"]["url"]
                    print(f"Found video URL in nested structure: {video_url}")

        if not video_url:
            raise HTTPException(
                status_code=500,
                detail="No video URL found in response from the video generation service",
            )

        print(f"Successfully generated video URL: {video_url}")
        return JSONResponse(content={"video_url": video_url})

    except Exception as e:
        print(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-video-from-image")
async def generate_video_from_image(
    image: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
):
    try:
        contents = await image.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name

        try:
            print(f"Uploading image to Fal: {temp_file_path}")
            image_url = fal_client.upload_file(temp_file_path)
            print(f"Uploaded image URL: {image_url}")

            handler = await fal_client.submit_async(
                "fal-ai/kling-video/v2.1/master/image-to-video",
                arguments={
                    "prompt": prompt,
                    "image_url": image_url,
                },
            )
            output = await handler.get()

            print(f"Raw output from Fal (type={type(output)}): {repr(output)}")
            print(
                f"Output keys: {list(output.keys()) if isinstance(output, dict) else 'Not a dict'}"
            )

            video_url = None

            if isinstance(output, dict):
                if "video" in output and isinstance(output["video"], dict):
                    if "url" in output["video"]:
                        video_url = output["video"]["url"]
                        print(f"Found video URL in nested structure: {video_url}")

            if not video_url:
                raise HTTPException(status_code=500, detail="No video URL in response")

            print(f"Successfully extracted video URL: {video_url}")
            return JSONResponse(content={"video_url": video_url})

        except Exception as fal_error:
            print(f"Fal API error: {fal_error}")

            error_str = str(fal_error)

            if (
                "image_too_small" in error_str
                or "Image dimensions are too small" in error_str
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Image is too small for video generation. Please upload an image that is at least 300x300 pixels.",
                )
            elif "image_too_large" in error_str:
                raise HTTPException(
                    status_code=400,
                    detail="Image is too large. Please upload a smaller image.",
                )
            elif "unsupported_format" in error_str or "invalid_image" in error_str:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported image format. Please upload a JPEG, PNG, or WebP image.",
                )
            else:
                raise fal_error

        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        print(f"Image to video generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
