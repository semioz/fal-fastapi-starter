import os
import tempfile

import fal_client
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from core.schemas import GenerateImageRequest, RestoreImageRequest
from core.utils import is_valid_image, parse_fal_output

router = APIRouter()


@router.post("/restore-image")
async def restore_image(
    data: RestoreImageRequest = Form(),
):
    try:
        contents = await data.image.read()

        if not is_valid_image(data.image):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Only JPEG, PNG, and JPG are allowed.",
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name
            print(f"Saved temp file to: {temp_file_path}")

        try:
            print("Running image restoration model...")

            uploaded_url = fal_client.upload_file(temp_file_path)
            print(f"Uploaded file to Fal storage: {uploaded_url}")

            arguments = {
                k: v
                for k, v in {
                    "image_url": uploaded_url,
                    "guidance_scale": data.guidance_scale,
                    "num_inference_steps": data.num_inference_steps,
                    "safety_tolerance": data.safety_tolerance,
                    "output_format": data.output_format,
                    "aspect_ratio": data.aspect_ratio,
                    "seed": data.seed,
                    "sync_mode": data.sync_mode,
                }.items()
                if v is not None
            }

            print(f"Fal AI restoration arguments: {arguments}")

            handler = await fal_client.submit_async(
                "fal-ai/image-editing/photo-restoration",
                arguments=arguments,
            )

            output = await handler.get()

            print(f"Model output: {output}")
            result = parse_fal_output(output)

            if result is None:
                raise HTTPException(
                    status_code=500,
                    detail="No image URL found in response from the FAL API!",
                )

            return {"restored_image_url": result}

        except Exception as e:
            print(f"Error in model execution for Fal: {str(e)}")
            try:
                print("Trying fallback model...")
                handler = await fal_client.submit_async(
                    "fal-ai/nafnet/deblur",
                    arguments={"image_url": uploaded_url},
                )
                output = await handler.get()

                result = parse_fal_output(output)
                if result:
                    return {"restored_image_url": result}

                raise Exception("Fallback model returned invalid output")

            except Exception as fallback_error:
                print(f"Fallback model also failed for Fal: {str(fallback_error)}")
                raise HTTPException(
                    status_code=500,
                    detail="Image restoration failed. Please try a different image.",
                )
        finally:
            try:
                os.unlink(temp_file_path)
                print(f"Cleaned up temp file: {temp_file_path}")
            except Exception as e:
                print(f"Error cleaning up temp file: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in restore_image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        )


@router.post("/generate-image")
async def generate_image(
    data: GenerateImageRequest,
):
    try:
        print(f"Generating image with prompt: {data.prompt}")
        print(f"Model selected: {data.model_name}")

        arguments = {
            k: v
            for k, v in {
                "prompt": data.prompt,
                "negative_prompt": data.negative_prompt
                if data.negative_prompt
                else None,
                "aspect_ratio": data.aspect_ratio
                if data.aspect_ratio != "1:1"
                else None,
                "num_images": data.num_images if data.num_images != 1 else None,
                "seed": data.seed,
            }.items()
            if v is not None
        }

        print(f"Fal AI arguments: {arguments}")

        handler = await fal_client.submit_async(
            data.model_name,
            arguments=arguments,
        )

        output = await handler.get()

        print(f"Raw output from Fal (type={type(output)}): {repr(output)}")
        result = parse_fal_output(output)

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="No image URL found in response from the FAL API!",
            )

        if result.startswith("http"):
            return JSONResponse(content={"image_url": result})
        print(f"Serving temp file from: {result}")
        return FileResponse(result, media_type="image/jpeg", filename="generated.jpg")

    except Exception as e:
        print(f"Error in image generation: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate image: {str(e)}"
        )
