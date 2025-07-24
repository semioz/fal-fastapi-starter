# Fal.ai FastAPI Starter

Starter FastAPI backend for Fal.ai's image and video generation APIs. A minimal template to help developers quickly build applications with Fal.ai models.

## Features

- Image generation from text prompts
- Video generation from text or images  
- Image restoration and enhancement
- Full type safety with Pydantic

## Quick Start

1. Install dependencies: `uv sync`
2. Set up environment: Add your `FAL_KEY` to `.env` file
3. Run server: `uv run uvicorn main:app --reload`


## API Endpoints

### `GET /api/health`
Health check endpoint.

### `POST /api/generate-image`
Generate images from text prompts.

### `POST /api/restore-image`  
Restore and enhance uploaded images (multipart/form-data).

### `POST /api/generate-video-from-text`
Generate videos from text prompts.

### `POST /api/generate-video-from-image`
Generate videos from uploaded images (multipart/form-data).

## Configuration

Set your Fal.ai API key in `.env`:
```env
FAL_KEY=your_fal_api_key_here
```
