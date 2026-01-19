/**
 * manual.js - Napkin Mode Engine
 * Bi-directional "Linked Levers" logic.
 */

import * as state from './state.js';
import * as api from './api.js';
import * as ui from './ui.js';
import * as stock from './stock.js';
import * as variance from './variance.js';
import * as parametric from './parametric.js'; // Phase 5.5: Parametric shapes
import * as viewer from './viewer.js'; // Phase 5.5: Clear viewer on init

// ==== HELPER FUNCTIONS ====

/**
 * Generate a default Quote ID in format: Q-YYYYMMDD-###
 * where ### is a random 3-digit number (100-999)
 */
export function generateDefaultQuoteId() {
    const today = new Date();
    const dateStr = today.toISOString().slice(0, 10).replace(/-/g, ''); // YYYYMMDD
    const randomNum = Math.floor(Math.random() * 900) + 100; // 100-999
    return `Q-${dateStr}-${randomNum}`;
}

// ==== NEW LANDING SCREEN FLOW ====
// --- INITIALIZATION ---
export function initManualMode() {
    state.setIsManualMode(true);
    
    // CRITICAL: Unlock price (user is starting a new quote)
    variance.unlockPrice();
    
    // FIX: Clear traveler tags for new quote
    state.clearAllTravelers();
    state.clearAllTags();
    ui.renderTravelerBadges(); // Re-render with cleared state
    
    // CRITICAL: Clear 3D viewer (remove any previous models from File Mode)
    viewer.clearModel();
    console.log('🗑️ Viewer cleared for Napkin Mode');
    
    // Toggle UI Visibility (New Flow: Hide landing screen, show home button)
    // PHASE 5.5: Show viewer in Napkin Mode, hide removal rate slider (replaced by parametric configurator)
    const hide = ['upload-zone', 'file-input', 'calculate-btn', 'landing-screen', 'file-mode-guide', 'removal-rate-row'];
    const show = ['viewer-section', 'evidence-locker', 'quote-metadata', 'physics-section', 'configuration-section', 'economics-section', 'result-card', 'traveler-zone', 'tag-zone', 'home-btn', 'shape-configurator'];
    
    hide.forEach(id => { const el = document.getElementById(id); if(el) el.style.display = 'none'; });
    show.forEach(id => { 
        const el = document.getElementById(id); 
        if(el) {
            el.style.display = 'block';
            if(id === 'result-card') el.classList.add('visible');
        }
    });
    
    // Phase 5.5: Part volume is now calculated from parametric shape, not manual input
    
    // Defaults
    setVal('stock-x', 4.0); setVal('stock-y', 2.0); setVal('stock-z', 1.0);
    setVal('setup-time', 60); setVal('shop-rate', 75);

    // Default Material (Prevent Calc Error)
    const matSelect = document.getElementById('material-select');
    if (matSelect && !matSelect.value) {
        if (matSelect.querySelector('option[value="Aluminum 6061"]')) matSelect.value = "Aluminum 6061";
        else if (matSelect.options.length > 1) matSelect.selectedIndex = 1;
    }

    // ALWAYS generate new Quote ID (fresh quote every time)
    const quoteIdInput = document.getElementById('quote-id-input');
    if (quoteIdInput) {
        quoteIdInput.value = generateDefaultQuoteId();
    }
    
    // ALWAYS generate new default name (fresh quote every time)
    const refInput = document.getElementById('reference-name-input');
    if (refInput) {
        refInput.value = `Manual Quote - ${new Date().toLocaleTimeString()}`;
    }
    
    // PHASE 4: Clear identity fields (Customer/Contact) for new quote
    const customerInput = document.getElementById('customer-input');
    if (customerInput) {
        customerInput.value = '';
        delete customerInput.dataset.selectedId;
        delete customerInput.dataset.selectedDomain;
    }
    
    const contactInput = document.getElementById('contact-input');
    if (contactInput) {
        contactInput.value = '';
        contactInput.disabled = true;
        delete contactInput.dataset.selectedId;
        delete contactInput.dataset.selectedEmail;
        delete contactInput.dataset.customerId;
    }

    // Calc Initial State
    updatePartVolumeFromRemovalRate(); 
}

// --- SWITCH TO FILE MODE (From Landing Screen) ---
export function initFileMode() {
    state.setIsManualMode(false);
    state.setCurrentDbId(null); // Reset for new quote
    state.setSelectedFile(null); // Clear selected file
    
    // CRITICAL: Unlock price (user is starting a new quote)
    variance.unlockPrice();
    
    // FIX: Clear traveler tags for new quote
    state.clearAllTravelers();
    state.clearAllTags();
    ui.renderTravelerBadges(); // Re-render with cleared state
    
    // Toggle UI Visibility (New Flow: Hide landing screen, show upload zone & home button)
    // NOTE: file-input is NEVER shown - it's triggered programmatically via click()
    // NOTE: stl-viewer is NOT in hide list - it should remain available for displayResult() to show
    // PHASE 4: Sections will be shown by displayResult() when calculation completes
    const show = ['upload-zone', 'calculate-btn', 'home-btn'];
    const hide = ['evidence-locker', 'quote-metadata', 'physics-section', 'configuration-section', 'economics-section', 'bob-guide', 'file-mode-guide', 'removal-rate-row', 'landing-screen', 'shape-configurator'];
    
    show.forEach(id => { 
        const el = document.getElementById(id); 
        if(el) el.style.display = (id === 'upload-zone') ? 'flex' : 'block';
    });
    
    // Also show .button-center container (required for calculate button visibility)
    const buttonCenter = document.querySelector('.button-center');
    if (buttonCenter) buttonCenter.style.display = 'flex';
    
    hide.forEach(id => { 
        const el = document.getElementById(id); 
        if(el) el.style.display = 'none'; 
    });
    
    // Ensure Calculate button starts disabled (no file selected yet)
    const calcBtn = document.getElementById('calculate-btn');
    if (calcBtn) calcBtn.disabled = true;
    
    // Clear file name display
    const fileNameEl = document.getElementById('file-name');
    if (fileNameEl) fileNameEl.textContent = '';
    
    // CRITICAL: Reset file input so it can accept the same file again
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
    
    // Reset result card (remove visible class but don't force display:none)
    const resultCard = document.getElementById('result-card');
    if (resultCard) {
        resultCard.classList.remove('visible');
        // Ensure no inline display:none blocking future visibility
        resultCard.style.display = '';
    }
    
    // Hide Market Radar
    const marketRadar = document.getElementById('market-radar');
    if (marketRadar) marketRadar.style.display = 'none';
    
    // Clear any error messages
    const errorEl = document.getElementById('error-message');
    if (errorEl) errorEl.classList.remove('visible');
    
    // Clear quote metadata fields for fresh start (same as showLandingScreen)
    const quoteIdInput = document.getElementById('quote-id-input');
    if (quoteIdInput) quoteIdInput.value = '';
    
    const refInput = document.getElementById('reference-name-input');
    if (refInput) refInput.value = '';
    
    const quantityInput = document.getElementById('quantity-input');
    if (quantityInput) quantityInput.value = '1';
    
    // Phase 5: Complexity slider removed (Glass Box integrity)
    
    // PHASE 4: Clear identity fields (Customer/Contact)
    const customerInput = document.getElementById('customer-input');
    if (customerInput) {
        customerInput.value = '';
        delete customerInput.dataset.selectedId;
        delete customerInput.dataset.selectedDomain;
    }
    
    const contactInput = document.getElementById('contact-input');
    if (contactInput) {
        contactInput.value = '';
        contactInput.disabled = true;
        delete contactInput.dataset.selectedId;
        delete contactInput.dataset.selectedEmail;
        delete contactInput.dataset.customerId;
    }
    
    // CRITICAL: Part Volume is READ-ONLY in File Mode (derived from 3D model)
    const partVolInput = document.getElementById('part-volume-input');
    if (partVolInput) {
        partVolInput.readOnly = true;
        partVolInput.style.backgroundColor = '#2a2a2a'; // Darker gray (read-only)
        partVolInput.style.cursor = 'not-allowed';
        partVolInput.title = 'Part volume is calculated from the 3D model (read-only)';
    }
    
    console.log("✅ Switched to File Mode (Ready for new file selection)");
}

// --- RETURN TO LANDING SCREEN ---
export function showLandingScreen() {
    state.setIsManualMode(false);
    state.setCurrentDbId(null); // Reset for new quote
    state.setSelectedFile(null); // Clear selected file
    
    // FIX: Clear all tags when returning to landing screen (starting fresh)
    state.clearAllTravelers();
    state.clearAllTags();
    ui.renderTravelerBadges(); // Re-render with cleared state
    
    // Show landing screen, hide everything else
    // NOTE: file-input stays hidden (display: none in CSS) - never manually show/hide it
    // PHASE 4: Hide all 4 sections when returning to landing
    const show = ['landing-screen'];
    const hide = ['upload-zone', 'calculate-btn', 'home-btn', 
                  'evidence-locker', 'quote-metadata', 'physics-section', 'configuration-section', 'economics-section', 'bob-guide', 'file-mode-guide', 'removal-rate-row', 'viewer-section',
                  'result-card', 'traveler-zone', 'tag-zone', 'shape-configurator'];
    
    show.forEach(id => { 
        const el = document.getElementById(id); 
        if(el) el.style.display = 'block';
    });
    
    hide.forEach(id => { 
        const el = document.getElementById(id); 
        if(el) el.style.display = 'none'; 
    });
    
    // Reset Calculate button to disabled state
    const calcBtn = document.getElementById('calculate-btn');
    if (calcBtn) calcBtn.disabled = true;
    
    // Clear file name display
    const fileNameEl = document.getElementById('file-name');
    if (fileNameEl) fileNameEl.textContent = '';
    
    // CRITICAL: Reset file input so it can accept files again
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
    
    // Hide result card
    const resultCard = document.getElementById('result-card');
    if (resultCard) resultCard.classList.remove('visible');
    
    // Hide Market Radar
    const marketRadar = document.getElementById('market-radar');
    if (marketRadar) marketRadar.style.display = 'none';
    
    // Clear any error messages
    const errorEl = document.getElementById('error-message');
    if (errorEl) errorEl.classList.remove('visible');
    
    // Reset Part Volume input to neutral state
    const partVolInput = document.getElementById('part-volume-input');
    if (partVolInput) {
        partVolInput.readOnly = false;
        partVolInput.value = '0';
        partVolInput.style.backgroundColor = '#1a1a1a';
        partVolInput.style.cursor = 'text';
        partVolInput.title = '';
    }
    
    // Clear quote metadata fields for fresh start
    const quoteIdInput = document.getElementById('quote-id-input');
    if (quoteIdInput) quoteIdInput.value = '';
    
    const refInput = document.getElementById('reference-name-input');
    if (refInput) refInput.value = '';
    
    const quantityInput = document.getElementById('quantity-input');
    if (quantityInput) quantityInput.value = '1';
    
    // PHASE 4: Clear identity fields (Customer/Contact)
    const customerInput = document.getElementById('customer-input');
    if (customerInput) {
        customerInput.value = '';
        delete customerInput.dataset.selectedId;
        delete customerInput.dataset.selectedDomain;
    }
    
    const contactInput = document.getElementById('contact-input');
    if (contactInput) {
        contactInput.value = '';
        contactInput.disabled = true;
        delete contactInput.dataset.selectedId;
        delete contactInput.dataset.selectedEmail;
        delete contactInput.dataset.customerId;
    }
    
    // Phase 5: Complexity slider removed (Glass Box integrity)
    
    // Reset removal rate slider (Napkin Mode specific)
    const removalSlider = document.getElementById('removal-rate-slider');
    if (removalSlider) removalSlider.value = '50';
    
    // CRITICAL: Unlock price (user is starting a new quote)
    variance.unlockPrice();
    
    console.log("✅ Returned to Landing Screen (All state cleared)");
}

// --- LINKED LEVERS ---

// ==== PHASE 3: VALIDATED LINKED LEVERS ====
// Lever 1: Slider -> Updates Volume (with validation)
export function updatePartVolumeFromRemovalRate() {
    const stockVol = getStockVolume();
    const slider = document.getElementById('removal-rate-slider');
    const rate = slider ? parseFloat(slider.value) : 50;

    setText('removal-rate-value', `${rate.toFixed(1)}%`);
    
    // Calculate Part Volume (can never be negative)
    let partVol = stockVol * (1 - (rate / 100));
    partVol = Math.max(0, partVol); // Ensure non-negative
    
    // Calculate Removal Volume (Stock - Part)
    const removalVol = stockVol - partVol;
    
    // PHASE 3 VALIDATION: Removal volume cannot be negative
    if (removalVol < 0) {
        console.warn(`⚠️ Invalid state: Removal volume cannot be negative (${removalVol.toFixed(3)})`);
        // Clamp part volume to stock volume
        partVol = stockVol;
    }
    
    // Update Input (if not focused)
    const input = document.getElementById('part-volume-input');
    if (input && document.activeElement !== input) {
        input.value = partVol.toFixed(3);
    }
    
    triggerCalc();
}

// Lever 2: Volume Input -> Updates Slider (Reverse Drive with validation)
export function updateRemovalRateFromPartVolume() {
    const stockVol = getStockVolume();
    const input = document.getElementById('part-volume-input');
    let partVol = input ? parseFloat(input.value) : 0;
    
    if (stockVol <= 0) return;
    
    // PHASE 3 VALIDATION: Part volume cannot exceed stock volume
    if (partVol > stockVol) {
        console.warn(`⚠️ Part volume (${partVol.toFixed(3)}) exceeds stock volume (${stockVol.toFixed(3)}). Showing warning.`);
        
        // Show popup warning to user
        showPartVolumeWarning(partVol, stockVol);
        
        // Clamp to stock volume (auto-fix)
        partVol = stockVol;
        if (input) input.value = partVol.toFixed(3);
    }
    
    // PHASE 3 VALIDATION: Part volume cannot be negative
    if (partVol < 0) {
        console.warn(`⚠️ Part volume cannot be negative. Resetting to 0.`);
        partVol = 0;
        if (input) input.value = '0.000';
    }

    // Calc Rate: Rate = (1 - Part/Stock) * 100
    let rate = (1 - (partVol / stockVol)) * 100;
    
    // Clamp 0-100
    rate = Math.max(0, Math.min(100, rate));
    
    // Update Slider
    const slider = document.getElementById('removal-rate-slider');
    if (slider) slider.value = rate;
    setText('removal-rate-value', `${rate.toFixed(1)}%`);
    
    triggerCalc();
}

// Lever 3: Stock -> Updates Volume (maintaining Rate)
export function updateStockDimensions() {
    // Apply Bob's Reality Check: Snap to purchasable stock sizes
    snapStockToStandard();
    
    // Then recalculate part volume
    updatePartVolumeFromRemovalRate();
}

/**
 * Snap stock dimensions to standard commercial sizes (The Bob Reality Check)
 * EXPORTED so File Mode can use the same logic
 */
export function snapStockToStandard() {
    const currentDims = {
        x: parseFloat(getVal('stock-x')) || 0,
        y: parseFloat(getVal('stock-y')) || 0,
        z: parseFloat(getVal('stock-z')) || 0
    };
    
    // Skip if any dimension is invalid
    if (currentDims.x <= 0 || currentDims.y <= 0 || currentDims.z <= 0) return;
    
    // Get snapped dimensions
    const snapped = stock.snapStockDimensions(currentDims);
    
    // Apply with visual feedback (only if changed)
    stock.applySnappedDimensions(snapped);
}

// --- CALCULATION ---

let calcTimer = null;
function triggerCalc() {
    if (calcTimer) clearTimeout(calcTimer);
    calcTimer = setTimeout(calculateManualQuote, 200); // 200ms debounce
}

export async function calculateManualQuote() {
    // Re-read inputs immediately before sending to ensure freshness
    const stockX = parseFloat(getVal('stock-x')) || 0;
    const stockY = parseFloat(getVal('stock-y')) || 0;
    const stockZ = parseFloat(getVal('stock-z')) || 0;
    const material = document.getElementById('material-select')?.value;
    // Phase 5.5: Get part volume from parametric configurator instead of input field
    const partVol = parametric.getCurrentPartVolume() || 0;
    const quantity = parseInt(document.getElementById('quantity-input')?.value) || 1;

    if (!material) return;
    
    // Phase 5.5: Don't validate if part volume is 0 (user hasn't selected a shape yet)
    if (partVol === 0) {
        console.log('⏳ Waiting for shape configuration...');
        return; // Silently return, no error needed
    }
    
    // Client-side validation: Part volume cannot exceed stock volume
    const stockVol = stockX * stockY * stockZ;
    const errorDiv = document.getElementById('part-volume-error');
    
    if (partVol > stockVol) {
        // Show inline error (don't use popup for better UX)
        if (errorDiv) {
            errorDiv.style.display = 'block';
        }
        
        console.warn(`⚠️ Validation: Part volume (${partVol.toFixed(3)}) > Stock volume (${stockVol.toFixed(3)})`);
        return; // Don't proceed with calculation
    }
    
    // Clear error if validation passes
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }

    // FIX: Debug Payload to Console
    const payload = {
        stock_x: stockX, stock_y: stockY, stock_z: stockZ,
        material_name: material,
        part_volume: partVol,
        // Phase 5: complexity removed (always 1.0 for pure physics)
        setup_time: parseFloat(getVal('setup-time')) || 60,
        shop_rate: parseFloat(getVal('shop-rate')) || 75,
        quantity: quantity,
        handling_time: parseFloat(getVal('handling-time')) || 0.5,
        filename: getVal('reference-name-input') || 'Manual Quote',
        ops_mode: state.getOpsMode()
    };
    
    console.log("MANUAL QUOTE PAYLOAD:", payload);

    try {
        const response = await fetch('/manual_quote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const data = await response.json();
            console.log("MANUAL QUOTE RESPONSE:", data);
            state.setCurrentQuoteData(data);
            ui.displayResult(data);
        } else {
            // Handle validation errors "loudly"
            const errorText = await response.text();
            console.error("Manual Quote Failed:", errorText);
            
            try {
                const errObj = JSON.parse(errorText);
                ui.showError(`❌ ${errObj.error}`);
            } catch (e) {
                ui.showError(`❌ Server Error (${response.status}): ${errorText.substring(0, 100)}`);
            }
        }
    } catch (e) { 
        console.error(e); 
        ui.showError(`❌ Network Error: ${e.message}`);
    }
}

// Helpers
function getStockVolume() {
    const x = parseFloat(getVal('stock-x')) || 0;
    const y = parseFloat(getVal('stock-y')) || 0;
    const z = parseFloat(getVal('stock-z')) || 0;
    
    // PHASE 3 VALIDATION: Stock dimensions must all be positive
    if (x <= 0 || y <= 0 || z <= 0) {
        console.warn(`⚠️ Invalid stock dimensions: X=${x}, Y=${y}, Z=${z}`);
        // Don't calculate if any dimension is invalid
        setText('stock-volume', '0.000 in³');
        return 0;
    }
    
    const vol = x * y * z;
    setText('stock-volume', `${vol.toFixed(3)} in³`);
    return vol;
}

/**
 * Update stock volume display (exported for File Mode to use)
 */
export function updateStockVolumeDisplay() {
    const x = parseFloat(document.getElementById('stock-x')?.value) || 0;
    const y = parseFloat(document.getElementById('stock-y')?.value) || 0;
    const z = parseFloat(document.getElementById('stock-z')?.value) || 0;
    
    if (x <= 0 || y <= 0 || z <= 0) {
        const el = document.getElementById('stock-volume');
        if (el) el.textContent = '0.000 in³';
        return;
    }
    
    const vol = x * y * z;
    const el = document.getElementById('stock-volume');
    if (el) {
        el.textContent = `${vol.toFixed(3)} in³`;
        console.log(`📦 Stock volume updated: ${vol.toFixed(3)} in³`);
    }
}

function getVal(id) { return document.getElementById(id)?.value || 0; }
function setVal(id, v) { const el = document.getElementById(id); if(el) el.value = v; }
function setText(id, t) { const el = document.getElementById(id); if(el) el.textContent = t; }

// PHASE 3: Visual validation feedback
function showLinkedLeverWarning(message) {
    // Use centralized error display for consistent viewport positioning
    ui.showError(`⚠️ Linked Lever Warning: ${message}`);
}

/**
 * Show popup warning when part volume exceeds stock volume
 * Uses viewport-fixed error display for visibility (Phase 4 UX improvement)
 */
function showPartVolumeWarning(partVol, stockVol) {
    const message = `⚠️ PART VOLUME EXCEEDS STOCK SIZE

Part Volume: ${partVol.toFixed(3)} in³
Stock Volume: ${stockVol.toFixed(3)} in³

The finished part cannot be larger than the stock material. Please reduce the Part Volume or increase the Stock Dimensions.`;

    ui.showError(message);
    
    console.warn(`⚠️ Validation Failed: Part volume (${partVol.toFixed(3)}) > Stock volume (${stockVol.toFixed(3)})`);
}
