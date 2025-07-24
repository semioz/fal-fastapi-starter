from pydantic import BaseModel, Field
from typing import Optional, Annotated
from fastapi import UploadFile, File

class TextToVideoRequest(BaseModel):
    prompt: str
    model: Optional[str] = Field("fal-ai/minimax/hailuo-02/standard/text-to-video")
    aspect_ratio: Optional[str] = Field("16:9", description="Aspect ratio of the video (16:9, 9:16, 1:1)")
    duration: Optional[str] = Field("8s")
    negative_prompt: Optional[str] = Field(None, description="A negative prompt to guide the video generation")
    enhance_prompt: Optional[bool] = Field(True, description="Whether to enhance the video generation")
    seed: Optional[int] = Field(None, description="A seed to use for the video generation")
    resolution: Optional[str] = Field("720p", description="Resolution of the video (720p, 1080p)")
    generate_audio: Optional[bool] = Field(True)

class GenerateImageRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = Field("", description="A description of what to discourage in the generated images")
    aspect_ratio: Optional[str] = Field("1:1", description="The aspect ratio of the generated image")
    num_images: Optional[int] = Field(1, ge=1, le=4, description="Number of images to generate (1-4)")
    seed: Optional[int] = Field(None, description="Random seed for reproducible generation")
    model_name: Optional[str] = Field("fal-ai/imagen4/preview")

class RestoreImageRequest(BaseModel):
    image: Annotated[UploadFile, File()]
    guidance_scale: Optional[float] = Field(3.5, description="CFG scale - how closely to follow the restoration guidance")
    num_inference_steps: Optional[int] = Field(30, description="Number of inference steps for sampling")
    safety_tolerance: Optional[str] = Field("2", description="Safety tolerance level (1-6, 1 being most strict)")
    output_format: Optional[str] = Field("jpeg", description="Output format: jpeg or png")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio of the restored image")
    seed: Optional[int] = Field(None, description="Random seed for reproducible restoration")
    sync_mode: Optional[bool] = Field(False, description="Wait for image processing before returning response")