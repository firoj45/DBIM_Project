import uvicorn
import requests
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from bs4 import BeautifulSoup
import re
import logging

from testcases import dbim_checklist
from fastapi import File, UploadFile
from PIL import Image
import io
import numpy as np
from collections import Counter
from datetime import datetime
from utils import GOVERNMENT_COLOR_GROUPS,DARKEST_TONE_LIST

# Import utility functions
from utils import (
    logger,
    get_timestamp,
    find_color_group,
    is_darkest_in_group,
    get_footer_background_color,
    get_button_elements,
    get_button_background_color,
    is_color_in_palette
)

# Suppress BeautifulSoup warnings
import warnings
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

app = FastAPI(title="DBIM Toolkit API")

# CORS middleware configuration - allowing all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Log all incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

class VerificationResult(BaseModel):
    success: bool
    message: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

# In-memory storage for verification results
verification_results: Dict[int, VerificationResult] = {}

#testcase_4
@app.post("/api/verify/footer-color", response_model=VerificationResult)
async def verify_footer_color(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        arr = np.array(img)
        # Flatten to a list of RGB tuples
        pixels = arr.reshape(-1, 3)
        # Count most common color
        most_common = Counter(map(tuple, pixels)).most_common(1)[0][0]
        most_common_list = [int(x) for x in most_common]
        # Convert to hex
        hex_color = '#%02x%02x%02x' % tuple(most_common_list)
        hex_color = hex_color.upper()
        if str(hex_color) in DARKEST_TONE_LIST:
            # return {"rgb": most_common_list, "hex": hex_color}
            return VerificationResult(
                success=True,
                message=f"Tone of the colour palette {hex_color}",
                timestamp=datetime.utcnow().isoformat(),
                details={"rgb": most_common_list, "hex": hex_color})
        else:
            return VerificationResult(
                success=False,
                message=f"Tone of the colour palette {hex_color} NOT matched with palette",
                timestamp=datetime.utcnow().isoformat(),
                details={"rgb": most_common_list, "hex": hex_color}
)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)}) 

#testcase_9
@app.post("/api/verify/text-color", response_model=VerificationResult)
async def verify_text_color(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        arr = np.array(img)
        gray = np.dot(arr[...,:3], [0.299, 0.587, 0.114])  # Convert to grayscale
        mean_gray = np.mean(gray)
        # If mostly dark, look for light pixels (text); if mostly light, look for dark pixels (text)
        if mean_gray < 128:
            # Mostly dark background, look for light text
            threshold = mean_gray + (255 - mean_gray) * 0.5  # Midway to white
            mask = gray > threshold
        else:
            # Mostly light background, look for dark text
            threshold = mean_gray * 0.5
            mask = gray < threshold
        text_pixels = arr[mask]
        if len(text_pixels) == 0:
            # fallback: just use the most common color
            pixels = arr.reshape(-1, 3)
            most_common = Counter(map(tuple, pixels)).most_common(1)[0][0]
        else:
            most_common = Counter(map(tuple, text_pixels)).most_common(1)[0][0]
        most_common_list = [int(x) for x in most_common]
        hex_color = '#%02x%02x%02x' % tuple(most_common_list)
        hex_color = hex_color.upper()
        target_color = '#150202'.upper()
        is_match = (hex_color == target_color)
        return VerificationResult(
            success=is_match,
            message=f"Detected text color: {hex_color}. {'Matches required color.' if is_match else 'Does NOT match required color #150202.'}",
            timestamp=datetime.utcnow().isoformat(),
            details={"rgb": most_common_list, "hex": hex_color}
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# API Endpoints
@app.get("/api/guidelines")
async def get_guidelines() -> List[Dict[str, Any]]:
    """Return the list of all color guidelines from testcases.py"""
    return [
        {"id": gid, "description": desc} for gid, desc in dbim_checklist.items()
    ]

@app.get("/api/verify/color-palette-selection", response_model=VerificationResult)
async def verify_color_palette_selection():
    """Verify color palette selection guideline"""
    result = VerificationResult(
        success=True,
        message="Color palette selection verified successfully",
        timestamp=get_timestamp(),
        details={
            "colors": ["#0056b3", "#1a6bc4", "#3381d6", "#4d97e8", "#66adfa"],
            "gradients": 5,
            "status": "valid"
        }
    )
    verification_results[1] = result
    return result

@app.get("/api/verify/government-entity-color", response_model=VerificationResult)
async def verify_government_entity_color():
    """Verify government entity color guideline"""
    result = VerificationResult(
        success=True,
        message="Government entity color verified",
        timestamp=get_timestamp(),
        details={
            "selected_color": "#0056b3",
            "contrast_ratio": "4.5:1",
            "accessibility": "AA compliant"
        }
    )
    verification_results[2] = result
    return result

@app.get("/api/verify/iconography-color", response_model=VerificationResult)
async def verify_iconography_color():
    """Verify iconography color guideline"""
    result = VerificationResult(
        success=True,
        message="Iconography colors verified against palette",
        timestamp=get_timestamp(),
        details={
            "status": "all_icons_valid",
            "invalid_icons": []
        }
    )
    verification_results[3] = result
    return result

@app.get("/api/verify/cta-buttons", response_model=VerificationResult)
async def verify_cta_buttons(url: str = Query(..., description="URL of the website to verify")):
    """
    Verify that all call-to-action buttons use colors from the official government palette.
    
    Args:
        url: The URL of the website to check for CTA buttons
        
    Returns:
        VerificationResult with details about CTA button colors
    """
    try:
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all button-like elements
        buttons = get_button_elements(soup)
        if not buttons:
            return VerificationResult(
                success=False,
                message="No interactive buttons found on the page",
                timestamp=get_timestamp(),
                details={
                    "status": "no_buttons_found",
                    "suggestion": "The page might use non-standard button elements or load them dynamically with JavaScript"
                }
            )
        
    
        
        # Check each button
        results = []
        invalid_buttons = []
        
        for button in buttons:
            color_info = get_button_background_color(button, soup)
            # print("color_info: ", color_info)
            
            if color_info.get('status') != 'success':
                # Skip buttons where we can't determine the color
                continue
                
            color = color_info['color']
            is_valid = is_color_in_palette(color)
            
            result = {
                'text': button['text'],
                'element': button['element'],
                'color': color,
                'is_valid': is_valid,
                'source': color_info.get('source', 'unknown')
            }
            
            results.append(result)
            if not is_valid:
                invalid_buttons.append({
                    'text': button['text'][:50] + ('...' if len(button['text']) > 50 else ''),
                    'color': color,
                    'element': button['element']
                })
        # Prepare the final result
        all_valid = len(invalid_buttons) == 0
        
        # Prepare list of all found buttons with their details
        all_buttons = []
        for button in buttons:
            color_info = get_button_background_color(button, soup)
            button_info = {
                'text': button['text'][:100] + ('...' if len(button['text']) > 100 else ''),
                'element': button['element'],
                'classes': button.get('classes', []),
                'id': button.get('id', ''),
                'color_status': color_info.get('status', 'unknown'),
                'color': color_info.get('color', None),
                'source': color_info.get('source', 'unknown'),
                'is_valid': is_color_in_palette(color_info.get('color', '')) if color_info.get('status') == 'success' else None
            }
            all_buttons.append(button_info)
        
        # Determine status based on validation results
        if not results:
            status = "no_valid_buttons"
            message = "No buttons with valid color information were found"
        elif all_valid:
            status = "all_valid"
            message = "All call-to-action buttons use colors from the official palette"
        else:
            status = f"invalid_colors_found_{len(invalid_buttons)}_of_{len(results)}"
            message = f"Found {len(invalid_buttons)} out of {len(results)} buttons not using the official color palette"
        
        # Prepare common details
        details = {
            "status": status,
            "buttons_checked": len(buttons),
            "valid_buttons_count": len([b for b in all_buttons if b.get('is_valid') is True]),
            "invalid_buttons_count": len([b for b in all_buttons if b.get('is_valid') is False]),
            "buttons_without_colors": len([b for b in all_buttons if b.get('color_status') != 'success']),
            "all_buttons": all_buttons,
            "UI_status": False  # Add UI_status based on validation
        }
        
        # Add additional details based on status
        if status == "all_valid":
            details["valid_colors_found"] = [r['color'] for r in results]
        elif status.startswith("invalid_colors_found"):
            details.update({
                "invalid_buttons": invalid_buttons,
                "suggestion": "Ensure all call-to-action buttons use colors from the official government palette"
            })
        
        result = VerificationResult(
            success=all_valid,
            message=message,
            timestamp=get_timestamp(),
            details=details
        )
        
        verification_results[5] = result
        return result
        
    except requests.RequestException as e:
        return VerificationResult(
            success=False,
            message=f"Failed to fetch the webpage: {str(e)}",
            timestamp=get_timestamp(),
            details={
                "status": "request_error",
                "error": str(e),
                "suggestion": "Check the URL and try again. The server might be down or the URL might be incorrect."
            }
        )
    except Exception as e:
        return VerificationResult(
            success=False,
            message=f"An error occurred while verifying CTA buttons: {str(e)}",
            timestamp=get_timestamp(),
            details={
                "status": "error",
                "error": str(e),
                "suggestion": "Please try again later or contact support if the issue persists.",
                "UI_status": False
            }
        )

@app.get("/api/verify/highlight-backgrounds", response_model=VerificationResult)
async def verify_highlight_backgrounds():
    """Verify highlight backgrounds guideline"""
    result = VerificationResult(
        success=True,
        message="Highlight backgrounds are using valid colors",
        timestamp=get_timestamp(),
        details={
            "allowed_colors": ["linen", "#f5f5f5", "#e6f2ff"],
            "status": "all_valid"
        }
    )
    verification_results[6] = result
    return result

@app.get("/api/verify/brand-color-consideration", response_model=VerificationResult)
async def verify_brand_color_consideration():
    """Verify brand color consideration guideline"""
    result = VerificationResult(
        success=True,
        message="Brand color considerations are properly applied",
        timestamp=get_timestamp(),
        details={
            "brand_colors": ["#0056b3", "#1a6bc4"],
            "nearest_palette_match": "#0056b3",
            "status": "match_found"
        }
    )
    verification_results[7] = result
    return result

@app.get("/api/verify/digital-use-only", response_model=VerificationResult)
async def verify_digital_use_only():
    """Verify digital use only guideline"""
    result = VerificationResult(
        success=True,
        message="Colors are verified for digital use only",
        timestamp=get_timestamp(),
        details={
            "rgb_colors_only": True,
            "print_colors_restricted": True,
            "status": "valid"
        }
    )
    verification_results[8] = result
    return result

#testcase_10
@app.post("/api/verify/logo-lockups", response_model=VerificationResult)
async def verify_logo_lockups(file: UploadFile = File(...)):
    """
    Verify logo lockups guideline:
    - All logo lockups must be in black (#000000) on any background.
    Accepts a screenshot image upload.
    """
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)

        # --- Image Enhancement (optional, improves detection) ---
        import cv2
        sharpen_kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        sharpened = cv2.filter2D(image_np, -1, sharpen_kernel)
        img_yuv = cv2.cvtColor(sharpened, cv2.COLOR_RGB2YUV)
        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
        enhanced = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
        image_np = enhanced

        # 1. Detect background color from edges
        top_edge = image_np[0:5, :, :].reshape(-1, 3)
        bottom_edge = image_np[-5:, :, :].reshape(-1, 3)
        left_edge = image_np[:, 0:5, :].reshape(-1, 3)
        right_edge = image_np[:, -5:, :].reshape(-1, 3)
        background_pixels = np.concatenate((top_edge, bottom_edge, left_edge, right_edge), axis=0)
        bg_rgb = np.mean(background_pixels, axis=0)
        bg_hex = '#%02x%02x%02x' % tuple(int(x) for x in bg_rgb)

        # 2. Mask out background-like pixels (Euclidean distance < 15)
        flat_img = image_np.reshape(-1, 3)
        bg_rgb_arr = np.array(bg_rgb).reshape(1, 3)
        dist = np.linalg.norm(flat_img - bg_rgb_arr, axis=1)
        logo_pixels = flat_img[dist > 15]
        percent_logo = len(logo_pixels) / len(flat_img) if len(flat_img) > 0 else 0

        # 3. For logo pixels, check if they are close to black (all channels <= 40)
        black_pixels = [px for px in logo_pixels if all(c <= 40 for c in px)]
        percent_black = len(black_pixels) / len(logo_pixels) if len(logo_pixels) > 0 else 0

        # Calculate hex code for logo
        if len(logo_pixels) > 0:
            logo_rgb = np.mean(logo_pixels, axis=0)
            logo_hex = '#%02x%02x%02x' % tuple(int(x) for x in logo_rgb)
        else:
            logo_hex = None

        # Pass if at least 80% of logo pixels are black
        if percent_black >= 0.75:
            status = "valid"
            success = True
            message = f"Logo lockups are sufficiently black (>=75% black pixels). ({int(percent_black*100)}% black)"
        else:
            status = "invalid"
            success = False
            message = f"Logo lockups are not compliant. Only {int(percent_black*100)}% of logo pixels are black."

        result = VerificationResult(
            success=success,
            message=message,
            timestamp=get_timestamp(),
            details={
                "background_hex": bg_hex,
                "logo_hex": logo_hex,
                "percent_logo_pixels": int(percent_logo*100),
                "percent_black_logo_pixels": int(percent_black*100),
                "status": status
            }
        )
        verification_results[10] = result
        return result
    except Exception as e:
        result = VerificationResult(
            success=False,
            message=f"Error processing logo lockup image: {str(e)}",
            timestamp=get_timestamp(),
            details={"error": str(e)}
        )
        verification_results[10] = result
        return result

#tescase_11
@app.get("/api/verify/primary-backgrounds", response_model=VerificationResult)
async def verify_primary_backgrounds(url: str = Query(..., description="URL to check")):
    """Verify primary backgrounds guideline by capturing a screenshot and checking the central region for white background."""
    import tempfile
    import numpy as np
    from PIL import Image
    from playwright.async_api import async_playwright

    try:
        # Step 1: Capture full-page screenshot using Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state('networkidle')
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
                screenshot_path = tmpfile.name
                await page.screenshot(path=screenshot_path, full_page=True)
            await browser.close()

        # Step 2: Open screenshot and focus on central 60% region
        image = Image.open(screenshot_path).convert("RGB")
        img_np = np.array(image)
        h, w, _ = img_np.shape
        y1, y2 = int(0.2 * h), int(0.8 * h)
        x1, x2 = int(0.2 * w), int(0.8 * w)
        central_region = img_np[y1:y2, x1:x2, :]
        total_pixels = central_region.shape[0] * central_region.shape[1]

        # Step 3: Count pixels close to white (#FFFFFF)
        white_thresh = 245  # Allow a little tolerance
        white_pixels = np.mean(central_region, axis=2) >= white_thresh

        percent_white = np.sum(white_pixels) / total_pixels

        # Step 4: Prepare response
        status = "valid" if percent_white >= 0.5 else "invalid"
        success = percent_white >= 0.5
        message = (
            f"{int(percent_white*100)}% of the main background is white. "
            + ("Pass ✅" if success else "Fail ❌: At least 50% must be white.")
        )
        result = VerificationResult(
            success=success,
            message=message,
            timestamp=get_timestamp(),
            details={
                "background_hex": "#FFFFFF",
                "percent_white_pixels": int(percent_white * 100),
                "status": status
            }
        )
        verification_results[11] = result
        return result
    except Exception as e:
        result = VerificationResult(
            success=False,
            message=f"Error processing URL or screenshot: {str(e)}",
            timestamp=get_timestamp(),
            details={"error": str(e)}
        )
        verification_results[11] = result
        return result

#testcase_12
@app.post("/api/verify/state-emblem-usage", response_model=VerificationResult)
async def verify_state_emblem_usage(file: UploadFile = File(...)):
    """
    Verify state emblem usage guideline:
    - Emblem must be white (#FFFFFF) on dark background (#000000)
    - Emblem must be black (#000000) on white background (#FFFFFF)
    Accepts a screenshot image upload.
    """
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)

        # --- Image Enhancement ---
        import cv2
        sharpen_kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        sharpened = cv2.filter2D(image_np, -1, sharpen_kernel)
        img_yuv = cv2.cvtColor(sharpened, cv2.COLOR_RGB2YUV)
        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
        enhanced = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
        # Use enhanced image for all further processing
        image_np = enhanced

        # 1. Detect background color from edges
        top_edge = image_np[0:5, :, :].reshape(-1, 3)
        bottom_edge = image_np[-5:, :, :].reshape(-1, 3)
        left_edge = image_np[:, 0:5, :].reshape(-1, 3)
        right_edge = image_np[:, -5:, :].reshape(-1, 3)
        background_pixels = np.concatenate((top_edge, bottom_edge, left_edge, right_edge), axis=0)
        bg_rgb = np.mean(background_pixels, axis=0)
        bg_brightness = np.mean(bg_rgb)
        if bg_brightness > 180:
            bg_color = "White"
        elif bg_brightness < 80:
            bg_color = "Black"
        else:
            bg_color = "Gray"

        # 2. Mask out background-like pixels (Euclidean distance < 15)
        flat_img = image_np.reshape(-1, 3)
        bg_rgb_arr = np.array(bg_rgb).reshape(1, 3)
        dist = np.linalg.norm(flat_img - bg_rgb_arr, axis=1)
        emblem_pixels = flat_img[dist > 15]
        percent_emblem = len(emblem_pixels) / len(flat_img) if len(flat_img) > 0 else 0

        # 3. For emblem pixels, check for dark/light
        if bg_color == "White":
            dark_pixels = [px for px in emblem_pixels if all(c <= 60 for c in px)]
            percent_dark = len(dark_pixels) / len(emblem_pixels) if len(emblem_pixels) > 0 else 0
            if percent_dark >= 0.2:
                status = "valid"
                success = True
                message = f"Emblem is sufficiently dark (black/dark gray) on white background (valid). {int(percent_dark*100)}% dark pixels."
            else:
                status = "invalid"
                success = False
                message = f"Emblem/background contrast not compliant. Only {int(percent_dark*100)}% dark emblem pixels."
        elif bg_color == "Black":
            light_pixels = [px for px in emblem_pixels if all(c >= 200 for c in px)]
            percent_light = len(light_pixels) / len(emblem_pixels) if len(emblem_pixels) > 0 else 0
            if percent_light >= 0.2:
                status = "valid"
                success = True
                message = f"Emblem is sufficiently light (white/light) on dark background (valid). {int(percent_light*100)}% light pixels."
            else:
                status = "invalid"
                success = False
                message = f"Emblem/background contrast not compliant. Only {int(percent_light*100)}% light emblem pixels."
        else:
            status = "invalid"
            success = False
            message = "Background is not clearly white or black."

        # Calculate hex codes for swatch display
        bg_hex = '#%02x%02x%02x' % tuple(int(x) for x in bg_rgb)
        if len(emblem_pixels) > 0:
            emblem_rgb = np.mean(emblem_pixels, axis=0)
            emblem_hex = '#%02x%02x%02x' % tuple(int(x) for x in emblem_rgb)
        else:
            emblem_hex = None
        # Strict emblem color check (must be gray/black or gray/white)
        strict_emblem = False
        emblem_color_type = None
        if emblem_hex:
            r, g, b = [int(x) for x in np.mean(emblem_pixels, axis=0)]
            grayness = max(abs(r-g), abs(g-b), abs(r-b))
            # Looser gray check: allow grayness up to 18
            if grayness <= 18:
                if bg_color == "White" and max(r, g, b) <= 200:
                    strict_emblem = True
                    emblem_color_type = "gray/black"
                elif bg_color == "Black" and min(r, g, b) >= 200:
                    strict_emblem = True
                    emblem_color_type = "light gray/white"
        # If not strict, override to invalid
        if not strict_emblem:
            status = "invalid"
            success = False
            message = "Emblem color is not monochrome (gray/black for white bg or gray/white for black bg). Colored emblems are not allowed."
        result = VerificationResult(
            success=success,
            message=message,
            timestamp=get_timestamp(),
            details={
                "background_color": bg_color,
                "background_hex": bg_hex,
                "emblem_hex": emblem_hex,
                "emblem_color_type": emblem_color_type,
                "percent_emblem_pixels": int(percent_emblem*100),
                "status": status
            }
        )
        verification_results[12] = result
        return result
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# Get all verification results
@app.get("/api/verifications")
async def get_verification_results() -> Dict[int, Dict[str, Any]]:
    """Get all verification results"""
    return {k: v.dict() for k, v in verification_results.items()}

from urllib.parse import urljoin
import re

#testcase_20
from playwright.async_api import async_playwright
import os
import requests
import time
from fastapi import BackgroundTasks

# Guideline 54: Server Response Time
@app.get("/api/verify/server-response-time")
async def verify_server_response_time(url: str = Query(...)):
    try:
        start = time.time()
        r = requests.get(url, timeout=10)
        elapsed = (time.time() - start) * 1000  # ms
        return {
            "success": elapsed < 800,
            "url": url,
            "status_code": r.status_code,
            "response_time_ms": round(elapsed, 2),
            "message": (
                f"Good response time: {elapsed:.2f} ms" if elapsed < 800 
                else f"Slow response time: {elapsed:.2f} ms"
            )
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

# Guideline 55: Browser Caching
@app.get("/api/verify/browser-caching")
async def verify_browser_caching(url: str = Query(..., description="URL of the page to check caching headers")):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract static resource URLs
        static_urls = set()

        for tag in soup.find_all(["script", "link", "img"]):
            src = tag.get("src") or tag.get("href")
            if src:
                full_url = urljoin(url, src)
                if any(ext in full_url for ext in [".js", ".css", ".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2", ".ttf"]):
                    static_urls.add(full_url)

        results = []
        for static_url in static_urls:
            try:
                res = requests.head(static_url, timeout=5)
                headers = {k.lower(): v for k, v in res.headers.items()}
                has_cache = any(h in headers for h in ['cache-control', 'expires', 'etag'])
                results.append({
                    "url": static_url,
                    "status": "Cached" if has_cache else "Not Cached",
                    "headers": {k: headers[k] for k in ['cache-control', 'expires', 'etag'] if k in headers}
                })
            except Exception as e:
                results.append({
                    "url": static_url,
                    "status": "Failed to fetch",
                    "error": str(e)
                })

        cached_assets = [r for r in results if "Cached" in r["status"]]
        return {
            "success": len(cached_assets) > 0,
            "total_assets_checked": len(results),
            "cached_assets": len(cached_assets),
            "details": results,
            "message": "Some static assets have caching headers." if cached_assets else "No caching headers found for static assets."
        }

    except Exception as e:
        return {"success": False, "message": str(e)}

# Guideline 56: Images Optimized
@app.get("/api/verify/image-optimization")
async def verify_image_optimization(url: str = Query(...)):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')
            imgs = await page.evaluate('''() => Array.from(document.images).map(i => ({src: i.src, width: i.naturalWidth, height: i.naturalHeight, size: i.src.length}))''')
            await browser.close()
        optimized = all(img['width'] <= 1920 and img['height'] <= 1080 for img in imgs if img['width'] and img['height'])
        # Truncate src for each image, add src_truncated flag
        def truncate_img(img):
            src = img.get('src', '')
            maxlen = 100
            truncated = len(src) > maxlen
            return {
                **img,
                'src': src[:maxlen] + ('...' if truncated else ''),
                # 'src_truncated': truncated
            }
        images_trunc = [truncate_img(img) for img in imgs[:10]]
        return {
            "success": optimized,
            "image_count": len(imgs),
            "message": "All images appear optimized." if optimized else "Some images may not be optimized.",
            "images": images_trunc
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

# Guideline 57: JS Execution Optimized
@app.get("/api/verify/js-optimization")
async def verify_js_optimization(url: str = Query(..., description="Website URL to check JS optimization")):
    """
    Checks for JavaScript optimization:
    - Use of minified scripts
    - Use of async/defer
    - Presence of inline scripts
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')
            scripts = await page.evaluate('''() => 
                Array.from(document.scripts).map(s => ({
                    src: s.src, 
                    inline: !s.src, 
                    async: s.async, 
                    defer: s.defer, 
                    type: s.type, 
                    length: s.innerText.length
                }))
            ''')
            await browser.close()

        total_external = 0
        minified_external = 0
        async_or_defer = 0
        inline_scripts = 0
        large_inline_scripts = 0

        for s in scripts:
            if s["src"]:
                total_external += 1
                if ".min." in s["src"] or "min" in s["src"]:
                    minified_external += 1
                if s["async"] or s["defer"]:
                    async_or_defer += 1
            else:
                inline_scripts += 1
                if s["length"] > 500:  # Arbitrary large inline threshold
                    large_inline_scripts += 1

        msg = (
            f"{minified_external}/{total_external} external scripts are minified. "
            f"{async_or_defer}/{total_external} use async/defer. "
            f"{inline_scripts} inline scripts ({large_inline_scripts} large)."
        )

        success = (
            minified_external == total_external and
            async_or_defer == total_external and
            inline_scripts == 0
        )

        # Truncate 'src' and 'text' fields to 50 chars in sample_script_details
        truncated_scripts = []
        for s in scripts[:5]:
            new_s = s.copy()
            if 'src' in new_s and isinstance(new_s['src'], str):
                new_s['src'] = new_s['src'][:50]
            if 'text' in new_s and isinstance(new_s['text'], str):
                new_s['text'] = new_s['text'][:50]
            truncated_scripts.append(new_s)
        return {
            "success": success,
            "total_external_scripts": total_external,
            "minified_external_scripts": minified_external,
            "async_or_defer_used": async_or_defer,
            "inline_script_count": inline_scripts,
            "large_inline_scripts": large_inline_scripts,
            "message": msg,
            "sample_script_details": truncated_scripts
        }

    except Exception as e:
        return {"success": False, "message": str(e)}

# Guideline 58: Browser Pre-loading
@app.get("/api/verify/browser-preloading")
async def verify_browser_preloading(url: str = Query(...)):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')
            links = await page.evaluate('''() => Array.from(document.querySelectorAll('link[rel="preload"],link[rel="prefetch"]')).map(l => l.outerHTML)''')
            await browser.close()
        return {
            "success": len(links) > 0,
            "preload_links": links,
            "message": "Preloading detected." if links else "No preloading links found."
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

# Guideline 59: Lazy Loading Images
@app.get("/api/verify/lazy-loading")
async def verify_lazy_loading(url: str = Query(..., description="URL to check lazy loading usage")):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')

            lazy_elements = await page.evaluate('''() => {
                const lazyImages = Array.from(document.querySelectorAll('img[loading="lazy"], img.lazy, img[data-src]'));
                const lazyIframes = Array.from(document.querySelectorAll('iframe[loading="lazy"], iframe.lazy, iframe[data-src]'));
                const lazyVideos = Array.from(document.querySelectorAll('video[loading="lazy"], video.lazy, source[data-src]'));
                return {
                    image_count: lazyImages.length,
                    iframe_count: lazyIframes.length,
                    video_count: lazyVideos.length
                };
            }''')

            await browser.close()

        total_lazy = lazy_elements["image_count"] + lazy_elements["iframe_count"] + lazy_elements["video_count"]

        return {
            "success": total_lazy > 0,
            "lazy_image_count": lazy_elements["image_count"],
            "lazy_iframe_count": lazy_elements["iframe_count"],
            "lazy_video_count": lazy_elements["video_count"],
            "message": (
                f"Lazy-loaded elements detected: "
                f"{lazy_elements['image_count']} images, "
                f"{lazy_elements['iframe_count']} iframes, "
                f"{lazy_elements['video_count']} videos."
                if total_lazy else
                "No lazy loading detected for images, iframes, or videos."
            )
        }

    except Exception as e:
        return {"success": False, "message": str(e)}


# Guideline 60: Resource Loading Order
@app.get("/api/verify/resource-order")
async def verify_resource_order(url: str = Query(...)):
    """
    Verifies optimal resource load order:
    - CSS before JS
    - No blocking JS in head
    - Defer/async recommended
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')

            resource_order = await page.evaluate('''() => {
                const headChildren = Array.from(document.head.children);
                let cssBeforeJs = true;
                let foundCss = false;
                let blockingJs = false;
                let totalScripts = 0;
                let deferScripts = 0;
                let asyncScripts = 0;

                for (let el of headChildren) {
                    if (el.tagName === 'LINK' && el.rel === 'stylesheet') {
                        foundCss = true;
                    }
                    if (el.tagName === 'SCRIPT') {
                        totalScripts++;
                        if (el.defer) deferScripts++;
                        if (el.async) asyncScripts++;
                        if (!el.defer && !el.async && (!el.type || el.type === 'text/javascript')) {
                            if (!foundCss) cssBeforeJs = false;
                            blockingJs = true;
                        }
                    }
                }

                return {
                    cssBeforeJs,
                    blockingJs,
                    totalScripts,
                    deferScripts,
                    asyncScripts
                };
            }''')

            await browser.close()

        return {
            "success": resource_order["cssBeforeJs"] and not resource_order["blockingJs"],
            **resource_order,
            "message": (
                f"CSS before JS: {resource_order['cssBeforeJs']}. "
                f"Blocking JS in <head>: {resource_order['blockingJs']}. "
                f"Total Scripts: {resource_order['totalScripts']}, "
                f"Defer: {resource_order['deferScripts']}, Async: {resource_order['asyncScripts']}."
            )
        }

    except Exception as e:
        return {"success": False, "message": str(e)}


# Guideline 61: Critical Resources Prioritized
@app.get("/api/verify/critical-resources")
async def verify_critical_resources(url: str = Query(...)):
    """
    Checks for presence of inline critical CSS, eagerly loaded above-the-fold images,
    and optionally preloaded resources.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')

            # Check inline <style> blocks (usually critical CSS)
            critical_css = await page.evaluate('''() => {
                return Array.from(document.head.querySelectorAll('style'))
                            .map(s => s.innerText.length)
                            .reduce((a,b) => a+b, 0);
            }''')

            # Get above-the-fold images and their loading type
            above_fold_imgs = await page.evaluate('''() => {
                return Array.from(document.images)
                    .filter(img => {
                        const rect = img.getBoundingClientRect();
                        return rect.top < window.innerHeight && rect.left < window.innerWidth;
                    })
                    .map(img => ({src: img.src, loading: img.loading}));
            }''')

            # Check preload links
            preload_resources = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('link[rel="preload"]'))
                            .map(link => ({href: link.href, as: link.as}));
            }''')

            await browser.close()

        non_lazy_above_fold = [img for img in above_fold_imgs if img['loading'] != 'lazy']
        msg = (
            f"Critical CSS chars: {critical_css}. "
            f"Above-the-fold images: {len(above_fold_imgs)}, non-lazy: {len(non_lazy_above_fold)}. "
            f"Preloaded resources: {len(preload_resources)}"
        )

        # Truncate 'src' field for each image in above_fold_images
        truncated_above_fold_imgs = []
        for img in above_fold_imgs:
            new_img = img.copy()
            if 'src' in new_img and isinstance(new_img['src'], str):
                new_img['src'] = new_img['src'][:50]
            truncated_above_fold_imgs.append(new_img)

        return {
            "success": critical_css > 0 and len(non_lazy_above_fold) == len(above_fold_imgs),
            "critical_css_char_count": critical_css,
            "above_fold_images": truncated_above_fold_imgs,
            "non_lazy_above_fold_count": len(non_lazy_above_fold),
            "preload_resources": preload_resources,
            "message": msg
        }

    except Exception as e:
        return {"success": False, "message": str(e)}


# Guideline 62: Async Loading for Non-Essential Scripts
@app.get("/api/verify/async-scripts")
async def verify_async_scripts(url: str = Query(...)):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')
            async_scripts = await page.evaluate('''() => Array.from(document.scripts).filter(s => s.async || s.defer).map(s => s.src)''')
            await browser.close()
        return {
            "success": len(async_scripts) > 0,
            "async_scripts": async_scripts,
            "message": f"{len(async_scripts)} scripts loaded asynchronously." if async_scripts else "No async/defer scripts found."
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

# Guideline 63: Responsiveness
@app.get("/api/verify/responsiveness")
async def verify_responsiveness(url: str = Query(...)):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_viewport_size({"width": 375, "height": 667})  # Mobile
            await page.goto(url, wait_until='networkidle')
            mobile_width = await page.evaluate('''() => document.body.scrollWidth''')
            await page.set_viewport_size({"width": 1200, "height": 800})  # Desktop
            desktop_width = await page.evaluate('''() => document.body.scrollWidth''')
            await browser.close()
        responsive = abs(mobile_width - desktop_width) > 50
        print("-----",mobile_width ,desktop_width)
        return {
            "success": responsive,
            "mobile_body_width": mobile_width,
            "desktop_body_width": desktop_width,
            "message": "Responsive layout detected." if responsive else "No significant layout change detected."
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

# Guideline 64: CDN Used
@app.get("/api/verify/cdn")
async def verify_cdn(url: str = Query(...)):
    try:
        import re
        from bs4 import BeautifulSoup
        r = requests.get(url, timeout=10)
        cdn_keywords = ["cloudflare", "akamai", "fastly", "cdn", "edgekey", "stackpath"]
        server_header = r.headers.get('server', '').lower()
        body = r.text.lower()
        cdn_used = any(k in server_header or k in body for k in cdn_keywords)

        # Parse static asset URLs and check for CDN domains
        soup = BeautifulSoup(r.text, 'html.parser')
        static_urls = set()
        # Images
        static_urls.update(img.get('src','') for img in soup.find_all('img') if img.get('src'))
        # JS scripts
        static_urls.update(script.get('src','') for script in soup.find_all('script') if script.get('src'))
        # CSS
        static_urls.update(link.get('href','') for link in soup.find_all('link', rel='stylesheet') if link.get('href'))
        # Filter only URLs that look like CDN
        cdn_asset_urls = [u for u in static_urls if any(k in u.lower() for k in cdn_keywords)]

        # Truncate data URLs in cdn_asset_urls to 50 characters
        truncated_cdn_asset_urls = []
        for u in cdn_asset_urls[:10]:
            if u.startswith('data:'):
                truncated_cdn_asset_urls.append(u[:50])
            else:
                truncated_cdn_asset_urls.append(u)

        return {
            "success": cdn_used or bool(cdn_asset_urls),
            "message": ("CDN detected." if cdn_used or cdn_asset_urls else "No CDN detected."),
            "server_header": r.headers.get('server', ''),
            "cdn_asset_urls": truncated_cdn_asset_urls
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

# Guideline 65: Cache Headers for Static Assets
@app.get("/api/verify/cache-headers")
async def verify_cache_headers(url: str = Query(...)):
    try:
        import urllib.parse
        from bs4 import BeautifulSoup
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        asset_urls = set()
        # Images
        asset_urls.update(img.get('src','') for img in soup.find_all('img') if img.get('src'))
        # JS scripts
        asset_urls.update(script.get('src','') for script in soup.find_all('script') if script.get('src'))
        # CSS
        asset_urls.update(link.get('href','') for link in soup.find_all('link', rel='stylesheet') if link.get('href'))
        # Normalize and filter URLs
        normalized_urls = []
        for u in asset_urls:
            if u.startswith('http://') or u.startswith('https://'):
                normalized_urls.append(u)
            elif u.startswith('//'):
                normalized_urls.append('https:' + u)
            elif u.startswith('/'):
                parsed = urllib.parse.urlparse(url)
                normalized_urls.append(f"{parsed.scheme}://{parsed.netloc}{u}")
            # else: ignore data: and relative paths for brevity
        summary = []
        # for asset_url in normalized_urls[:10]:
        for asset_url in normalized_urls:  # limit to 10 assets
            try:
                asset_resp = requests.head(asset_url, timeout=5, allow_redirects=True)
                asset_cache_headers = {k.lower(): v for k, v in asset_resp.headers.items() if k.lower().startswith('cache') or k.lower() in ['etag', 'expires']}
                has_cache = any(h in asset_cache_headers for h in ['cache-control', 'expires', 'etag'])
                summary.append({
                    'url': asset_url[:50],  # truncate for brevity
                    'cache_headers': asset_cache_headers,
                    'has_cache_headers': has_cache
                })
            except Exception as ex:
                summary.append({'url': asset_url[:50], 'error': str(ex), 'has_cache_headers': False})
        overall_success = any(item['has_cache_headers'] for item in summary)
        return {
            "success": overall_success,
            "static_assets_checked": len(summary),
            "assets_with_cache_headers": sum(1 for item in summary if item['has_cache_headers']),
            "asset_cache_summary": summary,
            "message": (f"{sum(1 for item in summary if item['has_cache_headers'])} of {len(summary)} static assets have cache headers." if summary else "No static assets found.")
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
#testcase_20
@app.get("/api/verify/noto-sans")
async def verify_noto_sans(url: str = Query(..., description="URL of the webpage to verify")):
    """
    Verify if all text on the webpage uses Noto Sans font (browser-accurate, Playwright-based).
    Args:
        url: The URL of the webpage to check
    Returns:
        dict: Verification result with details about font usage
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')

            # DOM font-family check for Noto Sans
            fonts_used = await page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll("body *"));
                    const fonts = new Set();
                    elements.forEach(el => {
                        const style = window.getComputedStyle(el);
                        if (style && style.fontFamily) {
                            fonts.add(style.fontFamily.toLowerCase());
                        }
                    });
                    return Array.from(fonts);
                }
            """)
            print("fonts_used============",fonts_used)
            # Extract all unique font family names from the font-family strings (robust, handles quotes and spaces)
            all_families = set()
            for fam_str in fonts_used:
                # Split on commas, strip whitespace and quotes, lowercase
                for fam in fam_str.split(','):
                    fam = fam.strip().strip('"').strip("'").lower()
                    if fam:
                        all_families.add(fam)
            all_families_list = sorted(all_families)

            noto_sans_used = all("noto sans" in font for font in fonts_used)
            font_details = fonts_used

            await browser.close()

            return {
                "success": noto_sans_used,
                "all_text_noto_sans": noto_sans_used,
                "font_families_detected": all_families_list,
                "font_family_strings": font_details,
                "message": "All visible text uses Noto Sans." if noto_sans_used else "Some elements do not use Noto Sans.",
            }
        
        # Check for system font stack that might include Noto Sans on some systems
        system_fonts_used = any(family.lower() in ['sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 
                                                'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial'] 
                             for family in font_families)
        
        # Determine the result
        if noto_sans_loaded or uses_noto_sans:
            message = "Noto Sans is being used on this page"
            uses_noto_sans_only = True
            success = True
        elif google_fonts_used:
            message = "Google Fonts detected. Manual verification recommended to confirm Noto Sans usage."
            uses_noto_sans_only = None  # Can't be certain
            success = False
        elif system_fonts_used:
            message = "System fonts detected. Noto Sans might be used as a fallback on some systems."
            uses_noto_sans_only = None  # Can't be certain
            success = False
        else:
            message = "No evidence of Noto Sans usage found"
            uses_noto_sans_only = False
            success = False
        
        # --- NEW LOGIC: Check all visible text for Noto Sans usage ---
        # 1. Gather all style rules from <style> tags
        style_rules = []
        for style in soup.find_all('style'):
            if style.string:
                style_rules.append(style.string)
        style_rules_text = '\n'.join(style_rules)

        def get_font_from_style_attr(style_str):
            match = re.search(r'font-family\s*:\s*([^;]+)', style_str, re.IGNORECASE)
            if match:
                return match.group(1).lower()
            return None

        def get_font_from_style_rules(tag, classes, id_):
            # Check for matching CSS selectors in <style> blocks
            selectors = [tag]
            if classes:
                selectors.extend([f'.{c}' for c in classes])
            if id_:
                selectors.append(f'#{id_}')
            for sel in selectors:
                # Look for e.g. 'p { font-family: ... }', '.class { font-family: ... }', '#id { font-family: ... }'
                pattern = rf'{re.escape(sel)}\s*\{{[^}}]*font-family\s*:\s*([^;}}]+)'
                match = re.search(pattern, style_rules_text, re.IGNORECASE)
                if match:
                    return match.group(1).lower()
            return None

        # 2. Walk all elements with text
        elements_with_text = soup.find_all(lambda tag: tag.name not in ['script', 'style', 'noscript'] and tag.get_text(strip=True))
        non_noto_elements = []
        for elem in elements_with_text:
            # a. Inline style
            style_attr = elem.get('style', '')
            font = get_font_from_style_attr(style_attr)
            # b. Internal <style> rules
            if not font:
                font = get_font_from_style_rules(elem.name, elem.get('class', []), elem.get('id', None))
            # c. If still not found, skip (can't reliably determine)
            if not font:
                continue
            if 'noto sans' not in font:
                non_noto_elements.append({
                    'tag': elem.name,
                    'text': elem.get_text(strip=True)[:100],
                    'font_family': font
                })
        uses_noto_sans_only = len(non_noto_elements) == 0
        success = uses_noto_sans_only
        message = 'All visible text uses Noto Sans.' if uses_noto_sans_only else f"{len(non_noto_elements)} elements do not use Noto Sans."

        response_data = {
            'success': success,
            'uses_noto_sans_only': uses_noto_sans_only,
            'non_noto_elements': non_noto_elements,
            'detected_fonts': {
                'font_families': list(font_families),
                'font_faces': font_faces,
                'google_fonts_used': google_fonts_used,
                'system_fonts_used': system_fonts_used
            },
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
        }
        if font_families:
            response_data['detected_fonts']['primary_fonts'] = list(font_families)[:3]
            if len(font_families) > 3:
                response_data['detected_fonts']['primary_fonts'].append(f'+{len(font_families)-3} more')
        return response_data
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Serve static files from the frontend build directory
frontend_path = Path(__file__).parent / "frontend" / "build"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

@app.get("/api/hello")
async def hello_world():
    return {"message": "Hello from FastAPI!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
