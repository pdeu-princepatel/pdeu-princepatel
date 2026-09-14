import cv2
import base64
from pathlib import Path

def convert_face_to_bulletproof_svg(image_path: str = "my_face.png", output_path: str = "prince_config_diagnostics.svg"):
    # 1. Locate source image (check my_face.png, photo.png, etc.)
    p = Path(image_path)
    if not p.exists():
        for fallback in ["photo.png", "my_face.png", "portrait.png"]:
            if Path(fallback).exists():
                p = Path(fallback)
                break

    img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error: Could not locate portrait image at '{image_path}'.")
        return

    img_h, img_w = img.shape[:2]

    # Target bounding box inside the right panel (width: 310, height: 260)
    box_w = 310
    box_h = 265
    scale = min(box_w / img_w, box_h / img_h)
    face_w = int(img_w * scale)
    face_h = int(img_h * scale)

    # Downsample cleanly with Lanczos interpolation
    resized_img = cv2.resize(img, (face_w, face_h), interpolation=cv2.INTER_LANCZOS4)
    success, encoded_buffer = cv2.imencode('.png', resized_img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    if not success:
        print("Error: Failed to encode image.")
        return

    encoded_img = base64.b64encode(encoded_buffer).decode('utf-8')

    # Position portrait inside the right display frame
    panel_x = 500
    panel_y = 52
    face_x = panel_x + (box_w - face_w) // 2
    face_y = panel_y + (box_h - face_h) // 2

    # Dimensions of the whole card
    svg_w = 850
    svg_h = 390

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
  <title>Prince Patel — Profile Diagnostics &amp; Config</title>
  <defs>
    <!-- Background subtle gradient -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="50%" stop-color="#111827" />
      <stop offset="100%" stop-color="#0b0f17" />
    </linearGradient>

    <!-- Glowing accent gradient for border and badges -->
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="50%" stop-color="#818cf8" />
      <stop offset="100%" stop-color="#34d399" />
    </linearGradient>

    <!-- Clip path for rounded portrait window -->
    <clipPath id="portraitClip">
      <rect x="{panel_x}" y="{panel_y}" width="{box_w}" height="{box_h}" rx="12" ry="12" />
    </clipPath>

    <!-- Subtle cyber scanline grid overlay -->
    <pattern id="scanlines" width="6" height="6" patternUnits="userSpaceOnUse">
      <line x1="0" y1="5" x2="6" y2="5" stroke="#38bdf8" stroke-width="0.75" opacity="0.08" />
      <line x1="5" y1="0" x2="5" y2="6" stroke="#38bdf8" stroke-width="0.75" opacity="0.08" />
    </pattern>
  </defs>

  <style>
    .mono {{ font-family: "JetBrains Mono", "Fira Code", Consolas, monospace; }}
    .key {{ fill: #38bdf8; font-weight: 600; }}
    .str {{ fill: #34d399; }}
    .num {{ fill: #fbbf24; }}
    .bracket {{ fill: #818cf8; font-weight: bold; }}
    .comment {{ fill: #64748b; font-style: italic; }}
    .linenum {{ fill: #475569; font-size: 11px; text-anchor: end; user-select: none; }}
    .text-main {{ fill: #e2e8f0; font-size: 13px; }}
    .hud-label {{ fill: #94a3b8; font-size: 10px; font-weight: 600; letter-spacing: 1.5px; }}
    .badge-green {{ fill: #10b981; }}
  </style>

  <!-- Outer Window Container with Sleek Border -->
  <rect x="1" y="1" width="{svg_w - 2}" height="{svg_h - 2}" rx="12" fill="url(#bgGrad)" stroke="#30363d" stroke-width="1.5" />

  <!-- Window Header Bar -->
  <path d="M 1 13 C 1 6.5 6.5 1 13 1 L {svg_w - 13} 1 C {svg_w - 6.5} 1 {svg_w - 1} 6.5 {svg_w - 1} 13 L {svg_w - 1} 38 L 1 38 Z" fill="#161b22" stroke="#30363d" stroke-width="1" />

  <!-- Window Controls (Red, Yellow, Green traffic light dots) -->
  <circle cx="22" cy="19" r="6" fill="#ff5f56" />
  <circle cx="40" cy="19" r="6" fill="#ffbd2e" />
  <circle cx="58" cy="19" r="6" fill="#27c93f" />

  <!-- Active Tab Pill -->
  <rect x="80" y="8" width="190" height="24" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1" />
  <text x="96" y="24" class="mono" font-size="11" fill="#38bdf8">⚡ prince.config.json</text>

  <!-- Header Right Status Badge -->
  <circle cx="{svg_w - 110}" cy="19" r="4" class="badge-green" />
  <text x="{svg_w - 98}" y="23" class="mono hud-label" fill="#10b981">SYS // ACTIVE</text>

  <!-- Center Vertical Divider -->
  <line x1="475" y1="39" x2="475" y2="{svg_h - 1}" stroke="#21262d" stroke-dasharray="4 4" stroke-width="1.5" />

  <!-- LEFT PANEL: Code Editor Area -->
  <!-- Line Number Gutter -->
  <g class="mono linenum">
    <text x="36" y="70">1</text>
    <text x="36" y="93">2</text>
    <text x="36" y="116">3</text>
    <text x="36" y="139">4</text>
    <text x="36" y="162">5</text>
    <text x="36" y="185">6</text>
    <text x="36" y="208">7</text>
    <text x="36" y="231">8</text>
    <text x="36" y="254">9</text>
    <text x="36" y="277">10</text>
    <text x="36" y="300">11</text>
    <text x="36" y="323">12</text>
    <text x="36" y="346">13</text>
    <text x="36" y="369">14</text>
  </g>
  <line x1="45" y1="48" x2="45" y2="375" stroke="#21262d" stroke-width="1" />

  <!-- Code Syntax Block with Clean Indents -->
  <g class="mono text-main">
    <text x="55" y="70"><tspan class="bracket">&#123;</tspan></text>
    <text x="70" y="93"><tspan class="key">"name"</tspan>: <tspan class="str">"Prince Patel"</tspan>,</text>
    <text x="70" y="116"><tspan class="key">"title"</tspan>: <tspan class="str">"Backend &amp; Distributed Systems"</tspan>,</text>
    <text x="70" y="139"><tspan class="key">"core_stack"</tspan>: <tspan class="bracket">[</tspan><tspan class="str">"Golang"</tspan>, <tspan class="str">"Python"</tspan>, <tspan class="str">"Docker"</tspan><tspan class="bracket">]</tspan>,</text>
    <text x="70" y="162"><tspan class="key">"interests"</tspan>: <tspan class="bracket">[</tspan></text>
    <text x="95" y="185"><tspan class="str">"Distributed Caching"</tspan>,</text>
    <text x="95" y="208"><tspan class="str">"HCI (Human-Computer Interaction)"</tspan>,</text>
    <text x="95" y="231"><tspan class="str">"Data Science &amp; Systems"</tspan></text>
    <text x="70" y="254"><tspan class="bracket">]</tspan>,</text>
    <text x="70" y="277"><tspan class="key">"hobbies"</tspan>: <tspan class="bracket">[</tspan><tspan class="str">"Sketching"</tspan>, <tspan class="str">"Visualizing Ideas"</tspan><tspan class="bracket">]</tspan>,</text>
    <text x="70" y="300"><tspan class="key">"status"</tspan>: <tspan class="str">"building_next_gen"</tspan>,</text>
    <text x="70" y="323"><tspan class="key">"contributions"</tspan>: <tspan class="num">1</tspan>, <tspan class="comment">// PyShell &amp; Open Source</tspan></text>
    <text x="70" y="346"><tspan class="key">"philosophy"</tspan>: <tspan class="str">"Visualization helps understanding! 🧠"</tspan></text>
    <text x="55" y="369"><tspan class="bracket">&#125;</tspan></text>
  </g>

  <!-- RIGHT PANEL: Biometric Photographic Card -->
  <!-- HUD Header Label -->
  <text x="{panel_x}" y="47" class="mono hud-label" fill="#38bdf8">BIOMETRIC_MATRIX // IDENTITY_VERIFIED</text>

  <!-- Portrait Frame Background -->
  <rect x="{panel_x}" y="{panel_y}" width="{box_w}" height="{box_h}" rx="12" fill="#161b22" stroke="#30363d" stroke-width="1.5" />

  <!-- Photographic Cutout Layer inside ClipPath -->
  <g clip-path="url(#portraitClip)">
    <!-- Radial Ambient Backlight behind portrait -->
    <radialGradient id="faceGlow" cx="50%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.18" />
      <stop offset="60%" stop-color="#818cf8" stop-opacity="0.08" />
      <stop offset="100%" stop-color="#161b22" stop-opacity="0" />
    </radialGradient>
    <rect x="{panel_x}" y="{panel_y}" width="{box_w}" height="{box_h}" fill="url(#faceGlow)" />

    <!-- Embedded High-Definition Photo Cutout -->
    <image href="data:image/png;base64,{encoded_img}" x="{face_x}" y="{face_y}" width="{face_w}" height="{face_h}" preserveAspectRatio="xMidYMid meet" />

    <!-- Subtle Holographic Grid Pattern Overlay -->
    <rect x="{panel_x}" y="{panel_y}" width="{box_w}" height="{box_h}" fill="url(#scanlines)" />
  </g>

  <!-- Outer HUD Viewfinder Border -->
  <rect x="{panel_x}" y="{panel_y}" width="{box_w}" height="{box_h}" rx="12" fill="none" stroke="url(#accentGrad)" stroke-width="1.5" />

  <!-- Cyber Viewfinder Corner Accents -->
  <path d="M {panel_x + 2} {panel_y + 16} L {panel_x + 2} {panel_y + 2} L {panel_x + 16} {panel_y + 2}" fill="none" stroke="#38bdf8" stroke-width="2.5" />
  <path d="M {panel_x + box_w - 16} {panel_y + 2} L {panel_x + box_w - 2} {panel_y + 2} L {panel_x + box_w - 2} {panel_y + 16}" fill="none" stroke="#38bdf8" stroke-width="2.5" />
  <path d="M {panel_x + 2} {panel_y + box_h - 16} L {panel_x + 2} {panel_y + box_h - 2} L {panel_x + 16} {panel_y + box_h - 2}" fill="none" stroke="#38bdf8" stroke-width="2.5" />
  <path d="M {panel_x + box_w - 16} {panel_y + box_h - 2} L {panel_x + box_w - 2} {panel_y + box_h - 2} L {panel_x + box_w - 2} {panel_y + box_h - 16}" fill="none" stroke="#38bdf8" stroke-width="2.5" />

  <!-- Bottom Telemetry Status Bar -->
  <rect x="{panel_x}" y="{panel_y + box_h + 12}" width="{box_w}" height="42" rx="8" fill="#161b22" stroke="#30363d" stroke-width="1" />
  <circle cx="{panel_x + 18}" cy="{panel_y + box_h + 33}" r="4" fill="#34d399" />
  <text x="{panel_x + 30}" y="{panel_y + box_h + 28}" class="mono" font-size="10" font-weight="bold" fill="#38bdf8">SYS_STATUS: READY</text>
  <text x="{panel_x + 30}" y="{panel_y + box_h + 43}" class="mono" font-size="9" fill="#94a3b8">ENGINEER_ID: PATEL_PRINCE // 2026</text>
</svg>'''

    Path(output_path).write_text(svg_content, encoding="utf-8")
    print(f"Success! High-Fidelity SVG written to: {Path(output_path).resolve()} ({len(svg_content)} bytes)")

if __name__ == "__main__":
    convert_face_to_bulletproof_svg("my_face.png", "prince_config_diagnostics.svg")
