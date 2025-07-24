from typing import Annotated

from fastapi import File, UploadFile
from pydantic import BaseModel, Field


class TextToVideoRequest(BaseModel):
    prompt: str
    model: str | None = Field("fal-ai/minimax/hailuo-02/standard/text-to-video")
    aspect_ratio: str | None = Field(
        "16:9", description="Aspect ratio of the video (16:9, 9:16, 1:1)"
    )
    duration: str | None = Field("8s")
    negative_prompt: str | None = Field(
        None, description="A negative prompt to guide the video generation"
    )
    enhance_prompt: bool | None = Field(
        True, description="Whether to enhance the video generation"
    )
    seed: int | None = Field(None, description="A seed to use for the video generation")
    resolution: str | None = Field(
        "720p", description="Resolution of the video (720p, 1080p)"
    )
    generate_audio: bool | None = Field(True)


class GenerateImageRequest(BaseModel):
    prompt: str
    negative_prompt: str | None = Field(
        "", description="A description of what to discourage in the generated images"
    )
    aspect_ratio: str | None = Field(
        "1:1", description="The aspect ratio of the generated image"
    )
    num_images: int | None = Field(
        1, ge=1, le=4, description="Number of images to generate (1-4)"
    )
    seed: int | None = Field(
        None, description="Random seed for reproducible generation"
    )
    model: str | None = Field("fal-ai/imagen4/preview")


class ImageToVideoRequest(BaseModel):
    prompt: str
    model: str | None = Field("fal-ai/kling-video/v2.1/master/image-to-video")
    image: Annotated[UploadFile, File()]
    duration: str | None = Field("5", description="5 or 10 seconds")
    prompt_optimizer: bool | None = Field(
        True, description="Whether to use the model's prompt optimizer"
    )


class RestoreImageRequest(BaseModel):
    image: Annotated[UploadFile, File()]
    guidance_scale: float | None = Field(
        3.5, description="CFG scale - how closely to follow the restoration guidance"
    )
    num_inference_steps: int | None = Field(
        30, description="Number of inference steps for sampling"
    )
    safety_tolerance: str | None = Field(
        "2", description="Safety tolerance level (1-6, 1 being most strict)"
    )
    output_format: str | None = Field("jpeg", description="Output format: jpeg or png")
    aspect_ratio: str | None = Field(
        None, description="Aspect ratio of the restored image"
    )
    seed: int | None = Field(
        None, description="Random seed for reproducible restoration"
    )
    sync_mode: bool | None = Field(
        False, description="Wait for image processing before returning response"
    )
