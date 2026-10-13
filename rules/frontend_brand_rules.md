# Frontend, UI Design and Personal Brand High Priority Rules

These hard invariants govern all user interface engineering, WebGL 3D graphics, CSS architecture, and media processing. Every rule addresses documented bugs and design critiques from historical sessions.

***

## 1. Prohibition of Cheap Generic CSS Cards

### Problem
The model built flat rectangular cards with thin grey borders, uniform padding, and static plus icons, producing a generic, low quality appearance.

### Idrees's Solution
"the cards are still very ugly, i want them very high quality, your task was to use provided website trioon as a template... copy exact cards of something high quality 3d website"
"Banned: Cheap generic CSS cards. TRIONN cards are large, luxury, visually layered showcases with deep shadows, subtle inner bevel highlights, rich dark graphite surfaces, and pill tags."

### Enki's Proposed Solution
Enforce deep multi surface color tokens (`--bg-surface: #0A0B0E`, `--bg-card: #0E0F12`), inner bevel highlights, hairline borders with subtle opacity, and dynamic 3D tilt tracking with interactive specular glare overlays.

***

## 2. Prohibition of Cheap Wireframe 3D Elements

### Problem
The model injected an aggressive spinning wireframe icosahedron into the background, creating a distracting, amateurish aesthetic.

### Idrees's Solution
"there is no 3d floating, I want high quality 3d floating... the things you used 3d structure behind is bullshit... all the background structures, find a structures that moves with a normal speed in background throught out the whole website"

### Enki's Proposed Solution
All WebGL canvases must use production grade shaders: the dark metallic architectural prism monolith in `engine3d.js`, featuring chamfered titanium blocks, amber top rim lighting, cyan side specular fill, and smooth damped mouse parallax.

***

## 3. Purge of Creepy AI Voiceover Phrasing

### Problem
The model placed badges on video showcases reading "Play Screencast with AI Voiceover", triggering negative user perception.

### Idrees's Solution
"the button saying click to watch full video with voiceover, or something same, I dont want the part voiceover it's creepy and I also want pop out for the main page agentic workflows"

### Enki's Proposed Solution
Completely ban the word "voiceover" across all HTML files, scripts, and CSS. Use professional media labels: "Watch Full Video Screencast", "Full Demo · 74s Production Cut", or "Video Demonstration".

***

## 4. Defensive CSS Bounding on All Media Assets

### Problem
Inserting raw 1024x1024 source PNGs into headers without enclosing CSS bounding classes caused the image to render at full resolution, blowing out the navigation bar across the screen.

### Idrees's Solution
None provided by Idrees (Bugs caught during visual verification in commit `3be8d68`).

### Enki's Proposed Solution
Mandatory defensive CSS rules in `styles.css`. Every logo, brand mark, and screenshot must be wrapped in a strictly bounded container (such as `.header-logo-box` with explicit 32px constraints and `object-fit: cover`).

***

## 5. Prohibition of Broken Mailto Form Handlers

### Problem
The model built contact forms using standard `<form action="mailto:...">` tags, which caused mobile browsers to launch local mail client apps rather than submitting form data.

### Idrees's Solution
"Banned: Broken or fake contact forms. The form must connect directly to a working backend via FormSubmit AJAX with real time in place status feedback and a one click WhatsApp fallback."

### Enki's Proposed Solution
All contact forms must execute via asynchronous JavaScript `onsubmit` handlers submitting to FormSubmit AJAX, coupled with immediate in page status modal feedback and a direct WhatsApp fallback channel (+923489911425).

***

## 6. Prohibition of Aggressive Center Zoom Video Cropping

### Problem
When converting 16:9 widescreen videos to 9:16 vertical shorts, the model applied aggressive center cropping that sliced off presenter faces and subtitles.

### Idrees's Solution
"fuck you mother fucker, just put the raw video without cropping between the 9:16 frame"

### Enki's Proposed Solution
Never center zoom crop wide video into vertical frames. Use professional letterboxing or blurred side canvas duplication, keeping the complete original 16:9 video frame visible in the center of the 9:16 container.

***

## 7. Bidirectional Continuous Magnetic Scroll Spawn

### Problem
Using basic `IntersectionObserver` with an unobserve command caused scroll animations to run only once upon initial page load, leaving the layout completely static when scrolling back up.

### Idrees's Solution
"when we scroll up or down everytime without reloading cards all all other stuff comes like spaws from up or down... I want this everytime when we scroll down or up in a more intense way"

### Enki's Proposed Solution
Implement a bidirectional continuous scroll engine that monitors scroll velocity, direction, and scroll offsets, applying smooth enter and exit transitions dynamically in both directions.

***

## 8. WebGL Render Loop GPU Throttling

### Problem
The 3D engine rendered animation frames continuously at 60 FPS even when the browser tab was backgrounded or the canvas was scrolled out of view, draining GPU resources.

### Idrees's Solution
None provided by Idrees (Discovered during performance refactoring in commit `6fa37ec`).

### Enki's Proposed Solution
Add document visibility state listeners and canvas viewport observation. When the canvas is out of the active viewport or the tab is hidden, halt the Three.js render loop immediately.
