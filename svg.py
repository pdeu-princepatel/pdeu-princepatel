import cv2
import base64
import numpy as np
from pathlib import Path

def convert_face_to_bulletproof_svg(image_path: str = "ascii_face.png", output_path: str = "prince_config_diagnostics.svg"):
    p = Path(image_path)
    if not p.exists():
        for fallback in ["ascii_face.png", "media_1789416526374.png", "my_face.png"]:
            if Path(fallback).exists():
                p = Path(fallback)
                break

    img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error: Could not locate portrait source image '{image_path}'.")
        return

    # Crop empty transparent padding around the ASCII art
    alpha = img[:, :, 3] if img.shape[2] == 4 else np.ones(img.shape[:2], dtype=np.uint8) * 255
    coords = cv2.findNonZero(alpha)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        cropped = img[y:y+h, x:x+w]
    else:
        cropped = img

    # Target frame bounding box setup for the right panel area mapping
    box_w = 340
    box_h = 270

    # Calculate scale factors to fit inside the display box area gracefully
    img_h, img_w = cropped.shape[:2]
    scale = min(box_w / img_w, box_h / img_h)
    face_w = int(img_w * scale)
    face_h = int(img_h * scale)

    # Downsample the image dimensions with Lanczos interpolation
    resized_img = cv2.resize(cropped, (face_w, face_h), interpolation=cv2.INTER_LANCZOS4)

    # Enhance luminance so the ASCII characters pop vividly on the dark terminal canvas
    hsv = cv2.cvtColor(resized_img[:, :, :3], cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.6 + 45, 0, 255)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.1, 0, 255)
    bright_bgr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    enhanced_img = np.dstack([bright_bgr, resized_img[:, :, 3]])

    # Compress the downsampled image matrix to high-quality PNG bytes
    success, encoded_buffer = cv2.imencode('.png', enhanced_img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    if not success:
        print("Error: Failed to compress image bytes.")
        return

    # Encode the lightweight byte layer to Base64 text
    encoded_img = base64.b64encode(encoded_buffer).decode('utf-8')

    # Center alignment coordinates inside the right window panel area
    face_x = 485 + (box_w - face_w) // 2
    face_y = 50 + (box_h - face_h) // 2

    # 2. Design system theme layout color parameters (User's exact original styling)
    json_key = "#38bdf8"
    json_val = "#fbbf24"
    json_str = "#34d399"
    text_dim = "#006b50"
    text_mid = "#00b879"
    text_green = "#00ff9c"

    parts = []
    # Standard W3C SVG namespace
    parts.append('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="850" height="380" viewBox="0 0 850 380">')
    parts.append('  <title>Prince Patel — Custom Portrait Profile</title>')
    parts.append('  <style>')
    parts.append('    text { font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace; font-weight: 700; }')
    parts.append(f'    .key {{ fill: {json_key}; }} .val {{ fill: {json_val}; }} .str {{ fill: {json_str}; }}')
    parts.append(f'    .dim {{ fill: {text_dim}; }} .mid {{ fill: {text_mid}; }} .bright {{ fill: {text_green}; }}')
    parts.append('  </style>')

    # Background Canvas Box Setup
    parts.append('  <rect width="100%" height="100%" fill="#0b0f19" rx="8" stroke="#1e293b" stroke-width="1.5"/>')

    # Left IDE window decorations & headers
    parts.append('  <circle cx="25" cy="20" r="5" fill="#ef4444" opacity="0.8"/>')
    parts.append('  <circle cx="40" cy="20" r="5" fill="#f59e0b" opacity="0.8"/>')
    parts.append('  <circle cx="55" cy="20" r="5" fill="#10b981" opacity="0.8"/>')
    parts.append('  <text x="75" y="24" font-size="11" class="dim">prince.config — Editor</text>')

    # Left Panel Content: Editor config metrics schema
    parts.append('  <g font-size="13" fill="#e2e8f0" xml:space="preserve">')
    parts.append('    <text x="25" y="55"><tspan class="bright">{</tspan></text>')
    parts.append('    <text x="25" y="75">  <tspan class="key">"core_interests"</tspan>: <tspan class="bright">[</tspan></text>')
    parts.append('    <text x="25" y="95">    <tspan class="str">"Golang"</tspan>,</text>')
    parts.append('    <text x="25" y="115">    <tspan class="str">"Human-Computer Interaction (HCI)"</tspan>,</text>')
    parts.append('    <text x="25" y="135">    <tspan class="str">"Data Science"</tspan></text>')
    parts.append('    <text x="25" y="155">  <tspan class="bright">]</tspan>,</text>')
    parts.append('    <text x="25" y="175">  <tspan class="key">"current_sprint"</tspan>: <tspan class="bright">{</tspan></text>')
    parts.append('    <text x="25" y="195">    <tspan class="key">"learning"</tspan>: <tspan class="str">"Distributed Caching"</tspan>,</text>')
    parts.append('    <text x="25" y="215">    <tspan class="key">"status"</tspan>: <tspan class="val">"in_progress"</tspan></text>')
    parts.append('    <text x="25" y="235">  <tspan class="bright">}</tspan>,</text>')
    parts.append('    <text x="25" y="255">  <tspan class="key">"background_tasks"</tspan>: <tspan class="bright">[</tspan> <tspan class="str">"Sketching"</tspan>, <tspan class="str">"Visualizing"</tspan> <tspan class="bright">]</tspan>,</text>')
    parts.append('    <text x="25" y="275">  <tspan class="key">"system_log"</tspan>: <tspan class="str">"Visualization helps understanding!"</tspan></text>')
    parts.append('    <text x="25" y="295"><tspan class="bright">}</tspan></text>')
    parts.append('  </g>')

    # Center Split panel dividers
    parts.append('  <line x1="455" y1="15" x2="455" y2="365" stroke="#1e293b" stroke-dasharray="4 4" stroke-width="1.5"/>')
    parts.append('  <text x="475" y="32" font-size="11" class="bright" letter-spacing="1">USER_PROFILE_MATRIX // IMAGE_MATRIX_RENDER</text>')

    # 3. Right Side Face Render Section: Embedded ASCII Art Image
    parts.append(f'  <image href="data:image/png;base64,{encoded_img}" x="{face_x}" y="{face_y}" width="{face_w}" height="{face_h}" />')

    # Telemetry Status Bar Footer Metrics Box
    parts.append('  <rect x="475" y="335" width="355" height="30" fill="#111827" rx="4" stroke="#1e293b" stroke-width="1"/>')
    parts.append('  <text x="485" y="354" font-size="10" class="mid">SYS_STATUS:</text>')
    parts.append('  <text x="570" y="354" font-size="10" class="bright">VISUALIZATION == UNDERSTANDING</text>')
    parts.append('</svg>')

    Path(output_path).write_text("\n".join(parts), encoding="utf-8")
    print(f"Success! Terminal SVG with ASCII art generated at: {Path(output_path).resolve()}")

if __name__ == "__main__":
    convert_face_to_bulletproof_svg("ascii_face.png", "prince_config_diagnostics.svg")
