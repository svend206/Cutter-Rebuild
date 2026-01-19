/**
 * viewer.js - Three.js 3D Viewer Module
 * 
 * Handles all Three.js scene initialization and model loading.
 * THREE is loaded globally via <script> tag in index.html.
 */

let scene, camera, renderer, controls;
let currentModel = null;

// Normalize all models to this size for consistent camera framing
const TARGET_VIEW_SIZE = 10.0;

/**
 * Initialize Three.js viewer
 */
export function initViewer() {
    const container = document.getElementById('stl-viewer');
    if (!container) {
        console.warn('STL viewer container not found');
        return;
    }
    
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    // Create camera (Standard values - models will be normalized to fit)
    camera = new THREE.PerspectiveCamera(
        45, // FOV
        container.clientWidth / container.clientHeight, // Aspect ratio
        0.1, // Near plane (standard)
        1000 // Far plane (standard)
    );
    camera.position.set(15, 15, 15); // Position for normalized 10-unit models
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight1.position.set(1, 1, 1);
    scene.add(directionalLight1);
    
    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight2.position.set(-1, -1, -1);
    scene.add(directionalLight2);
    
    // Add orbit controls (attached to renderer's canvas element)
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.screenSpacePanning = false;
    controls.minDistance = 1;
    controls.maxDistance = 100;
    
    // DEBUG: Event listener to prove canvas receives interactions
    renderer.domElement.addEventListener('click', () => {
        console.log('🖱️ Canvas Clicked! Interaction is working.');
    });
    
    renderer.domElement.addEventListener('mousedown', () => {
        console.log('🖱️ Mouse Down on canvas');
    });
    
    console.log('✅ OrbitControls attached to canvas');
    console.log('✅ Canvas size:', renderer.domElement.width, 'x', renderer.domElement.height);
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    function onWindowResize() {
        if (!container || !camera || !renderer) return;
        
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        // Don't resize if container has no dimensions yet
        if (width === 0 || height === 0) {
            console.log('⚠️ Skipping resize (container not visible yet)');
            return;
        }
        
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
        
        console.log('📐 Viewer resized:', width, 'x', height);
    }
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
    
    // DEBUG: Check if container has actual size
    console.log('Three.js viewer initialized');
    console.log('📐 Container dimensions:', container.clientWidth, 'x', container.clientHeight);
    console.log('📐 Container computed style:', window.getComputedStyle(container).width, 'x', window.getComputedStyle(container).height);
    console.log('📐 Container visibility:', window.getComputedStyle(container).display, window.getComputedStyle(container).visibility);
}

/**
 * Load 3D model from Base64 data (DEPRECATED - OPTIMIZATION PASS 1)
 * Use loadModelFromUrl instead for better performance
 */
export function loadModelFromBase64(base64Data) {
    console.warn('loadModelFromBase64 is deprecated. Use loadModelFromUrl for streaming.');
    if (!base64Data) return;
    
    // Legacy support - decode and load (not recommended)
    console.log('Loading model from Base64 data...');
}

/**
 * Load 3D model from URL (OPTIMIZATION PASS 1)
 * Uses browser's native async threaded downloading for better performance.
 * No memory bloat from Base64 encoding.
 */
export function loadModelFromUrl(url) {
    if (!url) {
        console.error('No model URL provided');
        return;
    }
    
    if (!scene || !camera || !renderer) {
        console.error('Viewer not initialized. Call initViewer() first.');
        return;
    }
    
    console.log(`Loading model from URL: ${url}`);
    
    // Clear previous model
    clearModel();
    
    const loader = new THREE.STLLoader();
    
    loader.load(
        url,
        // Success callback
        (geometry) => {
            console.log('✅ Model loaded successfully');
            console.log('📦 Geometry type:', geometry.type);
            console.log('📦 Vertices:', geometry.attributes?.position?.count || 'unknown');
            
            try {
                // Compute normals for proper lighting
                geometry.computeVertexNormals();
                console.log('✅ Normals computed');
                
                // Create material (orange metallic - matches brand color)
                const material = new THREE.MeshPhongMaterial({
                    color: 0xff6600,
                    specular: 0x111111,
                    shininess: 200,
                    flatShading: false
                });
                console.log('✅ Material created');
                
                // Create mesh
                currentModel = new THREE.Mesh(geometry, material);
                console.log('✅ Mesh created');
                
                // Center the geometry at origin
                geometry.center();
                console.log('✅ Geometry centered');
                
                // VISUAL NORMALIZATION: Scale model to standard size
                // This handles models in any units (mm, cm, m, inches)
                const box = new THREE.Box3().setFromObject(currentModel);
                const size = new THREE.Vector3();
                box.getSize(size);
                const originalMaxDim = Math.max(size.x, size.y, size.z);
                
                // Use global TARGET_VIEW_SIZE constant (10.0)
                let scaleFactor = 1.0;
                
                if (originalMaxDim > 0) {
                    scaleFactor = TARGET_VIEW_SIZE / originalMaxDim;
                    currentModel.scale.set(scaleFactor, scaleFactor, scaleFactor);
                    console.log(`🔍 Visual Normalization: Original size=${originalMaxDim.toFixed(4)}, Scale=${scaleFactor.toFixed(2)}x, Final size=${TARGET_VIEW_SIZE}`);
                }
                
                // Add to scene
                scene.add(currentModel);
                console.log('✅ Added to scene');
                
                // DEBUG HELPER: Yellow box around model
                const boxHelper = new THREE.BoxHelper(currentModel, 0xffff00);
                scene.add(boxHelper);
                console.log('📦 Debug box helper added (yellow wireframe)');
                
                // Fit camera to normalized size
                fitCameraToNormalizedModel(TARGET_VIEW_SIZE);
                
                console.log('✅ Model rendered in viewer');
            } catch (renderError) {
                console.error('❌ Error rendering model:', renderError);
                console.error('Stack:', renderError.stack);
            }
        },
        // Progress callback
        (xhr) => {
            if (xhr.lengthComputable) {
                const percentComplete = (xhr.loaded / xhr.total) * 100;
                console.log(`Loading: ${Math.round(percentComplete)}%`);
            }
        },
        // Error callback
        (error) => {
            console.error('❌ Model loading failed:', error);
            console.error('Error type:', error?.constructor?.name);
            console.error('Error message:', error?.message);
            console.error('URL attempted:', url);
        }
    );
    
    console.log('Model URL loading initiated (streaming mode)');
    
    // Add timeout to detect stuck loads
    setTimeout(() => {
        if (!currentModel) {
            console.warn('⚠️ Model load timeout: Success callback did not fire within 10 seconds');
            console.warn('This could mean the geometry parsed but rendering failed silently');
        }
    }, 10000);
}

/**
 * Fit camera to normalized model (always 10 units after scaling)
 */
function fitCameraToNormalizedModel(targetSize) {
    if (!camera || !controls) return;
    
    // Calculate optimal camera distance for normalized size
    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(targetSize / 2 / Math.tan(fov / 2));
    cameraZ *= 2.0; // 2x padding for comfortable view
    
    // Position camera at diagonal for good view of all faces
    camera.position.set(cameraZ, cameraZ, cameraZ);
    camera.lookAt(0, 0, 0); // Model is centered at origin
    
    // Update controls target to origin
    controls.target.set(0, 0, 0);
    controls.update();
    
    console.log(`📐 Camera fitted: distance=${cameraZ.toFixed(2)}, target size=${targetSize}, FOV=${camera.fov}°`);
}

/**
 * Fit camera to current model selection
 */
export function fitCameraToSelection() {
    if (!controls || !currentModel) return;
    
    // Model is always normalized to 10 units
    fitCameraToNormalizedModel(10.0);
}

/**
 * Force viewer to resize (call this when viewer becomes visible)
 */
export function forceResize() {
    const container = document.getElementById('stl-viewer');
    if (!container || !camera || !renderer) return;
    
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    if (width === 0 || height === 0) {
        console.log('⚠️ Cannot resize: container still has 0 dimensions');
        return;
    }
    
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
    
    console.log('🔧 Viewer FORCE RESIZED:', width, 'x', height);
}

/**
 * Clear current model from scene
 */
export function clearModel() {
    if (currentModel && scene) {
        // Remove model
        scene.remove(currentModel);
        currentModel.geometry.dispose();
        currentModel.material.dispose();
        currentModel = null;
        
        // Remove any BoxHelpers (debug wireframes)
        const helpersToRemove = [];
        scene.traverse((object) => {
            if (object instanceof THREE.BoxHelper || object instanceof THREE.LineSegments) {
                helpersToRemove.push(object);
            }
        });
        helpersToRemove.forEach(helper => {
            if (helper.geometry) helper.geometry.dispose();
            if (helper.material) helper.material.dispose();
            scene.remove(helper);
        });
        
        console.log('🗑️ Previous model cleared (including helpers)');
    }
}

/**
 * Render Parametric Shape (Napkin Mode Configurator)
 * @param {string} type - Shape type: 'block', 'cylinder', 'tube', 'l-bracket', 'plate'
 * @param {object} dimensions - Shape-specific dimensions object
 */
export function renderParametricShape(type, dimensions) {
    if (!scene || !camera) {
        console.error('❌ Viewer not initialized');
        return null;
    }
    
    // Clear existing model
    clearModel();
    
    let geometry = null;
    let partVolume = 0;
    
    try {
        switch (type) {
            case 'block':
            case 'plate':
                // Block/Plate: BoxGeometry
                const { x, y, z } = dimensions;
                if (!x || !y || !z || x <= 0 || y <= 0 || z <= 0) {
                    console.warn('⚠️ Invalid block dimensions');
                    return null;
                }
                geometry = new THREE.BoxGeometry(x, y, z);
                partVolume = x * y * z;
                console.log(`📦 Block: ${x} × ${y} × ${z} = ${partVolume.toFixed(3)} in³`);
                break;
                
            case 'cylinder':
                // Cylinder: CylinderGeometry
                const { diameter, length } = dimensions;
                if (!diameter || !length || diameter <= 0 || length <= 0) {
                    console.warn('⚠️ Invalid cylinder dimensions');
                    return null;
                }
                const radius = diameter / 2;
                geometry = new THREE.CylinderGeometry(radius, radius, length, 32);
                partVolume = Math.PI * radius * radius * length;
                console.log(`🛢️ Cylinder: Ø${diameter} × ${length} = ${partVolume.toFixed(3)} in³`);
                break;
                
            case 'tube':
                // Tube: Hollow cylinder (outer - inner)
                const { od, id, length: tubeLength } = dimensions;
                if (!od || !id || !tubeLength || od <= 0 || id <= 0 || tubeLength <= 0 || id >= od) {
                    console.warn('⚠️ Invalid tube dimensions');
                    return null;
                }
                const outerRadius = od / 2;
                const innerRadius = id / 2;
                
                // Create a ring-shaped cross-section (circle with hole)
                const tubeShape = new THREE.Shape();
                // Outer circle
                tubeShape.absarc(0, 0, outerRadius, 0, Math.PI * 2, false);
                // Inner circle (hole) - must be in opposite direction
                const holePath = new THREE.Path();
                holePath.absarc(0, 0, innerRadius, 0, Math.PI * 2, true);
                tubeShape.holes.push(holePath);
                
                // Extrude settings for the tube length
                const tubeExtrudeSettings = {
                    depth: tubeLength,
                    bevelEnabled: false,
                    steps: 1
                };
                
                // Create extruded geometry
                geometry = new THREE.ExtrudeGeometry(tubeShape, tubeExtrudeSettings);
                
                // Rotate to align with cylinder orientation (standing up)
                geometry.rotateX(Math.PI / 2);
                
                partVolume = Math.PI * (outerRadius * outerRadius - innerRadius * innerRadius) * tubeLength;
                console.log(`⭕ Tube: OD ${od} × ID ${id} × ${tubeLength} = ${partVolume.toFixed(3)} in³`);
                break;
                
            case 'l-bracket':
                // L-Bracket: ExtrudeGeometry from L-shaped path
                const { leg1, leg2, width, thickness } = dimensions;
                if (!leg1 || !leg2 || !width || !thickness || leg1 <= 0 || leg2 <= 0 || width <= 0 || thickness <= 0) {
                    console.warn('⚠️ Invalid L-bracket dimensions');
                    return null;
                }
                
                // Create L-shape path
                const shape = new THREE.Shape();
                shape.moveTo(0, 0);
                shape.lineTo(leg1, 0);
                shape.lineTo(leg1, thickness);
                shape.lineTo(thickness, thickness);
                shape.lineTo(thickness, leg2);
                shape.lineTo(0, leg2);
                shape.lineTo(0, 0);
                
                // Extrude settings
                const extrudeSettings = {
                    depth: width,
                    bevelEnabled: false
                };
                
                geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
                
                // Calculate volume: (leg1 * thickness * width) + ((leg2 - thickness) * thickness * width)
                partVolume = (leg1 * thickness * width) + ((leg2 - thickness) * thickness * width);
                console.log(`🔧 L-Bracket: ${leg1} × ${leg2} × ${width} (t=${thickness}) = ${partVolume.toFixed(3)} in³`);
                break;
                
            case 'cone':
                // Cone: ConeGeometry
                const { diameter: coneDiameter, height: coneHeight } = dimensions;
                if (!coneDiameter || !coneHeight || coneDiameter <= 0 || coneHeight <= 0) {
                    console.warn('⚠️ Invalid cone dimensions');
                    return null;
                }
                const coneRadius = coneDiameter / 2;
                geometry = new THREE.ConeGeometry(coneRadius, coneHeight, 32);
                partVolume = (1/3) * Math.PI * coneRadius * coneRadius * coneHeight;
                console.log(`🔺 Cone: Ø${coneDiameter} × H${coneHeight} = ${partVolume.toFixed(3)} in³`);
                break;
                
            default:
                console.error('❌ Unknown shape type:', type);
                return null;
        }
        
        if (!geometry) {
            console.error('❌ Failed to create geometry');
            return null;
        }
        
        // Create material (metallic gray, like raw stock)
        const material = new THREE.MeshStandardMaterial({
            color: 0xcccccc,
            metalness: 0.5,
            roughness: 0.5,
            emissive: 0x222222, // Slight self-illumination so it's always visible
            emissiveIntensity: 0.3
        });
        
        // Create mesh
        currentModel = new THREE.Mesh(geometry, material);
        scene.add(currentModel);
        
        // Add wireframe overlay for clarity (blue edges)
        const wireframeGeometry = new THREE.EdgesGeometry(geometry);
        const wireframeMaterial = new THREE.LineBasicMaterial({ color: 0x00aaff, linewidth: 2 });
        const wireframe = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);
        currentModel.add(wireframe);
        
        // Center and normalize model
        const box = new THREE.Box3().setFromObject(currentModel);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        
        console.log(`📐 Parametric Shape BEFORE scaling:`);
        console.log(`   Size: ${size.x.toFixed(3)} × ${size.y.toFixed(3)} × ${size.z.toFixed(3)}`);
        console.log(`   MaxDim: ${maxDim.toFixed(3)}`);
        console.log(`   Center: ${center.x.toFixed(3)}, ${center.y.toFixed(3)}, ${center.z.toFixed(3)}`);
        
        // Center at origin
        currentModel.position.sub(center);
        console.log(`   Centered at origin`);
        
        // Scale to target size (10 units) - CRITICAL for visibility
        if (maxDim > 0) {
            const scale = TARGET_VIEW_SIZE / maxDim;
            currentModel.scale.set(scale, scale, scale);
            console.log(`🔍 Scaling parametric shape:`);
            console.log(`   ${maxDim.toFixed(3)} → ${TARGET_VIEW_SIZE} (scale factor: ${scale.toFixed(3)}x)`);
            console.log(`   Final visual size: ${TARGET_VIEW_SIZE}`);
            
            // Verify final size after scaling
            const finalBox = new THREE.Box3().setFromObject(currentModel);
            const finalSize = finalBox.getSize(new THREE.Vector3());
            const finalMaxDim = Math.max(finalSize.x, finalSize.y, finalSize.z);
            console.log(`📐 AFTER scaling: ${finalSize.x.toFixed(3)} × ${finalSize.y.toFixed(3)} × ${finalSize.z.toFixed(3)} (maxDim: ${finalMaxDim.toFixed(3)})`);
        } else {
            console.error('❌ MaxDim is 0! Shape will be invisible.');
            return null;
        }
        
        // Fit camera
        fitCameraToNormalizedModel(TARGET_VIEW_SIZE);
        
        console.log('✅ Parametric shape rendered:', type);
        
        return {
            volume: partVolume,
            dimensions: dimensions
        };
        
    } catch (error) {
        console.error('❌ Error rendering parametric shape:', error);
        return null;
    }
}

