import math
from pathlib import Path

def generate_cube_svg(output_path: str = "linkedin_cube.svg"):
    # Cube parameters
    size = 80
    distance = 320
    fov = 360
    cx = 250
    cy = 230

    def project(x, y, z):
        sz = z + distance
        return ((x * fov) / sz + cx, (y * fov) / sz + cy, sz)

    # 1. Cube 8 vertices
    points = [
        [-size, -size, -size], [size, -size, -size], [size, size, -size], [-size, size, -size],
        [-size, -size, size],  [size, -size, size],  [size, size, size],  [-size, size, size]
    ]

    # 12 wireframe edges
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0), # Back Face
        (4, 5), (5, 6), (6, 7), (7, 4), # Front Face
        (0, 4), (1, 5), (2, 6), (3, 7)  # Connecting struts
    ]

    # 2. Template for the recognizable LinkedIn "in" logo
    logo_elements = []
    # Letter 'i':
    # Dot
    logo_elements.append({'x': -32, 'y': -42, 'char': '■', 'is_logo': True})
    logo_elements.append({'x': -32, 'y': -32, 'char': '■', 'is_logo': True})
    # Stem
    for y in range(-12, 45, 11):
        logo_elements.append({'x': -32, 'y': y, 'char': '█', 'is_logo': True})

    # Letter 'n':
    # Left stem
    for y in range(-12, 45, 11):
        logo_elements.append({'x': -8, 'y': y, 'char': '█', 'is_logo': True})
    # Curved arch top
    logo_elements.append({'x': 3, 'y': -14, 'char': '▀', 'is_logo': True})
    logo_elements.append({'x': 14, 'y': -14, 'char': '▀', 'is_logo': True})
    logo_elements.append({'x': 25, 'y': -10, 'char': '▄', 'is_logo': True})
    # Right stem
    for y in range(-2, 45, 11):
        logo_elements.append({'x': 25, 'y': y, 'char': '█', 'is_logo': True})

    # 3. Template for the decorative matrix panels
    blue_face_template = []
    for y in range(-40, 45, 18):
        for x in range(-40, 45, 20):
            blue_face_template.push({'x': x, 'y': y, 'char': '░'}) if hasattr(blue_face_template, 'push') else blue_face_template.append({'x': x, 'y': y, 'char': '░'})

    # 4. Map faces to 4 sides of the cube
    face_elements = []
    # Face 0: Front Face (Z = +size) -> "in" Logo
    for p in logo_elements:
        face_elements.append({'origX': p['x'], 'origY': p['y'], 'origZ': size, 'char': p['char'], 'type': 'logo', 'is_logo': p['is_logo']})

    # Face 1: Right Face (X = +size) -> Matrix Grid
    for p in blue_face_template:
        face_elements.append({'origX': size, 'origY': p['y'], 'origZ': -p['x'], 'char': p['char'], 'type': 'blue', 'is_logo': False})

    # Face 2: Back Face (Z = -size) -> "in" Logo
    for p in logo_elements:
        face_elements.append({'origX': -p['x'], 'origY': p['y'], 'origZ': -size, 'char': p['char'], 'type': 'logo', 'is_logo': p['is_logo']})

    # Face 3: Left Face (X = -size) -> Matrix Grid
    for p in blue_face_template:
        face_elements.append({'origX': -size, 'origY': p['y'], 'origZ': p['x'], 'char': p['char'], 'type': 'blue', 'is_logo': False})

    # 5. Generate 36 frames for smooth 360-degree rotation (4.5 seconds total, lightweight & fast)
    num_frames = 36
    total_dur = 4.5
    frames_svg = []

    for f_idx in range(num_frames):
        angle = (f_idx / num_frames) * (2 * math.pi)
        cos_y = math.cos(angle)
        sin_y = math.sin(angle)

        render_queue = []

        # Wireframe edges
        segments = 6
        for p1_idx, p2_idx in edges:
            p1 = points[p1_idx]
            p2 = points[p2_idx]
            for s in range(segments + 1):
                t = s / segments
                x = p1[0] + (p2[0] - p1[0]) * t
                y = p1[1] + (p2[1] - p1[1]) * t
                z = p1[2] + (p2[2] - p1[2]) * t

                # Rotate around Y
                rx = x * cos_y + z * sin_y
                rz = -x * sin_y + z * cos_y

                px, py, pz = project(rx, y, rz)
                char = '+' if (s == 0 or s == segments) else '·'
                opacity = max(0.12, (rz + 120) / 240.0)

                render_queue.append({
                    'z': pz,
                    'html': f'<text x="{px:.1f}" y="{py:.1f}" fill="#0077B5" font-size="9" opacity="{opacity:.2f}">{char}</text>'
                })

        # Face elements
        for p in face_elements:
            rx = p['origX'] * cos_y + p['origZ'] * sin_y
            rz = -p['origX'] * sin_y + p['origZ'] * cos_y

            # Backface culling: only draw faces that have z > -40 to keep it clean and lightweight!
            if rz < -45:
                continue

            px, py, pz = project(rx, p['origY'], rz)
            base_opacity = max(0.2, (rz + 90) / 200.0)

            if p['type'] == 'logo':
                color = '#ffffff' if p['is_logo'] else '#0077B5'
                opacity = max(0.4, base_opacity)
                font_size = 15
            else:
                color = '#0077B5'
                opacity = base_opacity * 0.6
                font_size = 11

            render_queue.append({
                'z': pz,
                'html': f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{font_size}" font-weight="bold" opacity="{opacity:.2f}">{p["char"]}</text>'
            })

        # Sort back-to-front
        render_queue.sort(key=lambda item: item['z'])

        elements_str = "\n      ".join([item['html'] for item in render_queue])
        frames_svg.append(f'    <g class="cube-frame f{f_idx}">\n      {elements_str}\n    </g>')

    # Generate CSS rules for all frames
    frame_step_pct = 100.0 / num_frames
    delay_rules = []
    for i in range(num_frames):
        delay = i * (total_dur / num_frames)
        delay_rules.append(f'    .f{i} {{ animation-delay: {delay:.3f}s; }}')
    delay_css = "\n".join(delay_rules)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="480" height="500" viewBox="0 0 480 500">
  <title>Prince Patel — 3D Rotating ASCII LinkedIn Profile</title>
  <defs>
    <radialGradient id="linkedInGlow" cx="50%" cy="46%" r="50%">
      <stop offset="0%" stop-color="#0077B5" stop-opacity="0.25" />
      <stop offset="60%" stop-color="#0077B5" stop-opacity="0.08" />
      <stop offset="100%" stop-color="#050b14" stop-opacity="0" />
    </radialGradient>
  </defs>

  <style>
    .mono {{ font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace; }}
    .cube-frame {{
      opacity: 0;
      animation: rotatePlay {total_dur}s infinite step-start;
    }}
    @keyframes rotatePlay {{
      0%   {{ opacity: 1; }}
      {frame_step_pct:.4f}% {{ opacity: 0; }}
      100% {{ opacity: 0; }}
    }}
{delay_css}
    .hover-card:hover .btn-box {{
      fill: #0077B5;
      stroke: #38bdf8;
    }}
    .hover-card:hover .btn-text {{
      fill: #ffffff;
    }}
  </style>

  <!-- Interactive Link Wrapping Entire Card -->
  <a href="https://www.linkedin.com/in/prince-patel-844625282" target="_blank" class="hover-card" style="cursor: pointer;">
    <!-- Background Card -->
    <rect width="100%" height="100%" fill="#050b14" rx="14" stroke="#0077B5" stroke-opacity="0.35" stroke-width="1.5" />
    <rect width="100%" height="100%" fill="url(#linkedInGlow)" rx="14" />

    <!-- Terminal Header Info -->
    <circle cx="24" cy="24" r="4" fill="#0077B5" />
    <text x="36" y="28" class="mono" font-size="11" font-weight="bold" fill="#0077B5" letter-spacing="1">LINKEDIN // MATRIX_CORE</text>
    <text x="445" y="28" class="mono" font-size="10" fill="#00ff9c" text-anchor="end">● ACTIVE</text>
    <line x1="15" y1="42" x2="465" y2="42" stroke="#0077B5" stroke-opacity="0.2" stroke-width="1" />

    <!-- 3D Rotating Cube Render Target -->
    <g font-family="monospace" text-anchor="middle" dominant-baseline="central">
{chr(10).join(frames_svg)}
    </g>

    <!-- Subtitle Meta -->
    <text x="240" y="415" class="mono" font-size="10" fill="#0077B5" opacity="0.6" text-anchor="middle" letter-spacing="1">Y-AXIS CONTINUOUS 3D ASCII ROTATION</text>

    <!-- Interactive Call-To-Action Button -->
    <g>
      <rect class="btn-box" x="110" y="435" width="260" height="36" rx="8" fill="#0c1a2e" stroke="#0077B5" stroke-width="1.2" />
      <text class="btn-text mono" x="240" y="458" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle">CONNECT ON LINKEDIN ↗</text>
    </g>
  </a>
</svg>
'''

    Path(output_path).write_text(svg_content, encoding="utf-8")
    print(f"Success! 3D Rotating ASCII LinkedIn SVG created at: {Path(output_path).resolve()} ({len(svg_content)} bytes)")

if __name__ == "__main__":
    generate_cube_svg("linkedin_cube.svg")
