# server.py
"""
PromptShopMCP

A MCP server that allows you to generate images using simple text commands. Transform ideas into images using natural language with Google's Gemini models.

Features:
- Image generation from text prompts using Google's Gemini models
- Image modification based on text instructions

Required environment variables:
- GEMINI_API_KEY: Your Google Gemini API key

Usage:
1. Set the required environment variables
2. Run the server using FastMCP
3. Use the provided tools to generate images
"""
from mcp.server.fastmcp import FastMCP
import os
import tempfile
import requests
from io import BytesIO
from PIL import Image
import hashlib
from google import genai
from google.genai import types
import sys

# Create an MCP server
mcp = FastMCP("PromptShopMCP")

# Directory to store generated images
IMAGES_DIR = os.path.join(os.getcwd(), "generated_images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Track generated files
generated_files = {}

# Helper function for logging to stderr (won't interfere with JSON RPC)
def log_debug(message):
    print(message, file=sys.stderr, flush=True)

def is_safe_image(image_data):
    """
    Perform basic safety checks on an image
    
    Parameters:
    - image_data: Binary image data
    
    Returns:
    - Boolean indicating if image appears safe
    """
    try:
        # Basic validation that this is a valid image file
        img = Image.open(BytesIO(image_data))
        img.verify()

        # Check file size (prevent excessively large images)
        if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
            return False

        # Calculate image hash for potential blacklist checking
        # (Could be expanded to check against known unsafe image hashes)
        image_hash = hashlib.md5(image_data).hexdigest()

        # Additional checks could be added here
        # - AI-based content moderation
        # - More sophisticated image analysis

        return True
    except Exception as e:
        log_debug(f"Image safety check failed: {str(e)}")
        return False

def download_image(url):
    """
    Download an image from a URL
    
    Parameters:
    - url: URL of the image to download
    
    Returns:
    - Tuple of (success_boolean, image_data_or_error_message)
    """
    try:
        # Set a timeout and user agent for the request
        headers = {
            "User-Agent": "GeminiImageModifier/1.0"
        }
        response = requests.get(url, headers=headers, timeout=10)

        # Check if request was successful
        if response.status_code == 200:
            # Check content type is an image
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                return False, f"Not an image: Content-Type is {content_type}"

            # Get image data
            image_data = response.content

            # Check image safety
            if is_safe_image(image_data):
                return True, image_data
            else:
                return False, "Image failed safety checks"
        else:
            return False, f"Failed to download image: HTTP {response.status_code}"

    except Exception as e:
        return False, f"Error downloading image: {str(e)}"

@mcp.resource("generated-image://{image_id}")
def get_generated_image(image_id: str) -> bytes:
    """
    Get a previously generated image by its ID
    """
    if image_id in generated_files:
        with open(generated_files[image_id]["path"], "rb") as f:
            return f.read()
    else:
        return f"Error: Image with ID {image_id} not found"

@mcp.resource("image-info://{image_id}")
def get_image_info(image_id: str) -> str:
    """
    Get information about a previously generated image
    """
    if image_id in generated_files:
        info = generated_files[image_id]
        return f"Generated image: {info['name']}\nMIME type: {info['mime_type']}\nPrompt: {info['prompt']}"
    else:
        return f"Error: Image with ID {image_id} not found"

@mcp.resource("list-images://")
def list_images() -> str:
    """
    List all generated images
    """
    result = "Generated images:\n"
    for img_id, info in generated_files.items():
        result += f"- {img_id}: {info['name']} ({info['mime_type']})\n"
    return result

@mcp.tool()
def generate_image_from_url(
    image_url: str,
    prompt: str,
    mime_type: str = "image/jpeg",
    temperature: float = 1.0,
    top_p: float = 0.95,
    top_k: int = 40
) -> str:
    """
    Download an image from URL and use Gemini to modify it based on prompt.
    The generated image will be saved locally and its path will be returned.
    
    Parameters:
    - image_url: URL of the image to download and modify
    - prompt: Text instruction for how to modify the image, this prompt should be simple and concise, like "add sth to sth" or "remove sth" or "change sth to sth"
    - mime_type: MIME type of the image (default: image/jpeg)
    - temperature: Creativity parameter (0.0-1.0)
    - top_p: Token selection parameter (0.0-1.0)
    - top_k: Token selection parameter (1-100)
    
    Returns:
    - String containing the local file path of the generated image
    """
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    # Download image from URL
    success, result = download_image(image_url)
    if not success:
        raise ValueError(f"Error downloading image from URL: {result}")

    # Create a temporary file for the downloaded image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(result)
        temp_file_path = temp_file.name

    try:
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)

        # Upload file to Gemini
        uploaded_file = client.files.upload(
            file=temp_file_path,
            config={"mime_type": mime_type}
        )

        # Create a conversation history with the uploaded image
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=uploaded_file.uri,
                        mime_type=mime_type,
                    ),
                    types.Part.from_text(text=prompt),
                ]
            ),
        ]

        # Configure the generation request
        generate_content_config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=8192,
            response_modalities=["image", "text"],
            response_mime_type="text/plain",
        )

        # Use streaming to capture the response chunks
        image_data = None
        response_mime_type = None
        text_response = ""

        # Process the streamed response
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash-exp",
            contents=contents,
            config=generate_content_config,
        ):
            if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
                continue

            # Check for inline image data
            if hasattr(chunk.candidates[0].content.parts[0], 'inline_data') and chunk.candidates[0].content.parts[0].inline_data:
                image_data = chunk.candidates[0].content.parts[0].inline_data.data
                response_mime_type = chunk.candidates[0].content.parts[0].inline_data.mime_type
                log_debug(f"Received inline image data: {response_mime_type}")
                break  # Once we have the image, we can stop processing
            # Accumulate text response
            elif hasattr(chunk, 'text') and chunk.text:
                text_response += chunk.text

        # If we found inline image data
        if image_data:
            # Save generated image to a file for history tracking
            import time
            output_file_name = f"generated_{int(time.time())}.jpg"
            output_file_path = os.path.join(IMAGES_DIR, output_file_name)

            # Save to file
            with open(output_file_path, "wb") as f:
                f.write(image_data)

            # Store generated file info
            file_id = f"gen_{len(generated_files)}"
            generated_files[file_id] = {
                "path": output_file_path,
                "name": output_file_name,
                "mime_type": response_mime_type or "image/jpeg",
                "prompt": prompt,
                "source_url": image_url
            }

            # Return the local file path
            log_debug(f"Image saved to: {output_file_path}")
            return output_file_path

        # If no inline image found, but we have text response, log for debugging
        if text_response:
            log_debug(f"Received text response: {text_response}")

        # If we reach here, no valid image was obtained
        raise ValueError(
            "No image data returned from Gemini. Please try a different prompt or image.")

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass

@mcp.tool()
def generate_image_from_text(
    prompt: str,
    temperature: float = 1.0,
    top_p: float = 0.95,
    top_k: int = 40
) -> str:
    """
    Generate an image using Gemini based on a text prompt only (no input image required).
    Here's how prompt should be written like, you need to expand on the details:
    - "Close-up photograph of a pair of mismatched socks with different patterns, on a dark blue velvet wooden background."
    - "Dreamy pastel landscape, soft lines, gentle colors, fluffy clouds, rainbow mountains, minimalist"
    - "Group of aliens visiting a farmer's market, trying to understand human food culture. Lots of fresh fruits and vegetables everywhere"
    - "Renaissance vampire king, flower-studded hat, flared nostrils, pink hue, soft gaze, portrait, candid, quarter-turn"
    
    The generated image will be saved locally and its path will be returned.
    
    Parameters:
    - prompt: Text instruction for what image to generate
    - temperature: Creativity parameter (0.0-1.0)
    - top_p: Token selection parameter (0.0-1.0)
    - top_k: Token selection parameter (1-100)
    
    Returns:
    - String containing the local file path of the generated image
    """
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    try:
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)

        # Create content with just the text prompt
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ]
            ),
        ]

        # Configure the generation request
        generate_content_config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=8192,
            response_modalities=["image", "text"],
            response_mime_type="text/plain",
        )

        # Use streaming to capture the response chunks
        image_data = None
        response_mime_type = None
        text_response = ""

        # Process the streamed response
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash-exp-image-generation",
            contents=contents,
            config=generate_content_config,
        ):
            if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
                continue

            # Check for inline image data
            if hasattr(chunk.candidates[0].content.parts[0], 'inline_data') and chunk.candidates[0].content.parts[0].inline_data:
                image_data = chunk.candidates[0].content.parts[0].inline_data.data
                response_mime_type = chunk.candidates[0].content.parts[0].inline_data.mime_type
                log_debug(f"Received inline image data: {response_mime_type}")
                break  # Once we have the image, we can stop processing
            # Accumulate text response
            elif hasattr(chunk, 'text') and chunk.text:
                text_response += chunk.text

        # If we found inline image data
        if image_data:
            # Save generated image to a file for history tracking
            import time
            output_file_name = f"generated_{int(time.time())}.jpg"
            output_file_path = os.path.join(IMAGES_DIR, output_file_name)

            # Save to file
            with open(output_file_path, "wb") as f:
                f.write(image_data)

            # Store generated file info
            file_id = f"gen_{len(generated_files)}"
            generated_files[file_id] = {
                "path": output_file_path,
                "name": output_file_name,
                "mime_type": response_mime_type or "image/jpeg",
                "prompt": prompt
            }

            # Return the local file path
            log_debug(f"Image saved to: {output_file_path}")
            return output_file_path

        # If no inline image found, but we have text response, log for debugging
        if text_response:
            log_debug(f"Received text response: {text_response}")

        # If we reach here, no valid image was obtained
        raise ValueError(
            "No image data returned from Gemini. Please try a different prompt.")

    except Exception as e:
        log_debug(f"Error in generate_image_from_text: {str(e)}")
        raise ValueError(f"Failed to generate image: {str(e)}")
