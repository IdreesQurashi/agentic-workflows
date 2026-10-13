# Frontend, UI Design and Personal Brand Operational Instructions

These standard operating procedures define the step by step workflow for designing, building, and maintaining high luxury web interfaces, Three.js 3D engines, and portfolio assets at `idreesqurashi.github.io`. Every procedure addresses design violations and bugs identified across previous website builds.

***

## 1. TRIONN Luxury 3D Card Architecture

### Problem
Cards rendered as flat, unstyled boxes with thin grey outlines, lacking depth, interaction physics, and visual prestige.

### Idrees's Solution
"the cards are still very ugly, i want them very high quality, your task was to use provided website trioon as a template... copy exact cards of something high quality 3d website"

### Enki's Proposed Solution
Every interactive showcase card must implement the full multi layer specification:
1. Surfaces: Deep dark graphite background (`#0E0F12`) on a dark canvas (`#0A0B0E`).
2. Borders: Fine hairline border (`rgba(255, 255, 255, 0.08)`) with subtle inner top highlight.
3. Specular Glare: Inject `<div class="card-glare"></div>` inside every card container.
4. Interaction: Bind 3D perspective tilt tracking in JavaScript that calculates mouse coordinates and dynamically updates specular glare opacity and translation transforms.
5. Pill Badges: Floating pill tags with backdrop blur and monospace typography.

***

## 2. Monumental Editorial Typography Hierarchy

### Problem
Headlines used plain sans serif fonts, awkward line breaks, and microscopic uppercase tags that looked like generic AI web templates.

### Idrees's Solution
"headline is fucked up, havent you check the implementation plan that claude planned and didnt you worked according to it?"
"Banned: Clunky text heavy heroes without polish. Replicate TRIONN's exact typographic scale with monumental grotesque display fonts contrasted against luxury italic serif accents."

### Enki's Proposed Solution
Apply the dual font typographic pairing system:
* Display Font: Monumental grotesque headings (Familjen Grotesk or Plus Jakarta Sans) set at clamp scales (2.5rem to 5.5rem).
* Accent Font: Luxury editorial italic serif accents (Playfair Display) reserved exclusively for 1 or 2 focal words per headline.
* Body Text: Clean neutral sans serif (Inter) with generous line heights (1.6 to 1.8) and restrained opacity (0.7 to 0.85).
* Eliminate meaningless eyebrow badges above titles.

***

## 3. 85 Percent Screen Modal Pop Out Engine

### Problem
Project details were either crammed into tiny cards or navigated to external pages, disrupting the immersive portfolio browsing experience.

### Idrees's Solution
"then the person clicks that card and view it's full screen pop out not full screen but a normal pop out which covers alomost 85% area of screen leaving the 15% in side or maybe 80 20 or 70 30 as you think is a good ratio... and I also want pop out for the main page agentic workflows"

### Enki's Proposed Solution
Engineer an in page modal overlay engine:
1. Container Bounds: Modal container occupies exactly 85% of viewport width and 85% of viewport height on desktop.
2. Backdrop: Blurred dark backdrop overlay (`rgba(0, 0, 0, 0.75)` with `backdrop-filter: blur(12px)`).
3. Transitions: Smooth scale up (0.95 to 1.0) and opacity transitions with cubic bezier easing.
4. Controls: Floating close button at the top right, background click dismiss, and Escape key listeners.

***

## 4. WebGL Three.js Monolith Shader Configuration

### Problem
Background 3D elements either used fast spinning wireframe cubes or caused severe browser frame rate drops due to unthrottled render loops.

### Idrees's Solution
"there is no 3d floating, I want high quality 3d floating... find a structures that moves with a normal speed in background throught out the whole website"

### Enki's Proposed Solution
Configure the canonical Three.js scene in `engine3d.js`:
* Geometry: Multi block chamfered architectural prism monolith with titanium metallic finish.
* Lighting: Warm amber top rim light contrasted with cool cyan side fill and subtle ambient occlusion.
* Movement: Damped mouse parallax with slow continuous orbital rotation.
* Performance: Halt the render loop immediately whenever document visibility is hidden or when the canvas is outside the viewport.

***

## 5. Asset Decoupling and Performance Optimization

### Problem
Embedding dozens of Base64 encoded images directly inside HTML files caused page weights to swell to 4MB, crippling mobile loading speeds.

### Idrees's Solution
None provided by Idrees (Discovered during performance review of Project A2).

### Enki's Proposed Solution
All media assets must be stored as separate files in a dedicated `assets/` directory. Configure HTML image tags with native `loading="lazy"` and `decoding="async"`, keeping raw HTML page weight strictly under 100KB.
