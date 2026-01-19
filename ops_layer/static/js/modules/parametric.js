/**
 * parametric.js - Parametric Shape Configurator (Napkin Mode Phase 5.5)
 * 
 * Replaces simple Part Volume input with intelligent shape builder.
 * Calculates volumes physically, renders 3D shapes, and suggests similar parts.
 */

import * as viewer from './viewer.js';
import * as manual from './manual.js';
import * as ui from './ui.js';

// Debounce timer for dimension changes
let dimensionDebounceTimer = null;

// Current shape configuration
let currentShapeConfig = {
    type: null,
    dimensions: {},
    volume: 0
};

/**
 * Initialize parametric configurator
 */
export function initParametricConfigurator() {
    console.log('🎨 Initializing Parametric Configurator...');
    
    // Visual shape cards (Phase 5.5 - Visual Selection)
    const shapeCards = document.querySelectorAll('.shape-card');
    shapeCards.forEach(card => {
        card.addEventListener('click', () => {
            const shapeType = card.getAttribute('data-shape');
            selectShapeCard(shapeType);
        });
    });
    
    // Shape selector (hidden, for backward compatibility)
    const shapeSelector = document.getElementById('shape-selector');
    if (shapeSelector) {
        shapeSelector.addEventListener('change', handleShapeChange);
    }
    
    // Auto-calculate stock button
    const autoCalcBtn = document.getElementById('stock-auto-calc-btn');
    if (autoCalcBtn) {
        autoCalcBtn.addEventListener('click', autoCalculateStock);
    }
    
    // Dimension inputs (all shapes)
    const dimensionInputs = document.querySelectorAll('.dimension-input');
    dimensionInputs.forEach(input => {
        // Auto-select content on focus (so typing replaces "0")
        input.addEventListener('focus', (e) => {
            e.target.select();
        });
        
        input.addEventListener('input', () => {
            // Debounce for smooth UX
            if (dimensionDebounceTimer) {
                clearTimeout(dimensionDebounceTimer);
            }
            dimensionDebounceTimer = setTimeout(() => {
                handleDimensionChange();
            }, 300); // Wait 300ms after user stops typing
        });
    });
    
    console.log('✅ Parametric Configurator initialized');
}

/**
 * Select shape card (visual selection)
 */
function selectShapeCard(shapeType) {
    console.log('🔷 Shape card selected:', shapeType);
    
    // Remove 'selected' class from all cards
    const allCards = document.querySelectorAll('.shape-card');
    allCards.forEach(card => card.classList.remove('selected'));
    
    // Add 'selected' class to clicked card
    const selectedCard = document.querySelector(`.shape-card[data-shape="${shapeType}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    // Update hidden dropdown (for backward compatibility)
    const shapeSelector = document.getElementById('shape-selector');
    if (shapeSelector) {
        shapeSelector.value = shapeType;
    }
    
    // Trigger shape change handler
    handleShapeChange();
}

/**
 * Handle shape selector change
 */
function handleShapeChange() {
    const shapeSelector = document.getElementById('shape-selector');
    const selectedShape = shapeSelector?.value;
    
    console.log('🔷 Shape selected:', selectedShape);
    
    // Hide all dimension sets
    const dimensionSets = document.querySelectorAll('.dimension-set');
    dimensionSets.forEach(set => {
        set.style.display = 'none';
    });
    
    // Show dimension inputs container
    const dimensionInputsContainer = document.getElementById('dimension-inputs');
    if (dimensionInputsContainer && selectedShape) {
        dimensionInputsContainer.style.display = 'block';
    } else if (dimensionInputsContainer) {
        dimensionInputsContainer.style.display = 'none';
    }
    
    // Show relevant dimension set
    if (selectedShape) {
        // Map shape types to their dimension input sets
        // Note: "plate" shares dimensions with "block" (both use X/Y/Z)
        let dimSetId = `dims-${selectedShape}`;
        
        // Special case: plate uses block dimensions
        if (selectedShape === 'plate') {
            dimSetId = 'dims-block';
        }
        
        const dimSet = document.getElementById(dimSetId);
        if (dimSet) {
            dimSet.style.display = 'block';
        } else {
            console.warn(`⚠️ Dimension set not found: ${dimSetId} (shape: ${selectedShape})`);
        }
        
        // Store shape type
        currentShapeConfig.type = selectedShape;
        currentShapeConfig.dimensions = {};
        currentShapeConfig.volume = 0;
        
        // Clear calculated volume
        updateVolumeDisplay(0);
    }
}

/**
 * Handle dimension input change
 */
function handleDimensionChange() {
    const shapeType = currentShapeConfig.type;
    if (!shapeType) {
        console.warn('⚠️ No shape type selected');
        return;
    }
    
    // Get dimensions based on shape type
    const dimensions = getDimensions(shapeType);
    if (!dimensions) {
        console.warn('⚠️ Invalid dimensions');
        return;
    }
    
    // Validate dimensions (all must be positive)
    const dimensionValues = Object.values(dimensions);
    if (dimensionValues.some(v => v <= 0)) {
        console.log('⏳ Waiting for all dimensions to be positive...');
        updateVolumeDisplay(0);
        return;
    }
    
    // Calculate volume
    const volume = calculateVolume(shapeType, dimensions);
    if (volume === null) {
        console.error('❌ Volume calculation failed');
        return;
    }
    
    // Update state
    currentShapeConfig.dimensions = dimensions;
    currentShapeConfig.volume = volume;
    
    // Update UI
    updateVolumeDisplay(volume);
    
    // Ensure viewer is visible and resized
    viewer.forceResize();
    
    // Render 3D shape
    const result = viewer.renderParametricShape(shapeType, dimensions);
    if (result) {
        console.log(`✅ Shape rendered: ${shapeType}, Volume: ${volume.toFixed(3)} in³`);
    } else {
        console.error('❌ Shape rendering failed');
    }
    
    // Auto-calculate stock (with padding)
    autoCalculateStock();
    
    // Trigger recalculation of quote
    manual.calculateManualQuote();
    
    // Check for "Close Cousin" matches (debounced)
    checkForSimilarParts(volume, dimensions);
}

/**
 * Get dimensions object based on shape type
 */
function getDimensions(shapeType) {
    switch (shapeType) {
        case 'block':
        case 'plate':
            return {
                x: parseFloat(document.getElementById('dim-block-x')?.value) || 0,
                y: parseFloat(document.getElementById('dim-block-y')?.value) || 0,
                z: parseFloat(document.getElementById('dim-block-z')?.value) || 0
            };
            
        case 'cylinder':
            return {
                diameter: parseFloat(document.getElementById('dim-cyl-diameter')?.value) || 0,
                length: parseFloat(document.getElementById('dim-cyl-length')?.value) || 0
            };
            
        case 'tube':
            return {
                od: parseFloat(document.getElementById('dim-tube-od')?.value) || 0,
                id: parseFloat(document.getElementById('dim-tube-id')?.value) || 0,
                length: parseFloat(document.getElementById('dim-tube-length')?.value) || 0
            };
            
        case 'l-bracket':
            return {
                leg1: parseFloat(document.getElementById('dim-bracket-leg1')?.value) || 0,
                leg2: parseFloat(document.getElementById('dim-bracket-leg2')?.value) || 0,
                width: parseFloat(document.getElementById('dim-bracket-width')?.value) || 0,
                thickness: parseFloat(document.getElementById('dim-bracket-thickness')?.value) || 0
            };
            
        case 'cone':
            return {
                diameter: parseFloat(document.getElementById('dim-cone-diameter')?.value) || 0,
                height: parseFloat(document.getElementById('dim-cone-height')?.value) || 0
            };
            
        default:
            console.error('❌ Unknown shape type:', shapeType);
            return null;
    }
}

/**
 * Calculate volume for given shape type and dimensions
 */
function calculateVolume(shapeType, dimensions) {
    let volume = 0;
    
    try {
        switch (shapeType) {
            case 'block':
            case 'plate':
                // Volume = X × Y × Z
                volume = dimensions.x * dimensions.y * dimensions.z;
                break;
                
            case 'cylinder':
                // Volume = π × r² × h
                const radius = dimensions.diameter / 2;
                volume = Math.PI * radius * radius * dimensions.length;
                break;
                
            case 'tube':
                // Volume = π × (r_outer² - r_inner²) × h
                const outerRadius = dimensions.od / 2;
                const innerRadius = dimensions.id / 2;
                
                // Validation: inner diameter must be less than outer
                if (dimensions.id >= dimensions.od) {
                    ui.showError('⚠️ Inner diameter must be less than outer diameter');
                    return null;
                }
                
                volume = Math.PI * (outerRadius * outerRadius - innerRadius * innerRadius) * dimensions.length;
                break;
                
            case 'l-bracket':
                // Volume = (leg1 × thickness × width) + ((leg2 - thickness) × thickness × width)
                volume = (dimensions.leg1 * dimensions.thickness * dimensions.width) + 
                         ((dimensions.leg2 - dimensions.thickness) * dimensions.thickness * dimensions.width);
                break;
                
            case 'cone':
                // Volume = (1/3) × π × r² × h
                const coneRadius = dimensions.diameter / 2;
                volume = (1/3) * Math.PI * coneRadius * coneRadius * dimensions.height;
                break;
                
            default:
                console.error('❌ Unknown shape type for volume calculation:', shapeType);
                return null;
        }
        
        return volume;
        
    } catch (error) {
        console.error('❌ Volume calculation error:', error);
        return null;
    }
}

/**
 * Update volume display
 */
function updateVolumeDisplay(volume) {
    const volumeDisplay = document.getElementById('calculated-part-volume');
    if (volumeDisplay) {
        volumeDisplay.textContent = `${volume.toFixed(3)} in³`;
    }
}

/**
 * Auto-calculate stock dimensions (Part + 0.125" padding)
 */
function autoCalculateStock() {
    const shapeType = currentShapeConfig.type;
    const dimensions = currentShapeConfig.dimensions;
    
    if (!shapeType || !dimensions || Object.keys(dimensions).length === 0) {
        console.log('⏳ Waiting for shape dimensions...');
        return;
    }
    
    const PADDING = 0.125; // 1/8" padding for machining
    
    let stockX = 0, stockY = 0, stockZ = 0;
    
    switch (shapeType) {
        case 'block':
        case 'plate':
            stockX = dimensions.x + (2 * PADDING);
            stockY = dimensions.y + (2 * PADDING);
            stockZ = dimensions.z + (2 * PADDING);
            break;
            
        case 'cylinder':
            // Stock for cylinder: diameter + padding for X and Y, length + padding for Z
            stockX = dimensions.diameter + (2 * PADDING);
            stockY = dimensions.diameter + (2 * PADDING);
            stockZ = dimensions.length + (2 * PADDING);
            break;
            
        case 'tube':
            // Stock for tube: OD + padding for X and Y, length + padding for Z
            stockX = dimensions.od + (2 * PADDING);
            stockY = dimensions.od + (2 * PADDING);
            stockZ = dimensions.length + (2 * PADDING);
            break;
            
        case 'l-bracket':
            // Stock for L-bracket: bounding box + padding
            stockX = dimensions.leg1 + (2 * PADDING);
            stockY = dimensions.leg2 + (2 * PADDING);
            stockZ = dimensions.width + (2 * PADDING);
            break;
            
        case 'cone':
            // Stock for cone: diameter + padding for X and Y, height + padding for Z
            stockX = dimensions.diameter + (2 * PADDING);
            stockY = dimensions.diameter + (2 * PADDING);
            stockZ = dimensions.height + (2 * PADDING);
            break;
            
        default:
            console.warn('⚠️ Cannot auto-calculate stock for unknown shape:', shapeType);
            return;
    }
    
    // Update stock input fields
    const stockXInput = document.getElementById('stock-x');
    const stockYInput = document.getElementById('stock-y');
    const stockZInput = document.getElementById('stock-z');
    
    if (stockXInput) stockXInput.value = stockX.toFixed(3);
    if (stockYInput) stockYInput.value = stockY.toFixed(3);
    if (stockZInput) stockZInput.value = stockZ.toFixed(3);
    
    // Update stock volume display
    manual.updateStockVolumeDisplay();
    
    // Update removal volume display
    updateRemovalVolumeDisplay();
    
    console.log(`📦 Stock auto-calculated: ${stockX.toFixed(3)} × ${stockY.toFixed(3)} × ${stockZ.toFixed(3)}`);
}

/**
 * Update removal volume display
 */
function updateRemovalVolumeDisplay() {
    const stockX = parseFloat(document.getElementById('stock-x')?.value) || 0;
    const stockY = parseFloat(document.getElementById('stock-y')?.value) || 0;
    const stockZ = parseFloat(document.getElementById('stock-z')?.value) || 0;
    const stockVolume = stockX * stockY * stockZ;
    
    const partVolume = currentShapeConfig.volume || 0;
    const removalVolume = stockVolume - partVolume;
    
    const removalDisplay = document.getElementById('removal-volume');
    if (removalDisplay) {
        if (removalVolume < 0) {
            removalDisplay.textContent = '⚠️ Negative!';
            removalDisplay.style.color = '#ff3333';
            
            // Show error
            const errorDiv = document.getElementById('part-volume-error');
            if (errorDiv) {
                errorDiv.style.display = 'block';
            }
        } else {
            removalDisplay.textContent = `${removalVolume.toFixed(3)} in³`;
            removalDisplay.style.color = '#ff6600';
            
            // Hide error
            const errorDiv = document.getElementById('part-volume-error');
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
        }
    }
}

/**
 * Check for similar parts ("Close Cousin" intelligence)
 * @param {number} volume - Part volume
 * @param {object} dimensions - Part dimensions
 */
function checkForSimilarParts(volume, dimensions) {
    console.log('🧠 Checking for similar parts...');
    
    // Calculate aspect ratio (for similarity matching)
    let aspectRatio = 1.0;
    const shapeType = currentShapeConfig.type;
    
    switch (shapeType) {
        case 'block':
        case 'plate':
            // Aspect ratio = longest / shortest dimension
            const dims = [dimensions.x, dimensions.y, dimensions.z];
            aspectRatio = Math.max(...dims) / Math.min(...dims);
            break;
            
        case 'cylinder':
        case 'tube':
            // Aspect ratio = length / diameter
            const diameter = shapeType === 'cylinder' ? dimensions.diameter : dimensions.od;
            aspectRatio = dimensions.length / diameter;
            break;
            
        case 'l-bracket':
            // Aspect ratio = max leg / thickness
            aspectRatio = Math.max(dimensions.leg1, dimensions.leg2) / dimensions.thickness;
            break;
    }
    
    console.log(`📐 Shape fingerprint: Volume=${volume.toFixed(3)} in³, Aspect Ratio=${aspectRatio.toFixed(2)}`);
    
    // TODO: Query backend for similar parts (mock for now)
    // For Phase 5.5, this will query /api/similar_parts with volume and aspect ratio
    // and display "Smart Toast" if matches found
    
    // Mock: Show toast if volume is between 5-10 in³ (demo)
    if (volume >= 5 && volume <= 10) {
        setTimeout(() => {
            showSimilarPartsToast('SpaceX_Bracket_RevA', 0.92);
        }, 500);
    }
}

/**
 * Show "Smart Toast" for similar parts detection
 * @param {string} partName - Name of similar part
 * @param {number} confidence - Confidence score (0-1)
 */
function showSimilarPartsToast(partName, confidence) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    const confidencePercent = (confidence * 100).toFixed(0);
    toast.textContent = `🧠 Similarity Detected: Close match to '${partName}' (${confidencePercent}% confidence). Click to apply historical tags.`;
    toast.classList.add('show');
    toast.style.cursor = 'pointer';
    
    // Click to apply tags
    toast.onclick = () => {
        console.log('🔖 Applying historical tags from:', partName);
        // TODO: Load tags from similar part
        ui.showToast('Historical tags applied!');
    };
    
    // Auto-hide after 8 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        toast.onclick = null;
    }, 8000);
}

/**
 * Get current part volume (for manual quote calculation)
 */
export function getCurrentPartVolume() {
    return currentShapeConfig.volume || 0;
}

/**
 * Get current shape configuration (for Genesis Hash generation)
 * @returns {object} Shape config {type, dimensions, volume}
 */
export function getCurrentShapeConfig() {
    return {
        type: currentShapeConfig.type,
        dimensions: {...currentShapeConfig.dimensions},  // Clone to prevent mutation
        volume: currentShapeConfig.volume
    };
}

