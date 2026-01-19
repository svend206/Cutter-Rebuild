/**
 * variance.js - Glass Box Variance Attribution Module (Phase 4)
 * Handles distributive sliders for price variance explanation
 */

import * as state from './state.js';

// Active pricing tags (will be populated from backend)
let availableTags = [];

// Price Lock: Track if user has manually overridden the price
let userPriceLocked = false;

/**
 * Initialize variance tracking system
 * @param {Array} tags - Array of active pricing tags from backend
 */
export function initializeVariance(tags) {
    availableTags = tags || [];
    console.log('[VARIANCE] Initialized with tags:', availableTags);
}

/**
 * Unlock the price (allow system to update it)
 * Call this when material changes or user returns to landing
 */
export function unlockPrice() {
    userPriceLocked = false;
    console.log('[VARIANCE] Price unlocked (system can update)');
    
    // Hide reset button when price is unlocked
    const resetBtn = document.getElementById('reset-price-btn');
    if (resetBtn) resetBtn.style.display = 'none';
}

/**
 * Initialize variance UI interactions (collapsible sections, reset button)
 */
export function initVarianceUI() {
    // Collapsible variance section
    const varianceHeader = document.getElementById('variance-header');
    const varianceDetails = document.getElementById('variance-details');
    
    if (varianceHeader && varianceDetails) {
        varianceHeader.addEventListener('click', () => {
            varianceDetails.classList.toggle('hidden');
        });
    }
    
    // Reset price button
    const resetBtn = document.getElementById('reset-price-btn');
    const finalPriceInput = document.getElementById('final-price-input');
    
    if (resetBtn && finalPriceInput) {
        resetBtn.addEventListener('click', () => {
            const systemAnchor = parseFloat(finalPriceInput.dataset.systemAnchor) || 0;
            finalPriceInput.value = systemAnchor.toFixed(2);
            
            // Unlock price and hide variance
            unlockPrice();
            
            // Clear all sliders
            const sliders = document.querySelectorAll('.variance-slider');
            sliders.forEach(slider => {
                slider.value = 0;
                const valueSpan = slider.parentElement.querySelector('.slider-value');
                if (valueSpan) valueSpan.textContent = '0%';
            });
            
            // Hide variance section
            const varianceSection = document.getElementById('variance-section');
            if (varianceSection) varianceSection.style.display = 'none';
            
            // Update displays
            const quantity = getQuantity();
            updatePriceDisplays(systemAnchor, quantity);
            updateTotal();
            
            console.log('[VARIANCE] Price reset to anchor:', systemAnchor);
        });
    }
}

/**
 * Show or hide the Price Stack based on result data
 * @param {Object} data - Quote data from backend
 */
export function updateGlassBox(data) {
    if (!data || !data.physics_price) {
        hidePriceStack();
        return;
    }
    
    const priceStack = document.getElementById('price-stack');
    const systemAnchor = document.getElementById('system-anchor');
    const finalPriceInput = document.getElementById('final-price-input');
    const materialCost = document.getElementById('material-cost');
    const laborCost = document.getElementById('labor-cost');
    const setupCost = document.getElementById('setup-cost');
    
    if (!priceStack || !systemAnchor || !finalPriceInput) return;
    
    // Calculate base price (before tags)
    const priceData = data.physics_price || data.price || {};
    const basePriceTotal = priceData.total_price || 0.0;
    const materialCostValue = priceData.material_cost || 0.0;
    const laborCostValue = priceData.labor_cost || 0.0;
    
    // Get current quantity and setup time for setup cost calculation
    const quantityInput = document.getElementById('quantity-input');
    const setupTimeInput = document.getElementById('setup-time');
    const shopRateInput = document.getElementById('shop-rate');
    const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;
    const setupTime = setupTimeInput ? parseFloat(setupTimeInput.value) || 0 : 0;
    const shopRate = shopRateInput ? parseFloat(shopRateInput.value) || 75 : 75;
    
    // Calculate setup cost (amortized per unit)
    const setupCostValue = (setupTime / 60) * shopRate / quantity;
    
    // CRITICAL: Convert to per-unit price
    const basePricePerUnit = basePriceTotal / quantity;
    const materialCostPerUnit = materialCostValue / quantity;
    const laborCostPerUnit = laborCostValue / quantity;
    
    // Show Price Stack
    priceStack.style.display = 'block';
    
    // Set System Anchor and cost breakdown (per-unit prices)
    systemAnchor.textContent = `$${basePricePerUnit.toFixed(2)}`;
    if (materialCost) materialCost.textContent = `$${materialCostPerUnit.toFixed(2)}`;
    if (laborCost) laborCost.textContent = `$${laborCostPerUnit.toFixed(2)}`;
    if (setupCost) setupCost.textContent = `$${setupCostValue.toFixed(2)}`;
    
    // CRITICAL: Only update user's price if they haven't manually locked it
    // (User can still adjust quantity/complexity without losing their manual override)
    if (!userPriceLocked) {
        finalPriceInput.value = basePricePerUnit.toFixed(2);
        updatePriceDisplays(basePricePerUnit, quantity);
        console.log(`[VARIANCE] Price updated to anchor: $${basePricePerUnit.toFixed(2)}/unit (${quantity} units)`);
    } else {
        console.log('[VARIANCE] Price locked by user, preserving manual override');
        // Trigger variance display since user's price likely differs from new anchor
        handlePriceChange();
    }
    
    // Store system anchor PER-UNIT for later use
    finalPriceInput.dataset.systemAnchor = basePricePerUnit;
    
    // Check if user has set any variance attribution (non-zero slider values)
    const hasVarianceAttribution = checkIfVarianceSet();
    
    // Hide variance UI ONLY if: price not locked AND no variance has been set
    // This prevents clearing variance sliders when user adjusts complexity/removal rate
    const varianceSection = document.getElementById('variance-section');
    if (!userPriceLocked && !hasVarianceAttribution) {
        if (varianceSection) varianceSection.style.display = 'none';
    } else if (hasVarianceAttribution) {
        // If variance was set, keep it visible and update for new anchor
        console.log('[VARIANCE] Preserving variance attribution across recalculation');
        updateUnexplainedVariance();
    }
}

/**
 * Check if any variance sliders have been set to non-zero values
 */
function checkIfVarianceSet() {
    const sliders = document.querySelectorAll('.variance-slider');
    if (sliders.length === 0) return false;
    
    for (const slider of sliders) {
        if (parseFloat(slider.value) > 0) {
            return true;
        }
    }
    return false;
}

/**
 * Hide the Price Stack
 */
function hidePriceStack() {
    const priceStack = document.getElementById('price-stack');
    if (priceStack) {
        priceStack.style.display = 'none';
    }
}

/**
 * Handle changes to the final price input (Behavior B: Price-Driven)
 * Shows variance section and calculates unexplained variance
 * Formula: Unexplained = Final - (Anchor + Sum_of_Sliders)
 */
export function handlePriceChange() {
    const finalPriceInput = document.getElementById('final-price-input');
    const systemAnchorPerUnit = parseFloat(finalPriceInput.dataset.systemAnchor) || 0;
    const userPricePerUnit = parseFloat(finalPriceInput.value) || 0;
    
    // Get current quantity
    const quantityInput = document.getElementById('quantity-input');
    const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;
    
    // CRITICAL: Lock the price when user manually edits it
    // (Prevents system from overwriting it during quantity/complexity changes)
    userPriceLocked = true;
    console.log(`[VARIANCE] Price locked by user at $${userPricePerUnit.toFixed(2)}/unit (${quantity} units = $${(userPricePerUnit * quantity).toFixed(2)} total)`);
    
    // Show reset button when price is manually edited
    const resetBtn = document.getElementById('reset-price-btn');
    if (resetBtn) resetBtn.style.display = 'block';
    
    // CRITICAL: Update HUD and Total Price Display immediately
    updatePriceDisplays(userPricePerUnit, quantity);
    
    // Calculate per-unit difference
    const deltaPerUnit = userPricePerUnit - systemAnchorPerUnit;
    const deltaPercent = systemAnchorPerUnit > 0 ? (deltaPerUnit / systemAnchorPerUnit * 100) : 0;
    
    const varianceSection = document.getElementById('variance-section');
    
    // Show variance section if difference is significant (> $0.50/unit or > 1%)
    if (Math.abs(deltaPerUnit) > 0.5 || Math.abs(deltaPercent) > 1) {
        varianceSection.style.display = 'block';
        
        // Update variance total display
        const varianceTotalDisplay = document.getElementById('variance-total-display');
        const varianceText = deltaPercent >= 0 ? '+' : '';
        varianceTotalDisplay.textContent = `${varianceText}${deltaPercent.toFixed(1)}%`;
        varianceTotalDisplay.style.color = deltaPerUnit > 0 ? '#ffaa00' : '#ff0000';
        
        // Generate sliders if they don't exist
        generateSliders();
        
        // Calculate unexplained variance
        updateUnexplainedVariance();
    } else {
        varianceSection.style.display = 'none';
    }
}

/**
 * Update price displays (HUD, Total, Per-Unit)
 */
function updatePriceDisplays(pricePerUnit, quantity) {
    const totalPrice = pricePerUnit * quantity;
    const hudPriceText = quantity > 1 
        ? `$${totalPrice.toFixed(2)} ($${pricePerUnit.toFixed(2)}/ea)`
        : `$${totalPrice.toFixed(2)}`;
    
    const hudElement = document.getElementById('hud-price');
    const totalPriceElement = document.getElementById('total-price');
    const quantityDisplay = document.getElementById('quantity-display');
    const perUnitDisplay = document.getElementById('per-unit-display');
    
    if (hudElement) hudElement.textContent = hudPriceText;
    if (totalPriceElement) totalPriceElement.textContent = `$${totalPrice.toFixed(2)}`;
    if (quantityDisplay) quantityDisplay.textContent = quantity.toString();
    if (perUnitDisplay) perUnitDisplay.textContent = pricePerUnit.toFixed(2);
}

/**
 * Calculate and display unexplained variance
 * Formula: Unexplained = Final - (Anchor + Explained_Variance)
 */
function updateUnexplainedVariance() {
    const finalPriceInput = document.getElementById('final-price-input');
    const systemAnchorPerUnit = parseFloat(finalPriceInput.dataset.systemAnchor) || 0;
    const userPricePerUnit = parseFloat(finalPriceInput.value) || 0;
    
    // Get sum of explained variance from sliders
    const explainedVariancePercent = getSumOfSliders();
    const explainedVarianceDollars = (explainedVariancePercent / 100) * (userPricePerUnit - systemAnchorPerUnit);
    
    // Calculate unexplained variance
    const totalDelta = userPricePerUnit - systemAnchorPerUnit;
    const unexplainedVarianceDollars = totalDelta - explainedVarianceDollars;
    const unexplainedVariancePercent = systemAnchorPerUnit > 0 
        ? (unexplainedVarianceDollars / systemAnchorPerUnit) * 100 
        : 0;
    
    // Update display
    const unexplainedDisplay = document.getElementById('unexplained-variance');
    const unexplainedRow = document.getElementById('unexplained-variance-row');
    
    if (unexplainedDisplay) {
        const sign = unexplainedVarianceDollars >= 0 ? '+' : '';
        unexplainedDisplay.textContent = `${sign}$${unexplainedVarianceDollars.toFixed(2)} (${sign}${unexplainedVariancePercent.toFixed(1)}%)`;
        
        // Visual feedback: Amber glow if > 1% or > $2.00 (per documentation)
        const isSignificant = Math.abs(unexplainedVariancePercent) > 1 || Math.abs(unexplainedVarianceDollars) > 2.00;
        
        if (unexplainedRow) {
            if (isSignificant) {
                // Amber: Prompt user to explain
                unexplainedDisplay.style.color = '#ffaa00';
                unexplainedRow.style.borderLeftColor = '#ffaa00';
                unexplainedRow.style.backgroundColor = '#3a2a1a'; // Subtle amber glow
                unexplainedRow.style.borderLeftWidth = '6px'; // Emphasize
            } else {
                // Green: Within noise floor / psychological buffer
                unexplainedDisplay.style.color = '#00ff00';
                unexplainedRow.style.borderLeftColor = '#00ff00';
                unexplainedRow.style.backgroundColor = '#1a1a1a';
                unexplainedRow.style.borderLeftWidth = '4px';
            }
        }
    }
    
    console.log(`[VARIANCE] Unexplained: $${unexplainedVarianceDollars.toFixed(2)} (Total Delta: $${totalDelta.toFixed(2)}, Explained: $${explainedVarianceDollars.toFixed(2)})`);
}

/**
 * Get sum of all slider values (0-100)
 */
function getSumOfSliders() {
    const sliders = document.querySelectorAll('.variance-slider');
    let total = 0;
    sliders.forEach(slider => {
        total += parseFloat(slider.value) || 0;
    });
    return total;
}

/**
 * Get current quantity from input
 */
function getQuantity() {
    const quantityInput = document.getElementById('quantity-input');
    return quantityInput ? parseInt(quantityInput.value) || 1 : 1;
}

/**
 * Generate variance attribution sliders for active tags
 * CRITICAL: Preserve existing slider values across regeneration (for recalculation persistence)
 * EXPORTED: Used by pattern matching to auto-create sliders when tags are suggested
 */
export function generateSliders() {
    const sliderContainer = document.getElementById('slider-container');
    if (!sliderContainer) return;
    
    // PRESERVE EXISTING SLIDER VALUES before clearing
    const existingValues = {};
    const existingSliders = sliderContainer.querySelectorAll('.variance-slider');
    existingSliders.forEach(slider => {
        const tag = slider.dataset.tag;
        const value = parseFloat(slider.value) || 0;
        if (value > 0) {
            existingValues[tag] = value;
        }
    });
    
    // Clear existing sliders
    sliderContainer.innerHTML = '';
    
    // Use state.activeMarkups to get available tags
    const tags = Object.keys(state.activeMarkups);
    
    if (tags.length === 0) {
        sliderContainer.innerHTML = '<p style="color: #aaaaaa; font-style: italic;">No pricing tags available. Please configure tags in settings.</p>';
        return;
    }
    
    // Generate a slider for each tag (compact, grid-friendly)
    tags.forEach(tag => {
        // RESTORE previous value if it existed
        const savedValue = existingValues[tag] || 0;
        
        const sliderRow = document.createElement('div');
        sliderRow.className = 'slider-row';
        sliderRow.style.cssText = 'padding: 8px; background-color: #2a2a2a; border-radius: 4px;';
        
        sliderRow.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <label style="color: #ffffff; font-weight: bold; font-size: 0.9em;">${tag}</label>
                <span class="slider-value" style="color: #00aaff; font-weight: bold; min-width: 45px; text-align: right; font-size: 0.95em;">${savedValue}%</span>
            </div>
            <input type="range" 
                   class="variance-slider" 
                   data-tag="${tag}" 
                   min="0" 
                   max="100" 
                   value="${savedValue}" 
                   step="1"
                   style="width: 100%; height: 6px; background: linear-gradient(to right, #444444, #00aaff); border-radius: 3px; outline: none; cursor: pointer;">
        `;
        
        sliderContainer.appendChild(sliderRow);
    });
    
    if (Object.keys(existingValues).length > 0) {
        console.log('[VARIANCE] Restored slider values:', existingValues);
    }
    
    // Attach event listeners
    setupSliderListeners();
    
    // Update total display with restored values
    updateTotal();
    
    // Initialize with equal distribution if desired
    // autoDistribute();
}

/**
 * Setup event listeners for variance sliders
 */
function setupSliderListeners() {
    const sliders = document.querySelectorAll('.variance-slider');
    
    sliders.forEach(slider => {
        slider.addEventListener('input', (e) => {
            // Update display value
            const valueSpan = e.target.parentElement.querySelector('.slider-value');
            valueSpan.textContent = `${e.target.value}%`;
            
            // Normalize all sliders to sum to 100%
            normalizeSliders(e.target);
            
            // Update total display
            updateTotal();
            
            // BEHAVIOR A: Slider-Driven Price Update
            // When sliders change, recalculate the final price
            updateFinalPriceFromSliders();
            
            // Recalculate unexplained variance
            updateUnexplainedVariance();
        });
    });
}

/**
 * BEHAVIOR A: Update final price based on slider values (Slider-Driven)
 * Formula: Final = Anchor + (Sum_of_Sliders / 100) * Variance_Amount
 * Where Variance_Amount is determined by the sliders
 */
function updateFinalPriceFromSliders() {
    const finalPriceInput = document.getElementById('final-price-input');
    const systemAnchorPerUnit = parseFloat(finalPriceInput.dataset.systemAnchor) || 0;
    
    // Get current sum of sliders (0-100)
    const sliderSum = getSumOfSliders();
    
    // If sliders sum to 0, price stays at anchor
    if (sliderSum === 0) {
        finalPriceInput.value = systemAnchorPerUnit.toFixed(2);
        updatePriceDisplays(systemAnchorPerUnit, getQuantity());
        return;
    }
    
    // Calculate the "explained" variance amount
    // This is tricky: we need to preserve the user's total delta intent
    // The sliders represent ATTRIBUTION, not MAGNITUDE
    // So we keep the current delta and just update unexplained variance
    // (Don't auto-update price from sliders - let user drive price)
    
    // For now, sliders only affect ATTRIBUTION, not the final price
    // The user's manually entered price is the source of truth
    // Sliders just explain WHERE the variance comes from
    
    console.log('[VARIANCE] Sliders updated. Unexplained variance recalculated.');
}

/**
 * Normalize sliders so they always sum to 100%
 * When one slider is adjusted, others are proportionally reduced
 * @param {HTMLElement} changedSlider - The slider that was just changed
 */
function normalizeSliders(changedSlider) {
    const sliders = Array.from(document.querySelectorAll('.variance-slider'));
    const changedValue = parseFloat(changedSlider.value);
    
    // Get all other sliders
    const otherSliders = sliders.filter(s => s !== changedSlider);
    
    // Calculate sum of other sliders
    let otherSum = 0;
    otherSliders.forEach(s => {
        otherSum += parseFloat(s.value);
    });
    
    // Calculate remaining percentage
    const remaining = 100 - changedValue;
    
    // If remaining is negative or other sum is zero, reset others to zero
    if (remaining <= 0 || otherSum === 0) {
        otherSliders.forEach(s => {
            s.value = 0;
            const valueSpan = s.parentElement.querySelector('.slider-value');
            if (valueSpan) valueSpan.textContent = '0%';
        });
        return;
    }
    
    // Proportionally adjust other sliders
    otherSliders.forEach(s => {
        const currentValue = parseFloat(s.value);
        const proportion = currentValue / otherSum;
        const newValue = Math.round(proportion * remaining);
        s.value = newValue;
        
        const valueSpan = s.parentElement.querySelector('.slider-value');
        if (valueSpan) valueSpan.textContent = `${newValue}%`;
    });
}

/**
 * Auto-distribute variance equally among all tags
 */
function autoDistribute() {
    const sliders = document.querySelectorAll('.variance-slider');
    if (sliders.length === 0) return;
    
    const equalValue = Math.floor(100 / sliders.length);
    const remainder = 100 - (equalValue * sliders.length);
    
    sliders.forEach((slider, index) => {
        // Give remainder to first slider
        const value = index === 0 ? equalValue + remainder : equalValue;
        slider.value = value;
        
        const valueSpan = slider.parentElement.querySelector('.slider-value');
        if (valueSpan) valueSpan.textContent = `${value}%`;
    });
    
    updateTotal();
}

/**
 * Update the total percentage display
 */
function updateTotal() {
    const sliders = document.querySelectorAll('.variance-slider');
    const totalDisplay = document.getElementById('slider-total');
    const warningDisplay = document.getElementById('slider-warning');
    
    if (!totalDisplay) return 0;
    
    let total = 0;
    sliders.forEach(slider => {
        total += parseFloat(slider.value);
    });
    
    totalDisplay.textContent = `${total}%`;
    
    // Color code the total
    if (total === 100) {
        totalDisplay.style.color = '#00ff00'; // Green - valid
        if (warningDisplay) warningDisplay.style.display = 'none';
    } else if (total > 100) {
        totalDisplay.style.color = '#ff0000'; // Red - over
        if (warningDisplay) warningDisplay.style.display = 'block';
    } else {
        totalDisplay.style.color = '#ffaa00'; // Orange - under
        if (warningDisplay) warningDisplay.style.display = 'block';
    }
    
    return total;
}

/**
 * Get current variance attribution data
 * @returns {Object} Variance attribution object with tag weights
 */
export function getVarianceAttribution() {
    const sliders = document.querySelectorAll('.variance-slider');
    const attribution = {};
    
    sliders.forEach(slider => {
        const tag = slider.dataset.tag;
        const value = parseFloat(slider.value) / 100; // Convert to 0-1 range
        if (value > 0) {
            attribution[tag] = value;
        }
    });
    
    return attribution;
}

/**
 * Validate that sliders sum to exactly 100%
 * @returns {boolean} True if valid, false otherwise
 */
export function validateVariance() {
    const total = updateTotal();
    return total === 100;
}

/**
 * Get complete Glass Box data for saving
 * @returns {Object} Glass Box data including system anchor, final price, and variance
 */
export function getGlassBoxData() {
    const finalPriceInput = document.getElementById('final-price-input');
    const systemAnchor = parseFloat(finalPriceInput.dataset.systemAnchor) || 0;
    const finalPrice = parseFloat(finalPriceInput.value) || 0;
    const delta = finalPrice - systemAnchor;
    
    const data = {
        system_price_anchor: systemAnchor,
        final_quoted_price: finalPrice,
        variance_attribution: null
    };
    
    // Only include attribution if there's a significant variance and sliders are shown
    const varianceSliders = document.getElementById('variance-sliders');
    if (varianceSliders && varianceSliders.style.display !== 'none') {
        const attribution = getVarianceAttribution();
        if (Object.keys(attribution).length > 0) {
            data.variance_attribution = {
                tags: attribution,
                delta: delta,
                percent: systemAnchor > 0 ? (delta / systemAnchor * 100) : 0
            };
        }
    }
    
    return data;
}

