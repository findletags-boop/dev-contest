
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
