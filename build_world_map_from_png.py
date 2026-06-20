from PIL import Image
import numpy as np
import json

# =====================================================
# CONFIG
# =====================================================

IMAGE_PATH = "map.png"      # input PNG

GRID_LEFT = 152
GRID_TOP = 90

CELL_SIZE = 12

SQUARE_SIZE = 8.4

ALPHA_THRESHOLD = 20

MAP_W = 2200
MAP_H = 1200

# =====================================================

img = Image.open(IMAGE_PATH).convert("RGBA")
arr = np.array(img)

h, w = arr.shape[:2]

cols = int(round((w - GRID_LEFT) / CELL_SIZE))
rows = int(round((h - GRID_TOP) / CELL_SIZE))

occupied = []

for row in range(rows):
    for col in range(cols):

        cell_x = GRID_LEFT + col * CELL_SIZE
        cell_y = GRID_TOP + row * CELL_SIZE

        x1 = int(cell_x + 1)
        y1 = int(cell_y + 1)
        x2 = int(min(cell_x + CELL_SIZE - 1, w))
        y2 = int(min(cell_y + CELL_SIZE - 1, h))

        region = arr[y1:y2, x1:x2, 3]

        if region.size == 0:
            continue

        if np.max(region) > ALPHA_THRESHOLD:
            occupied.append([row, col])

print(f"Detected {len(occupied)} occupied grid cells")

min_col = min(col for row, col in occupied)
max_col = max(col for row, col in occupied)

min_row = min(row for row, col in occupied)
max_row = max(row for row, col in occupied)

content_left = GRID_LEFT + min_col * CELL_SIZE
content_right = GRID_LEFT + max_col * CELL_SIZE + SQUARE_SIZE

content_top = GRID_TOP + min_row * CELL_SIZE
content_bottom = GRID_TOP + max_row * CELL_SIZE + SQUARE_SIZE

content_width = content_right - content_left
content_height = content_bottom - content_top

target_left = (MAP_W - content_width) / 2
target_top = (MAP_H - content_height) / 2

offset_x = target_left - content_left
offset_y = target_top - content_top

print("Content left:", content_left)
print("Content right:", content_right)
print("Content width:", content_width)

print("Offset X:", offset_x)

with open("occupied_cells.json", "w") as f:
    json.dump(occupied, f)

# =====================================================
# BUILD HTML
# =====================================================

css = """

* {
    margin:0;
    padding:0;
    box-sizing:border-box;
}

html,
body {
    width:100%;
    height:100%;
    overflow:hidden;
    background:white;
}

.viewport {

    width:100vw;
    height:100vh;

    overflow:hidden;

    display:flex;
    justify-content:center;
    align-items:center;

    touch-action:none;
}

#map {
    
    position:relative;

    width:2200px;
    height:1030px;
    transform-origin:center center;
    will-change:transform;
}

.pixel {

    position:absolute;

    width:8.4px;
    height:8.4px;

    background:#d8d8d8;
}
"""

with open("style.css", "w") as f:
    f.write(css)

# ---------- JS ----------
js = """
const map = document.getElementById("map");

const MAP_W = 2200;
const MAP_H = 1200;

const IS_MOBILE = window.innerWidth < 768;

let baseScale = 1;

let minZoom = IS_MOBILE ? 0.6 : 1;
let zoom = IS_MOBILE ? 2 : 1;
let firstZoom = true;

let x = -window.innerWidth * 0.1;
let y = 0;

let dragging = false;

let lastX = 0;
let lastY = 0;

let pinchDistance = null;

function fitMapToPixels() {

    let maxRight = 0;
    let maxBottom = 0;

    document.querySelectorAll(".pixel").forEach(pixel => {

        const left =
            parseFloat(pixel.style.left) || 0;

        const top =
            parseFloat(pixel.style.top) || 0;

        const right =
            left + pixel.offsetWidth;

        const bottom =
            top + pixel.offsetHeight;

        maxRight =
            Math.max(maxRight, right);

        maxBottom =
            Math.max(maxBottom, bottom);

    });

    map.style.width =
        `${Math.ceil(maxRight)}px`;

    map.style.height =
        `${Math.ceil(maxBottom)}px`;

}

function clampZoom(z) {

    return Math.max(
        minZoom,
        Math.min(10, z)
    );

}

function updateTransform() {

    map.style.transform =
        `translate(${x}px, ${y}px) scale(${baseScale * zoom})`;

}

function fitMap() {

    const scaleX =
        (window.innerWidth * 0.85) /
        MAP_W;

    const scaleY =
        (window.innerHeight * 0.85) /
        MAP_H;

    baseScale =
        Math.min(scaleX, scaleY);

    updateTransform();

}

fitMap();

window.addEventListener(
    "resize",
    fitMap
);

// WHEEL ZOOM
window.addEventListener(
    "wheel",
    e => {

        e.preventDefault();

        const newZoom =
            clampZoom(
                zoom *
                (1 - e.deltaY * 0.0015)
            );

        if(newZoom === zoom)
            return;

        zoom = newZoom;

        updateTransform();

    },
    { passive:false }
);

// MOUSE DRAG
map.addEventListener(
    "mousedown",
    e => {

        dragging = true;

        lastX = e.clientX;
        lastY = e.clientY;

    }
);

window.addEventListener(
    "mouseup",
    () => {

        dragging = false;

    }
);

window.addEventListener(
    "mousemove",
    e => {

        if(!dragging)
            return;

        x += e.clientX - lastX;
        y += e.clientY - lastY;

        lastX = e.clientX;
        lastY = e.clientY;

        updateTransform();

    }
);

// TOUCH HELPERS
function distance(t1, t2) {

    const dx =
        t1.clientX - t2.clientX;

    const dy =
        t1.clientY - t2.clientY;

    return Math.sqrt(
        dx * dx +
        dy * dy
    );

}

// TOUCH START
map.addEventListener(
    "touchstart",
    e => {

        if(e.touches.length === 1) {

            if(zoom <= minZoom)
                return;

            dragging = true;

            lastX =
                e.touches[0].clientX;

            lastY =
                e.touches[0].clientY;

        }

        if(e.touches.length === 2) {

            dragging = false;

            pinchDistance =
                distance(
                    e.touches[0],
                    e.touches[1]
                );

        }

    },
    { passive:false }
);

// TOUCH MOVE
map.addEventListener(
    "touchmove",
    e => {

        e.preventDefault();

        if(
            e.touches.length === 1 &&
            dragging
        ) {

            x +=
                e.touches[0].clientX -
                lastX;

            y +=
                e.touches[0].clientY -
                lastY;

            lastX =
                e.touches[0].clientX;

            lastY =
                e.touches[0].clientY;

            updateTransform();

        }

        if(e.touches.length === 2) {

            const d =
                distance(
                    e.touches[0],
                    e.touches[1]
                );

            if(pinchDistance) {

                const newZoom =
                    clampZoom(
                        zoom *
                        (d / pinchDistance)
                    );

                if(newZoom !== zoom) {

                    zoom = newZoom;

                    updateTransform();

                }

            }

            pinchDistance = d;

        }

    },
    { passive:false }
);

// TOUCH END
map.addEventListener(
    "touchend",
    () => {

        dragging = false;
        pinchDistance = null;

    }
);
"""

with open("script.js", "w") as f:
    f.write(js)

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>World Map</title>
<link rel="stylesheet" href="style.css">

</head>

<body>

<div class="viewport">
<div id="map">
"""

for row, col in occupied:

    left = (
        col * CELL_SIZE
        + (CELL_SIZE - SQUARE_SIZE)/2
    )

    top = (
        row * CELL_SIZE
        + (CELL_SIZE - SQUARE_SIZE)/2
    )

    html += (
        f'<div class="pixel" '
        f'style="left:{left}px;'
        f'top:{top}px"></div>\n'
    )

html += f"""
</div>
</div>

<script src="script.js"></script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Created: occupied_cells.json")
print("Created: index.html")
print("Created: style.css")
print("Created: script.js")