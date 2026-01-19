/**
 * ui.js - UI/DOM Manipulation Module
 */

import * as state from './state.js';
import * as api from './api.js';
import * as viewer from './viewer.js';
import * as stock from './stock.js';
import * as variance from './variance.js';

// ==== PHASE 3: DEBOUNCING UTILITY (Fixes Slider Jitter) ====
// Global debounce timers for different slider types
const debounceTimers = {
    complexity: null,
    tagSlider: null,
    setupTime: null,
    shopRate: null,
    quantity: null
};

/**
 * Debounced slider handler - Prevents API spam during drag
 * @param {string} timerKey - The timer identifier
 * @param {Function} callback - The function to call after debounce
 * @param {number} delay - Milliseconds to wait (default 300ms)
 */
export function debounceSlider(timerKey, callback, delay = 300) {
    if (debounceTimers[timerKey]) {
        clearTimeout(debounceTimers[timerKey]);
    }
    
    debounceTimers[timerKey] = setTimeout(() => {
        callback();
        debounceTimers[timerKey] = null;
    }, delay);
}

// Helper: Check if element is currently focused
function isFocused(elementId) {
    const el = document.getElementById(elementId);
    return el && document.activeElement === el;
}

// =========================================================================
// REFACTORING STRIKE 2: Extracted Functions from displayResult()
// =========================================================================

/**
 * Update the price card with calculated costs and runtime.
 * Phase 4 Ready: Can be conditionally hidden for "Blind Mode" (User role).
 * 
 * @param {Object} data - Quote data from backend
 * @param {number} quantity - Number of parts to quote
 * @returns {number} finalTotal - Final price after markups (needed for Market Radar)
 */
function updatePriceCard(data, quantity) {
    if (!data) return 0;
    
    const priceData = data.physics_price || data.price || {};
    let basePrice = priceData.total_price || 0.0;
    
    // Calculate Markup from active tags
    let totalMarkupPercent = 0;
    Object.keys(state.activeMarkups).forEach(tag => {
        if (state.selectedTags.has(tag)) {
            totalMarkupPercent += state.activeMarkups[tag];
        }
    });
    
    const finalTotal = basePrice * (1 + (totalMarkupPercent / 100));
    const pricePerPart = finalTotal / quantity;
    
    // CRITICAL: Check if user has manually entered a price (Glass Box override)
    const finalPriceInput = document.getElementById('final-price-input');
    let displayTotal, displayPerUnit;
    
    if (finalPriceInput && finalPriceInput.value && parseFloat(finalPriceInput.value) > 0) {
        // User has entered a manual per-unit price - use that
        displayPerUnit = parseFloat(finalPriceInput.value);
        displayTotal = displayPerUnit * quantity;
        console.log(`[UI] Using user's manual price: $${displayPerUnit.toFixed(2)}/unit × ${quantity} = $${displayTotal.toFixed(2)}`);
    } else {
        // No manual price - use anchor
        displayTotal = finalTotal;
        displayPerUnit = pricePerPart;
    }
    
    // Update Main Price Display (with per-part breakdown if Qty > 1)
    const mainPriceText = quantity > 1 
        ? `$${displayTotal.toFixed(2)} ($${displayPerUnit.toFixed(2)}/ea)`
        : `$${displayTotal.toFixed(2)}`;
    
    updateText('total-price', mainPriceText);
    updateText('hud-price', mainPriceText);  // Sync with HUD
    
    // Update Cost Breakdown
    updateText('material-cost', `$${(priceData.material_cost || 0).toFixed(2)}`);
    updateText('labor-cost', `$${(priceData.labor_cost || 0).toFixed(2)}`);
    updateText('stock-volume', `${(data.stock?.volume || 0).toFixed(3)} in³`);
    
    // Update Runtime
    const runtime = data.runtime || {};
    const totalRuntime = data.total_runtime_mins || runtime.total_time_mins || runtime.minutes || 0;
    updateText('runtime', `${totalRuntime.toFixed(1)} mins`);
    
    return displayTotal;  // Return for Market Radar positioning
}

/**
 * Update stock dimension inputs with "Active Input Guard".
 * FILE MODE: Snaps to standard purchasable sizes ("Bob's Reality Check").
 * NAPKIN MODE: Uses values as-is (snapping handled in manual.js).
 * 
 * @param {Object} data - Quote data from backend
 */
function updateStockInputs(data) {
    if (!data || !data.stock) return;
    
    if (!state.getIsManualMode()) {
        // FILE MODE: Apply "Bob's Reality Check" - snap to purchasable stock sizes
        const snappedStock = stock.snapStockDimensions({
            x: data.stock.x || 0,
            y: data.stock.y || 0,
            z: data.stock.z || 0
        });
        
        updateInputSafe('stock-x', snappedStock.x);
        updateInputSafe('stock-y', snappedStock.y);
        updateInputSafe('stock-z', snappedStock.z);
        
        console.log('📏 Stock dimensions snapped to standard sizes:', snappedStock);
    } else {
        // NAPKIN MODE: Use as-is (snapping happens in manual.js on user input)
        updateInputSafe('stock-x', data.stock.x);
        updateInputSafe('stock-y', data.stock.y);
        updateInputSafe('stock-z', data.stock.z);
    }
}

/**
 * Update part volume input with mode-specific logic.
 * FILE MODE: Always update (read-only, derived from 3D model).
 * NAPKIN MODE: Only update if user isn't actively editing.
 * 
 * @param {Object} data - Quote data from backend
 */
function updatePartVolume(data) {
    const partVolInput = document.getElementById('part-volume-input');
    if (!partVolInput) return;
    
    // Debug logging
    console.log('📐 Part Volume Debug:');
    console.log('   data.geometry:', data.geometry);
    console.log('   data.geometry?.volume:', data.geometry?.volume);
    console.log('   data.part_volume:', data.part_volume);
    
    const vol = data.geometry?.volume || data.part_volume || 0;
    console.log('   Resolved volume:', vol);
    
    const isManualMode = state.getIsManualMode();
    console.log('   isManualMode:', isManualMode);
    
    if (!isManualMode) {
        // FILE MODE: Always populate from model geometry
        partVolInput.value = vol.toFixed(4);
        console.log(`   ✅ File Mode: Part Volume set to ${vol.toFixed(4)} in³`);
    } else if (!isFocused('part-volume-input')) {
        // NAPKIN MODE: Only update if user isn't actively editing
        partVolInput.value = vol.toFixed(4);
        console.log(`   ✅ Napkin Mode: Part Volume set to ${vol.toFixed(4)} in³`);
    } else {
        console.log('   ⏭️ Napkin Mode: Skipping update (field is focused)');
    }
}

/**
 * Update material select dropdown.
 * Dynamically adds material if it doesn't exist in the dropdown.
 * 
 * @param {Object} data - Quote data from backend
 */
function updateMaterialSelect(data) {
    const matSelect = document.getElementById('material-select');
    if (!matSelect || !data.material) return;
    
    // Add material to dropdown if it doesn't exist
    if (!matSelect.querySelector(`option[value="${data.material}"]`)) {
        const opt = document.createElement('option');
        opt.value = data.material;
        opt.textContent = data.material;
        matSelect.appendChild(opt);
    }
    
    // ONLY update if user is not actively using the dropdown
    // (Prevents "snap back" bug when user is selecting a different material)
    if (document.activeElement !== matSelect) {
        matSelect.value = data.material;
    }
}

/**
 * Update Market Radar (Market Intelligence visualization).
 * Phase 4 Ready: This section will be visible to both Bob and Tim.
 * 
 * @param {Object} data - Quote data from backend
 * @param {number} finalTotal - Final price after markups (for marker positioning)
 */
function updateMarketRadar(data, finalTotal) {
    const marketRadar = document.getElementById('market-radar');
    if (!marketRadar) return;
    
    if (!data.market_analysis) {
        // No market data - hide radar
        marketRadar.style.display = 'none';
        return;
    }
    
    const analysis = data.market_analysis;
    const stats = analysis.cluster_stats;
    
    // Show radar
    marketRadar.style.display = 'block';
    
    // Populate metrics
    updateText('radar-count', stats.count);
    updateText('radar-median', `$${stats.median_price.toFixed(2)}`);
    updateText('radar-variance', `${analysis.variance_pct > 0 ? '+' : ''}${analysis.variance_pct}%`);
    
    // Update status badge
    const badge = document.getElementById('radar-status-badge');
    if (badge) {
        badge.textContent = analysis.recommendation.toUpperCase();
        badge.className = 'radar-badge ' + analysis.recommendation.toLowerCase();
    }
    
    // Update range labels
    updateText('radar-min', `$${stats.min_price.toFixed(0)}`);
    updateText('radar-max', `$${stats.max_price.toFixed(0)}`);
    
    // Position the marker on the range track
    const marker = document.getElementById('radar-marker');
    if (marker && stats.max_price > stats.min_price) {
        const range = stats.max_price - stats.min_price;
        const position = ((finalTotal - stats.min_price) / range) * 100;
        const clampedPosition = Math.max(0, Math.min(100, position));
        marker.style.left = `${clampedPosition}%`;
    }
}

/**
 * Setup File Mode specific UI elements (3D Viewer, guides, metadata).
 * Only called when in File Mode (!isManualMode).
 * 
 * @param {Object} data - Quote data from backend
 */
/**
 * Update Extracted Geometry section (Phase 5.6 - Unit Verification)
 * Shows part volume and assumed units, allows user to correct if wrong
 */
function updateExtractedGeometry(data) {
    const section = document.getElementById('extracted-geometry-section');
    const bboxDisplay = document.getElementById('bbox-display');
    const volumeDisplay = document.getElementById('part-volume-display');
    const warningIcon = document.getElementById('unit-warning');
    
    if (!section || !bboxDisplay || !volumeDisplay || !warningIcon) {
        console.warn('[Unit Verification] Extracted geometry elements not found');
        return;
    }
    
    // Get geometry data
    const volume = data.geometry?.volume || data.part_volume || 0;
    const assumedUnits = data.assumed_units || 'in';  // Default to inches
    const bbox = data.geometry?.bbox || { x: 0, y: 0, z: 0 };
    
    // Show section (File Mode only)
    section.style.display = 'block';
    
    // Update bounding box display (X × Y × Z format)
    const bboxText = `${bbox.x.toFixed(2)} × ${bbox.y.toFixed(2)} × ${bbox.z.toFixed(2)} ${assumedUnits}`;
    bboxDisplay.textContent = bboxText;
    
    // Update volume display
    volumeDisplay.textContent = `${volume.toFixed(3)} ${assumedUnits}³`;
    
    // Show warning icon if dimensions seem unusual (conservative heuristic)
    const shouldWarn = checkDimensionsUnusual(bbox, assumedUnits);
    warningIcon.style.display = shouldWarn ? 'inline' : 'none';
    
    // Store current geometry in global scope for unit conversion
    window.currentGeometry = {
        originalVolume: volume,
        currentUnits: assumedUnits,
        dimensions: bbox,
        data: data  // Keep reference to full data for repricing
    };
    
    console.log(`[Unit Verification] BBox: ${bboxText}, Volume: ${volume.toFixed(3)} ${assumedUnits}³, Warning: ${shouldWarn}`);
}

/**
 * Check if dimensions seem unusual (conservative heuristic for warning icon)
 * Only warn when VERY likely wrong to avoid false positives
 */
function checkDimensionsUnusual(bbox, units) {
    const maxDim = Math.max(bbox.x, bbox.y, bbox.z);
    const minDim = Math.min(bbox.x, bbox.y, bbox.z);
    
    // Conservative checks - only warn when extremely likely wrong
    if (units === 'in') {
        // If guessed inches but part is > 100", probably mm
        if (maxDim > 100) return true;
        // If guessed inches but part is < 0.01", probably corrupt
        if (maxDim < 0.01) return true;
    } else if (units === 'mm') {
        // If guessed mm but part is < 1mm, probably inches
        if (maxDim < 1) return true;
        // If guessed mm but part is > 5000mm (5 meters), probably inches
        if (maxDim > 5000) return true;
    }
    
    return false;  // Dimensions seem reasonable
}

/**
 * Initialize quick-fix buttons for unit conversion (Phase 5.6 - Enhanced UX)
 * Called once when page loads
 */
export function initQuickFixButtons() {
    const btnMM = document.getElementById('quick-convert-mm');
    const btnIN = document.getElementById('quick-convert-in');
    
    if (!btnMM || !btnIN) {
        console.warn('[Unit Verification] Quick-fix buttons not found');
        return;
    }
    
    // Convert to mm button
    btnMM.addEventListener('click', async function() {
        await performUnitConversion('mm');
    });
    
    // Convert to in button
    btnIN.addEventListener('click', async function() {
        await performUnitConversion('in');
    });
    
    console.log('[Unit Verification] Quick-fix buttons initialized');
}

/**
 * Perform unit conversion to target unit
 */
async function performUnitConversion(toUnit) {
    const currentData = window.currentGeometry;
    
    if (!currentData) {
        console.warn('[Unit Verification] No geometry data available');
        showToast('No geometry data available', 'error');
        return;
    }
    
    const fromUnit = currentData.currentUnits;
    const originalVolume = currentData.originalVolume;
    const dimensions = currentData.dimensions;
    
    // Don't convert if already in target unit
    if (fromUnit === toUnit) {
        showToast(`Already in ${toUnit}`, 'info');
        return;
    }
    
    console.log(`[Unit Verification] Converting ${originalVolume} ${fromUnit}³ → ${toUnit}³`);
    
    // Disable buttons during conversion
    const btnMM = document.getElementById('quick-convert-mm');
    const btnIN = document.getElementById('quick-convert-in');
    if (btnMM) btnMM.disabled = true;
    if (btnIN) btnIN.disabled = true;
    
    try {
        // Call /api/convert_units endpoint with dimensions
        const response = await fetch('/api/convert_units', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                original_volume: originalVolume,
                dimensions: dimensions,  // NEW: Send dimensions for bbox conversion
                from_unit: fromUnit,
                to_unit: toUnit
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            const convertedVolume = result.converted_volume;
            const convertedDims = result.converted_dimensions;
            
            // Update bounding box display
            const bboxDisplay = document.getElementById('bbox-display');
            if (bboxDisplay && convertedDims) {
                const bboxText = `${convertedDims.x.toFixed(2)} × ${convertedDims.y.toFixed(2)} × ${convertedDims.z.toFixed(2)} ${toUnit}`;
                bboxDisplay.textContent = bboxText;
            }
            
            // Update volume display
            const volumeDisplay = document.getElementById('part-volume-display');
            if (volumeDisplay) {
                volumeDisplay.textContent = `${convertedVolume.toFixed(3)} ${toUnit}³`;
            }
            
            // Update warning icon based on new dimensions
            const warningIcon = document.getElementById('unit-warning');
            if (warningIcon && convertedDims) {
                const shouldWarn = checkDimensionsUnusual(convertedDims, toUnit);
                warningIcon.style.display = shouldWarn ? 'inline' : 'none';
            }
            
            // Update stored data
            window.currentGeometry.originalVolume = convertedVolume;
            window.currentGeometry.currentUnits = toUnit;
            window.currentGeometry.dimensions = convertedDims || dimensions;
            
            console.log(`[Unit Verification] ✓ Converted to ${convertedVolume.toFixed(3)} ${toUnit}³`);
            
            // Show success toast
            showToast(`Units converted to ${toUnit}`, 'success');
            
            // TODO: Trigger full repricing with new volume
            // This would require recalculating with the backend
            console.log('[Unit Verification] ⚠️ Manual repricing required - refresh to recalculate');
            
        } else {
            console.error('[Unit Verification] Conversion failed:', result.error);
            showToast(`Conversion failed: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('[Unit Verification] API call failed:', error);
        showToast('Failed to convert units. Please try again.', 'error');
    } finally {
        // Re-enable buttons
        if (btnMM) btnMM.disabled = false;
        if (btnIN) btnIN.disabled = false;
    }
}

function setupFileMode3DViewer(data) {
    // Hide upload zone and calculate button
    const uploadZone = document.getElementById('upload-zone');
    if (uploadZone) uploadZone.style.display = 'none';
    
    const calculateBtn = document.getElementById('calculate-btn');
    if (calculateBtn) calculateBtn.style.display = 'none';
    
    // Show Quote Metadata Section
    const quoteMetadata = document.getElementById('quote-metadata');
    if (quoteMetadata) quoteMetadata.style.display = 'block';
    
    // ALWAYS generate new Quote ID (fresh quote every time)
    const quoteIdInput = document.getElementById('quote-id-input');
    if (quoteIdInput) {
        const today = new Date();
        const dateStr = today.toISOString().slice(0, 10).replace(/-/g, '');
        const randomNum = Math.floor(Math.random() * 900) + 100;
        quoteIdInput.value = `Q-${dateStr}-${randomNum}`;
    }
    
    // ALWAYS auto-fill Quote Reference with filename (fresh quote every time)
    const refInput = document.getElementById('reference-name-input');
    if (refInput && data.filename) {
        const cleanName = data.filename.replace(/\.(step|stp|stl)$/i, '').replace(/_/g, ' ');
        refInput.value = cleanName;
    }
    
    // Show File Mode Guide
    const fileModeGuide = document.getElementById('file-mode-guide');
    if (fileModeGuide) {
        fileModeGuide.style.display = 'block';
        
        const filenameDisplay = document.getElementById('file-mode-filename');
        if (filenameDisplay && data.filename) {
            filenameDisplay.textContent = data.filename;
        }
    }
    
    // Show 3D Viewer Section
    const viewerSection = document.getElementById('viewer-section');
    if (viewerSection) {
        viewerSection.style.display = 'block';
        console.log('📍 3D Viewer container shown');
        console.log('📐 Viewer Section dimensions:', viewerSection.offsetWidth, 'x', viewerSection.offsetHeight);
    }
    
    const viewerDiv = document.getElementById('stl-viewer');
    if (viewerDiv) {
        viewerDiv.style.display = 'block';
        console.log('📍 3D Viewer element shown');
        console.log('📐 STL Viewer dimensions:', viewerDiv.offsetWidth, 'x', viewerDiv.offsetHeight);
        
        // Force canvas resize after viewer becomes visible
        setTimeout(() => {
            viewer.forceResize();
            
            // DEBUG: Verify canvas is now correct size
            console.log('📐 STL Viewer dimensions (after delay):', viewerDiv.offsetWidth, 'x', viewerDiv.offsetHeight);
            const canvas = viewerDiv.querySelector('canvas');
            if (canvas) {
                console.log('📐 Canvas dimensions:', canvas.offsetWidth, 'x', canvas.offsetHeight);
                console.log('🖱️ Canvas pointer-events:', window.getComputedStyle(canvas).pointerEvents);
            }
        }, 50);
    }
}

/**
 * Show result card and tag/traveler zones.
 * Common to both File and Napkin modes.
 * 
 * @param {Object} data - Quote data from backend
 */
function showResultUIElements(data) {
    // Show Results Card
    const card = document.getElementById('result-card');
    if (card) {
        card.classList.add('visible');
        card.style.display = '';
        console.log('📍 Result card made visible');
    }
    
    // PHASE 4: Show all 4 flow sections
    const quoteMetadata = document.getElementById('quote-metadata');
    if (quoteMetadata) quoteMetadata.style.display = 'block';
    
    const physicsSection = document.getElementById('physics-section');
    if (physicsSection) physicsSection.style.display = 'block';
    
    const configSection = document.getElementById('configuration-section');
    if (configSection) configSection.style.display = 'block';
    
    const economicsSection = document.getElementById('economics-section');
    if (economicsSection) economicsSection.style.display = 'block';
    
    // Show Tag and Traveler zones (legacy compatibility)
    const tagZone = document.getElementById('tag-zone');
    if (tagZone) tagZone.style.display = 'block';
    
    const travelerZone = document.getElementById('traveler-zone');
    if (travelerZone) travelerZone.style.display = 'block';
    
    // DUAL-MODE PARITY: Hide shape configurator in File Mode (Napkin Mode only)
    const shapeConfigurator = document.getElementById('shape-configurator');
    if (shapeConfigurator && !state.getIsManualMode()) {
        shapeConfigurator.style.display = 'none';
        console.log('🔒 Shape configurator hidden (File Mode)');
    }
    
    // Update Filename if provided
    if (data.filename) updateText('file-name', data.filename);
}

// =========================================================================
// MAIN ORCHESTRATOR (Refactored from 239 lines → ~25 lines)
// =========================================================================

export function displayResult(data) {
    if (!data) return;
    state.setCurrentQuoteData(data);
    
    // Get quantity for price calculations
    const qtyInput = document.getElementById('quantity-input');
    const quantity = qtyInput ? (parseInt(qtyInput.value) || 1) : 1;
    
    // Orchestrate UI updates (each function handles its own section)
    const finalTotal = updatePriceCard(data, quantity);       // Returns final price for Market Radar
    updateStockInputs(data);                                  // Stock X/Y/Z with snapping logic
    updatePartVolume(data);                                   // Part volume (mode-specific)
    updateMaterialSelect(data);                               // Material dropdown
    updateMarketRadar(data, finalTotal);                      // Market Intelligence
    variance.updateGlassBox(data);                            // Phase 4: Glass Box variance tracking
    showResultUIElements(data);                               // Result card + tags/travelers
    
    // File Mode specific: 3D Viewer setup + Unit Verification
    if (!state.getIsManualMode()) {
        setupFileMode3DViewer(data);
        updateExtractedGeometry(data);                        // Phase 5.6: Unit Verification
    } else {
        // Napkin Mode: Hide extracted geometry section
        const extractedGeometry = document.getElementById('extracted-geometry-section');
        if (extractedGeometry) extractedGeometry.style.display = 'none';
    }
}

// Helper for safe updates
function updateInputSafe(id, value) {
    const el = document.getElementById(id);
    if (el && document.activeElement !== el && value !== undefined) {
        el.value = parseFloat(value).toFixed(3);
    }
}

function updateText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

export async function loadHistory() {
    try {
        const historyData = await api.fetchHistory(); 
        const tbody = document.getElementById('history-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (!historyData || historyData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:#666;">No history yet</td></tr>';
            return;
        }

        // DEBUG: See exactly what the DB is returning
        console.log("📜 History Data Loaded:", historyData);

        historyData.forEach(item => {
            const row = document.createElement('tr');
            const isWon = item.status === 'Won';
            const isLost = item.status === 'Lost';
            
            // Format Quote ID
            const quoteId = item.quote_id || `#${item.id}`;
            
            // --- 1. Pricing Tags (Orange) ---
            let pricingTagsHtml = '';
            if (item.tag_weights && Object.keys(item.tag_weights).length > 0) {
                pricingTagsHtml = Object.keys(item.tag_weights).map(t => 
                    `<span class="status-badge" style="background:#444; color:#ccc; font-size:0.7em; margin-right:2px; margin-bottom:2px; display:inline-block;">${t}</span>`
                ).join('');
            }

            // --- 2. Traveler Tags (Blue) ---
            let travelerTagsHtml = '';
            // Robust check: Ensure it's an array and has items
            if (item.process_routing && Array.isArray(item.process_routing) && item.process_routing.length > 0) {
                travelerTagsHtml = item.process_routing.map(t => 
                    `<span class="traveler-badge-small">${t}</span>`
                ).join('');
            }

            // Combine Tags (Pricing + Break + Travelers)
            let combinedTags = pricingTagsHtml;
            if (pricingTagsHtml && travelerTagsHtml) combinedTags += '<br>';
            combinedTags += travelerTagsHtml;
            
            // Fallback
            if (!combinedTags) combinedTags = '<span style="color:#666;">-</span>';

            // Compliance Check (Janitor Protocol)
            let materialHtml = item.material;
            if (item.is_compliant === 0) {
                 materialHtml += ` <span style="cursor:pointer;" title="Non-Standard Material">⚠️</span>`;
            }

            // Action Buttons Logic
            let actionButtons = '';
            if (item.status === 'Draft') {
                // Draft: Show EDIT + WON/LOST + TRASH
                actionButtons = `
                    <button class="history-action-btn" onclick="window.loadQuoteFromHistory(${item.id})" style="background:#0066cc;">EDIT</button>
                    <button class="history-action-btn win" onclick="window.markWon(${item.id})">WON</button>
                    <button class="history-action-btn loss" onclick="window.markLost(${item.id})">LOST</button>
                `;
            } else if (!isWon && !isLost) {
                // Pending (not Draft, not Won/Lost)
                actionButtons = `
                    <button class="history-action-btn win" onclick="window.markWon(${item.id})">WON</button>
                    <button class="history-action-btn loss" onclick="window.markLost(${item.id})">LOST</button>
                `;
            }
            
            // Add TRASH button for ALL quotes (always available)
            actionButtons += `
                <button class="history-action-btn" 
                        onclick="window.confirmDeleteQuote(${item.id}, '${quoteId}')" 
                        style="background:#cc3333; margin-left:4px;" 
                        title="Archive this quote">
                    🗑️
                </button>
            `;
            
            row.innerHTML = `
                <td style="color: #ff6600; font-weight:bold; font-family: monospace;">${quoteId}</td>
                <td>${new Date(item.timestamp).toLocaleDateString()}</td>
                <td style="color: #cccccc;">${item.filename}</td>
                <td>$${item.final_price.toFixed(2)}</td>
                <td>${materialHtml}</td>
                <td>${item.setup_time}m</td>
                <td>${combinedTags}</td>
                <td>
                    <span class="status-badge ${item.status.toLowerCase()}" 
                          onclick="window.editStatus(${item.id}, '${item.status}')" 
                          style="cursor: pointer;" 
                          title="Click to change status">
                        ${item.status} ⚙️
                    </span>
                </td>
                <td>${actionButtons}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (e) {
        console.error("Failed to load history", e);
    }
}

// Modal & Toast Helpers
export function showToast(msg) {
    const t = document.getElementById('toast');
    if (t) { t.textContent = msg; t.classList.add('visible'); setTimeout(() => t.classList.remove('visible'), 3000); }
}

export function showError(msg) {
    const e = document.getElementById('error-message');
    if (!e) return;
    
    // Set error message
    e.textContent = msg;
    e.classList.add('visible');
    
    // Auto-dismiss after 5 seconds (longer than toast for readability)
    setTimeout(() => {
        e.classList.remove('visible');
    }, 5000);
    
    // Dismiss on click (user acknowledges error)
    const dismissHandler = () => {
        e.classList.remove('visible');
        e.removeEventListener('click', dismissHandler);
    };
    e.addEventListener('click', dismissHandler);
    
    console.log('[ERROR] Displayed to user:', msg);
}

// --- MODAL LOGIC & WINDOW EXPOSURE ---

// 1. Expose to Global Scope (Fixes "is not a function" error)
window.markWon = (id) => openModal('close-loop-modal', id);
window.markLost = (id) => openModal('loss-analysis-modal', id);

// Soft Delete Confirmation & Execution
window.confirmDeleteQuote = async (id, quoteIdDisplay) => {
    // Confirmation Dialog (Native - Air-Gapped)
    const confirmMsg = `Archive this quote?\n\nQuote: ${quoteIdDisplay}\nID: ${id}\n\n⚠️ This will:\n- Remove it from history\n- Exclude it from the learning model\n- Preserve the data for recovery\n\nContinue?`;
    
    if (!confirm(confirmMsg)) {
        console.log(`🚫 Delete cancelled for Quote ID ${id}`);
        return;
    }
    
    try {
        console.log(`🗑️ Deleting Quote ID ${id}...`);
        
        // Call backend endpoint
        const response = await fetch(`/delete_quote/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Delete failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Remove row from DOM (visual feedback)
            const row = document.querySelector(`#history-body tr[data-quote-id="${id}"]`);
            if (!row) {
                // Find row by scanning all rows for matching ID
                const allRows = document.querySelectorAll('#history-body tr');
                for (const r of allRows) {
                    const editBtn = r.querySelector(`button[onclick*="${id}"]`);
                    if (editBtn) {
                        r.style.transition = 'opacity 0.3s ease';
                        r.style.opacity = '0';
                        setTimeout(() => r.remove(), 300);
                        break;
                    }
                }
            } else {
                row.style.transition = 'opacity 0.3s ease';
                row.style.opacity = '0';
                setTimeout(() => row.remove(), 300);
            }
            
            showToast(`Quote ${quoteIdDisplay} archived successfully`);
            console.log(`✅ Quote ID ${id} soft deleted`);
        } else {
            throw new Error('Backend returned success: false');
        }
        
    } catch (e) {
        console.error(`❌ Failed to delete Quote ID ${id}:`, e);
        showError(`Failed to archive quote: ${e.message}`);
    }
};

window.loadQuoteFromHistory = async (id) => {
    try {
        // Fetch all history
        const historyData = await api.fetchHistory();
        const quote = historyData.find(q => q.id === id);
        
        if (!quote) {
            showError("Quote not found!");
            return;
        }
        
        console.log("📂 Loading Quote from History:", quote);
        
        // Set DB ID in state for Smart Save
        state.setCurrentDbId(id);
        
        // Reconstruct quote data object
        const quoteData = {
            filename: quote.filename,
            material: quote.material,
            fingerprint: JSON.parse(quote.fingerprint || '[]'),
            physics_price: {
                total_price: quote.anchor_price || quote.final_price,
                material_cost: 0,  // Not stored separately
                labor_cost: 0      // Not stored separately
            },
            stock: {
                x: 0, y: 0, z: 0, volume: 0  // Not stored in DB (TODO: Add if needed)
            },
            geometry: {
                volume: 0  // Not stored in DB
            },
            runtime: {
                total_time_mins: 0  // Not stored in DB
            }
        };
        
        // Populate UI
        state.setCurrentQuoteData(quoteData);
        
        // Set material
        const matSelect = document.getElementById('material-select');
        if (matSelect) matSelect.value = quote.material;
        
        // Set setup time
        const setupInput = document.getElementById('setup-time');
        if (setupInput) setupInput.value = quote.setup_time;
        
        // Set filename
        const refInput = document.getElementById('reference-name-input');
        if (refInput) refInput.value = quote.filename;
        
        // Set quote ID
        const quoteIdInput = document.getElementById('quote-id-input');
        if (quoteIdInput) quoteIdInput.value = quote.quote_id || '';
        
        // Restore pricing tags
        if (quote.tag_weights) {
            Object.entries(quote.tag_weights).forEach(([tag, weight]) => {
                state.addTag(tag, weight);
            });
        }
        
        // Restore traveler tags
        if (quote.process_routing && Array.isArray(quote.process_routing)) {
            quote.process_routing.forEach(traveler => {
                state.selectedTravelers.add(traveler);
            });
            renderTravelerBadges();
        }
        
        // Show result card
        const resultCard = document.getElementById('result-card');
        if (resultCard) resultCard.classList.add('visible');
        
        // Display price
        updateText('total-price', `$${quote.final_price.toFixed(2)}`);
        updateText('hud-price', `$${quote.final_price.toFixed(2)}`);
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        showToast(`✏️ Editing: ${quote.quote_id || `#${quote.id}`}`);
        
    } catch (e) {
        console.error("Failed to load quote:", e);
        showError("Failed to load quote from history");
    }
};

// Generic Modal Opener
function openModal(modalId, quoteId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('visible');
        // Store ID in hidden input
        const input = modal.querySelector('input[type="hidden"]');
        if (input) input.value = quoteId;
    }
}

// --- STATUS MANAGER (Unlock/Revert to Draft) ---

// Edit Status: Opens the status manager modal
window.editStatus = function(id, currentStatus) {
    document.getElementById('status-edit-quote-id').value = id;
    document.getElementById('current-status-display').textContent = currentStatus;
    
    // Show the modal
    document.getElementById('status-edit-modal').classList.add('visible');
};

// Set Status: Handle status changes
window.setStatus = async function(newStatus) {
    const id = document.getElementById('status-edit-quote-id').value;
    
    if (newStatus === 'Draft') {
        // Direct API call for Draft (Unlock)
        try {
            await api.updateQuoteStatus({
                quote_id: id,
                status: 'Draft'
                // PHASE 1: submit_to_guild removed - automatic submission violates firewall
            });
            showToast("🔓 Quote Unlocked (Reverted to Draft)");
            window.closeStatusModal();
            loadHistory();
        } catch (e) {
            showError("Failed to revert status");
            console.error("Status revert error:", e);
        }
    } 
    else if (newStatus === 'Won') {
        window.closeStatusModal();
        window.markWon(id); // Use existing logic
    } 
    else if (newStatus === 'Lost') {
        window.closeStatusModal();
        window.markLost(id); // Use existing logic
    }
};

// Close Status Modal
window.closeStatusModal = function() {
    document.getElementById('status-edit-modal').classList.remove('visible');
};

// 2. Setup Event Listeners
export function setupHistoryHandlers() {
    // PHASE 1/5 CLEANUP: sync-to-guild-btn handler removed (button deleted from UI)
    
    // Win Modal Submit
    const winForm = document.getElementById('close-loop-form');
    if (winForm) {
        winForm.onsubmit = async (e) => {
            e.preventDefault();
            const id = document.getElementById('close-loop-quote-id').value;
            const runtime = document.getElementById('actual-runtime').value;
            
            // PHASE 1 REMEDIATION: submit_to_guild removed - automatic submission violates firewall
            await api.updateQuoteStatus({
                quote_id: id,
                status: 'Won',
                actual_runtime: runtime
            });
            
            document.getElementById('close-loop-modal').classList.remove('visible');
            loadHistory(); // Refresh table
            // PHASE 1 REMEDIATION: loadGuildCredits() removed - Guild display violates firewall
            showToast("Job Won!");
        };
    }

    // Loss Modal Buttons
    const lossBtns = document.querySelectorAll('.loss-reason-btn');
    lossBtns.forEach(btn => {
        btn.onclick = () => {
            btn.classList.toggle('selected');
            const confirmBtn = document.getElementById('confirm-loss-btn');
            if (confirmBtn) confirmBtn.disabled = false;
        };
    });

    // Loss Confirm
    const lossConfirm = document.getElementById('confirm-loss-btn');
    if (lossConfirm) {
        lossConfirm.onclick = async () => {
            const id = document.getElementById('loss-analysis-quote-id').value;
            const reasons = Array.from(document.querySelectorAll('.loss-reason-btn.selected'))
                                .map(b => b.dataset.reason);
            
            // PHASE 1 REMEDIATION: submit_to_guild removed - automatic submission violates firewall
            await api.updateQuoteStatus({
                quote_id: id,
                status: 'Lost',
                loss_reason: reasons
            });

            document.getElementById('loss-analysis-modal').classList.remove('visible');
            loadHistory();
            // PHASE 1 REMEDIATION: loadGuildCredits() removed - Guild display violates firewall
            showToast("Loss Recorded.");
        };
    }

    // Close Buttons (Generic)
    document.querySelectorAll('.modal-button.secondary').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('.modal').forEach(m => m.classList.remove('visible'));
        };
    });
    
    // Status Modal: Close on outside click
    const statusModal = document.getElementById('status-edit-modal');
    if (statusModal) {
        statusModal.addEventListener('click', (e) => {
            if (e.target === statusModal) window.closeStatusModal();
        });
    }
}

// PHASE 1 REMEDIATION: loadGuildCredits() function removed
// Guild credit display in Ops violates firewall (Guild economics belong in Guild product) 

/**
 * Setup Tag Modal Handlers (Create & Manage Tags)
 */
export function setupTagModalHandlers() {
    const newTagButton = document.getElementById('new-tag-button');
    const manageTagsButton = document.getElementById('manage-tags-button');
    const tagModal = document.getElementById('tag-modal');
    const manageTagsModal = document.getElementById('manage-tags-modal');
    const tagForm = document.getElementById('tag-form');
    const cancelTagButton = document.getElementById('cancel-tag-button');
    const closeManageButton = document.getElementById('close-manage-tags-button');
    
    if (!tagModal || !manageTagsModal) return;
    
    // Open "New Tag" modal
    if (newTagButton) {
        newTagButton.addEventListener('click', () => {
            tagModal.classList.add('visible');
            tagForm.reset();
            document.getElementById('tag-modal-title').textContent = 'Create New Tag';
        });
    }
    
    // Open "Manage Tags" modal
    if (manageTagsButton) {
        manageTagsButton.addEventListener('click', async () => {
            await loadManageTagsModal();
            manageTagsModal.classList.add('visible');
        });
    }
    
    // Close modals
    if (cancelTagButton) {
        cancelTagButton.addEventListener('click', () => {
            tagModal.classList.remove('visible');
        });
    }
    
    if (closeManageButton) {
        closeManageButton.addEventListener('click', () => {
            manageTagsModal.classList.remove('visible');
        });
    }
    
    // Close modal on backdrop click
    tagModal.addEventListener('click', (e) => {
        if (e.target === tagModal) {
            tagModal.classList.remove('visible');
        }
    });
    
    manageTagsModal.addEventListener('click', (e) => {
        if (e.target === manageTagsModal) {
            manageTagsModal.classList.remove('visible');
        }
    });
    
    // Handle tag form submission
    if (tagForm) {
        tagForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const name = document.getElementById('tag-name').value.trim();
            const category = document.getElementById('tag-category').value;
            const impactType = document.getElementById('tag-effect').value;
            const impactValue = parseFloat(document.getElementById('tag-value').value) || 0;
            
            if (!name) {
                showError('Tag name is required');
                return;
            }
            
            try {
                const response = await fetch('/tags/new', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name,
                        category,
                        impact_type: impactType,
                        impact_value: impactValue
                    })
                });
                
                if (response.ok) {
                    tagModal.classList.remove('visible');
                    console.log('✅ Tag created successfully!');
                    tagForm.reset();
                    
                    // CRITICAL: Refresh tag list so new tag appears in variance sliders
                    const apiModule = await import('./api.js');
                    await apiModule.fetchTags();
                    console.log('✅ Tag list refreshed');
                } else {
                    const error = await response.json();
                    showError(error.error || 'Failed to create tag');
                }
            } catch (err) {
                showError('Network error: ' + err.message);
            }
        });
    }
}

/**
 * Load and display tags in the manage modal
 */
async function loadManageTagsModal() {
    try {
        const response = await fetch('/tags');
        const data = await response.json();
        const tagsList = document.getElementById('manage-tags-list');
        
        if (!tagsList) return;
        
        // Protected tags (Universal 9)
        const protectedTags = [
            'Rush Job', 'Expedite', 'Risk: Scrap High', 'Friends / Family',
            'Tight Tol', 'Complex Fixture', 'Heavy Deburr', 'Proto', 'Cust. Material'
        ];
        
        if (data.tags && data.tags.length > 0) {
            tagsList.innerHTML = data.tags.map(tag => {
                const isProtected = protectedTags.includes(tag.name);
                const impactText = tag.impact_type !== 'none' 
                    ? `${tag.impact_type}: ${tag.impact_value}` 
                    : 'No auto-impact';
                
                return `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; margin-bottom: 8px; background-color: #1a1a1a; border-radius: 4px; border-left: 3px solid ${isProtected ? '#00ff00' : '#ffaa00'};">
                        <div>
                            <strong style="color: #ffffff;">${tag.name}</strong>
                            <div style="color: #aaaaaa; font-size: 0.85em; margin-top: 4px;">
                                Category: ${tag.category || 'General'} | ${impactText}
                            </div>
                        </div>
                        ${isProtected 
                            ? '<span style="color: #00ff00; font-size: 0.85em;">🔒 Protected</span>'
                            : `<button onclick="deleteTag(${tag.id}, '${tag.name}')" class="modal-button secondary" style="padding: 6px 12px; font-size: 0.9em;">Delete</button>`
                        }
                    </div>
                `;
            }).join('');
        } else {
            tagsList.innerHTML = '<p style="color: #aaaaaa; text-align: center;">No tags found.</p>';
        }
    } catch (err) {
        console.error('Failed to load tags:', err);
    }
}

/**
 * Delete a custom tag (exposed globally for inline onclick)
 */
window.deleteTag = async function(tagId, tagName) {
    if (!confirm(`Delete tag "${tagName}"? This cannot be undone.`)) return;
    
    try {
        const response = await fetch(`/tags/${tagId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            console.log('✅ Tag deleted successfully!');
            
            // CRITICAL: Refresh tag list so deleted tag is removed from variance sliders
            const apiModule = await import('./api.js');
            await apiModule.fetchTags();
            
            loadManageTagsModal(); // Refresh modal list
        } else {
            const error = await response.json();
            showError(error.error || 'Failed to delete tag');
        }
    } catch (err) {
        showError('Network error: ' + err.message);
    }
};

// --- QUOTE ID VALIDATION ---

export function setupQuoteIdValidation() {
    const quoteIdInput = document.getElementById('quote-id-input');
    const saveButton = document.getElementById('save-button');
    
    if (!quoteIdInput) return;
    
    // Create warning message element (initially hidden)
    let warningDiv = document.getElementById('quote-id-warning');
    if (!warningDiv) {
        warningDiv = document.createElement('div');
        warningDiv.id = 'quote-id-warning';
        warningDiv.style.cssText = `
            display: none;
            margin-top: 8px;
            padding: 8px 12px;
            background-color: #4a1a1a;
            border: 1px solid #ff6666;
            border-radius: 4px;
            color: #ff6666;
            font-size: 0.9em;
            font-weight: bold;
        `;
        warningDiv.innerHTML = '⚠️ ID already exists. Change to avoid overwriting an existing quote.';
        quoteIdInput.parentNode.insertBefore(warningDiv, quoteIdInput.nextSibling);
    }
    
    // Validation function
    async function validateQuoteId() {
        const quoteId = quoteIdInput.value.trim();
        
        // Empty is OK (will auto-generate)
        if (quoteId === '') {
            quoteIdInput.style.borderColor = '#444444';
            warningDiv.style.display = 'none';
            if (saveButton) saveButton.disabled = false;
            return;
        }
        
        // Check if ID exists
        const api = await import('./api.js');
        const result = await api.checkQuoteId(quoteId);
        
        if (result.exists) {
            // ID exists - show warning
            quoteIdInput.style.borderColor = '#ff6666';
            quoteIdInput.style.boxShadow = '0 0 4px rgba(255, 102, 102, 0.5)';
            warningDiv.style.display = 'block';
            if (saveButton) saveButton.disabled = true;
        } else {
            // ID available - show success
            quoteIdInput.style.borderColor = '#66ff66';
            quoteIdInput.style.boxShadow = '0 0 4px rgba(102, 255, 102, 0.3)';
            warningDiv.style.display = 'none';
            if (saveButton) saveButton.disabled = false;
        }
    }
    
    // Attach blur event (fires when user clicks away or tabs out)
    quoteIdInput.addEventListener('blur', validateQuoteId);
    
    // Also validate on input (debounced for better UX)
    let inputTimeout;
    quoteIdInput.addEventListener('input', () => {
        clearTimeout(inputTimeout);
        inputTimeout = setTimeout(validateQuoteId, 500);
    });
}

// --- MARKET INTELLIGENCE HELP MODAL ---

export function setupMarketHelpModal() {
    const helpBtn = document.getElementById('market-help-btn');
    const modal = document.getElementById('market-help-modal');
    const closeBtn = document.getElementById('close-market-help');
    
    if (helpBtn && modal && closeBtn) {
        // Open modal when help button clicked
        helpBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent event bubbling
            modal.style.display = 'flex';
        });
        
        // Close modal when X button clicked
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        // Close modal when clicking outside content area
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
        
        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.style.display === 'flex') {
                modal.style.display = 'none';
            }
        });
    }
}

// --- TRAVELER TAGS LOGIC ---

export function setupTravelerHandlers() {
    renderTravelerBadges();
}

export function renderTravelerBadges() {
    const container = document.getElementById('traveler-badges');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Hardcoded list from Master Memory (Theme 5)
    const travelers = [
        "3-Axis Mill", "5-Axis Mill", "Lathe", "Swiss", "Wire EDM",
        "Surface Grind", "Anodize (Type II)", "Anodize (Hardcoat)",
        "Heat Treat", "Powder Coat", "Black Oxide", "Chromate/Alodine",
        "General Outside Process", "Assembly"
    ];
    
    travelers.forEach(name => {
        const badge = document.createElement('div');
        badge.className = `traveler-badge ${state.selectedTravelers.has(name) ? 'active' : ''}`;
        badge.textContent = name;
        badge.onclick = () => {
            state.toggleTraveler(name);
            renderTravelerBadges(); // Re-render to show active state
        };
        container.appendChild(badge);
    });
}

/**
 * Clear all traveler tags and re-render UI
 */
export function clearAndResetTravelerTags() {
    state.clearAllTravelers();
    renderTravelerBadges();
    console.log('✨ Traveler tags cleared and UI reset');
} 

export function setupStickyHud() {
    const hud = document.getElementById('sticky-hud');
    const totalPriceEl = document.getElementById('total-price');

    if (!hud || !totalPriceEl) return;

    // Logic: Show HUD when 'total-price' element scrolls out of view
    window.addEventListener('scroll', () => {
        const rect = totalPriceEl.getBoundingClientRect();
        // If bottom of price element is above top of viewport, show HUD
        if (rect.bottom < 0) {
            hud.classList.add('visible');
            document.body.classList.add('hud-visible'); // Notify sidebar to adjust height
        } else {
            hud.classList.remove('visible');
            document.body.classList.remove('hud-visible'); // Sidebar returns to full height
        }
    });
}
