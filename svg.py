import cv2
import base64
import numpy as np
from pathlib import Path

def convert_face_to_bulletproof_svg(
    ascii_path: str = "ascii_face.png",
    real_path: str = "my_face.png",
    output_path: str = "prince_config_diagnostics.svg"
):
    # 1. Load ASCII face
    ascii_p = Path(ascii_path)
    if not ascii_p.exists():
        for fallback in ["ascii_face.png", "media_1789416526374.png"]:
            if Path(fallback).exists():
                ascii_p = Path(fallback)
                break

    ascii_img = cv2.imread(str(ascii_p), cv2.IMREAD_UNCHANGED)
    if ascii_img is None:
        print(f"Error: Could not locate ASCII image '{ascii_path}'.")
        return

    # Load Real photo
    real_p = Path(real_path)
    if not real_p.exists():
        for fallback in ["my_face.png", "photo.png", "portrait.png"]:
            if Path(fallback).exists():
                real_p = Path(fallback)
                break

    real_img = cv2.imread(str(real_p), cv2.IMREAD_UNCHANGED)
    if real_img is None:
        print(f"Error: Could not locate real photo '{real_path}'.")
        return

    # Crop empty transparent padding from ASCII image
    a_alpha = ascii_img[:, :, 3] if ascii_img.shape[2] == 4 else np.ones(ascii_img.shape[:2], dtype=np.uint8) * 255
    a_coords = cv2.findNonZero(a_alpha)
    if a_coords is not None:
        ax, ay, aw, ah = cv2.boundingRect(a_coords)
        a_cropped = ascii_img[ay:ay+ah, ax:ax+aw]
    else:
        a_cropped = ascii_img

    # Crop real photo to matching head & shoulders bounds
    r_alpha = real_img[:, :, 3] if real_img.shape[2] == 4 else np.ones(real_img.shape[:2], dtype=np.uint8) * 255
    r_coords = cv2.findNonZero(r_alpha)
    if r_coords is not None:
        rx, ry, rw, rh = cv2.boundingRect(r_coords)
        r_cropped = real_img[ry:ry+rh, rx:rx+rw]
    else:
        r_cropped = real_img

    # Target frame bounding box inside right panel area
    box_w = 340
    box_h = 270

    img_h, img_w = a_cropped.shape[:2]
    scale = min(box_w / img_w, box_h / img_h)
    face_w = int(img_w * scale)
    face_h = int(img_h * scale)

    # Resize both layers to identical dimensions for seamless morph alignment
    a_resized = cv2.resize(a_cropped, (face_w, face_h), interpolation=cv2.INTER_LANCZOS4)
    r_resized = cv2.resize(r_cropped, (face_w, face_h), interpolation=cv2.INTER_LANCZOS4)

    # Enhance ASCII brightness so characters pop on dark canvas
    hsv = cv2.cvtColor(a_resized[:, :, :3], cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.6 + 45, 0, 255)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.1, 0, 255)
    bright_bgr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    a_enhanced = np.dstack([bright_bgr, a_resized[:, :, 3]])

    # Compress both images to PNG
    _, a_buf = cv2.imencode('.png', a_enhanced, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    _, r_buf = cv2.imencode('.png', r_resized, [cv2.IMWRITE_PNG_COMPRESSION, 9])

    encoded_ascii = base64.b64encode(a_buf).decode('utf-8')
    encoded_real = base64.b64encode(r_buf).decode('utf-8')

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
    parts.append('    .ascii-face { animation: asciiCycle 8s ease-in-out infinite; }')
    parts.append('    .real-face  { animation: realCycle 8s ease-in-out infinite; }')
    parts.append('    .scan-beam  { animation: beamSweep 8s ease-in-out infinite; }')
    parts.append('    @keyframes asciiCycle {')
    parts.append('      0%, 55%   { opacity: 1; }')
    parts.append('      65%, 85%  { opacity: 0; }')
    parts.append('      93%, 100% { opacity: 1; }')
    parts.append('    }')
    parts.append('    @keyframes realCycle {')
    parts.append('      0%, 55%   { opacity: 0; }')
    parts.append('      65%, 85%  { opacity: 1; }')
    parts.append('      93%, 100% { opacity: 0; }')
    parts.append('    }')
    parts.append('    @keyframes beamSweep {')
    parts.append('      0%, 54%    { opacity: 0; transform: translateY(0); }')
    parts.append('      56%        { opacity: 0.95; transform: translateY(0); }')
    parts.append(f'      66%        {{ opacity: 0.95; transform: translateY({face_h}px); }}')
    parts.append(f'      68%, 84%   {{ opacity: 0; transform: translateY({face_h}px); }}')
    parts.append(f'      86%        {{ opacity: 0.95; transform: translateY({face_h}px); }}')
    parts.append('      94%        { opacity: 0.95; transform: translateY(0); }')
    parts.append('      96%, 100%  { opacity: 0; transform: translateY(0); }')
    parts.append('    }')
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

    # 3. Right Side Face Render Section: ASCII + Real Face with Laser Scan Transition
    parts.append(f'  <g id="portrait-group">')
    # Layer 1: ASCII Face
    parts.append(f'    <image class="ascii-face" href="data:image/png;base64,{encoded_ascii}" x="{face_x}" y="{face_y}" width="{face_w}" height="{face_h}" />')
    # Layer 2: Real Photographic Cutout
    parts.append(f'    <image class="real-face" href="data:image/png;base64,{encoded_real}" x="{face_x}" y="{face_y}" width="{face_w}" height="{face_h}" />')
    # Layer 3: Cyan/Emerald Laser Scan Beam Sweep
    parts.append(f'    <line class="scan-beam" x1="{face_x}" y1="{face_y}" x2="{face_x + face_w}" y2="{face_y}" stroke="#00ff9c" stroke-width="2" stroke-linecap="round" />')
    parts.append('  </g>')

    # Telemetry Status Bar Footer Metrics Box
    parts.append('  <rect x="475" y="335" width="355" height="30" fill="#111827" rx="4" stroke="#1e293b" stroke-width="1"/>')
    parts.append('  <text x="485" y="354" font-size="10" class="mid">SYS_STATUS:</text>')
    parts.append('  <text x="570" y="354" font-size="10" class="bright">VISUALIZATION == UNDERSTANDING</text>')
    parts.append('</svg>')

    Path(output_path).write_text("\n".join(parts), encoding="utf-8")
    print(f"Success! Terminal SVG with seamless ASCII-to-Photo transition generated at: {Path(output_path).resolve()}")

if __name__ == "__main__":
    convert_face_to_bulletproof_svg("ascii_face.png", "my_face.png", "prince_config_diagnostics.svg")
