/**
 * RFQ Module - Handles RFQ-First workflow
 * Phase 5: "False Anchor" Prevention
 * 
 * Purpose: Ensure all critical RFQ details are entered BEFORE anchor price calculation
 * 
 * Critical Fields (Gating Logic):
 * - Material
 * - Quantity
 * - Lead Time
 * 
 * Optional Fields (Captured for Guild Intelligence):
 * - Target Price
 * - Price Breaks
 * - Outside Processing
 * - Quality Requirements
 * - Part Marking
 */

import * as ui from './ui.js';
import * as variance from './variance.js';
import * as state from './state.js';

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

let priceBreaks = [1, 5, 25, 100]; // Default price breaks
let outsideProcessingOptions = [];

// ============================================================================
// INITIALIZATION
// ============================================================================

export function initRFQ() {
    console.log('[RFQ] Initializing RFQ module...');
    
    // Load outside processing options (Traveler Tags)
    loadOutsideProcessingOptions();
    
    // Lead Time Date Picker
    setupLeadTimePicker();
    
    // Price Breaks
    setupPriceBreaks();
    
    // RFQ Requirements (Collapsible)
    setupRFQRequirementsCollapse();
    
    // Part Marking
    setupPartMarking();
    
    // Gating Logic: Monitor critical fields
    setupGatingLogic();
    
    // Price Breaks Table Monitoring
    initPriceBreaksTableMonitoring();
    
    // Phase 5.5: Pattern Matching Triggers (Ted View)
    setupPatternMatchingTriggers();
    
    console.log('[RFQ] RFQ module initialized');
}

// ============================================================================
// LEAD TIME PICKER
// ============================================================================

function setupLeadTimePicker() {
    const leadTimeDateInput = document.getElementById('lead-time-date');
    const leadTimeDaysDisplay = document.getElementById('lead-time-days-display');
    
    if (!leadTimeDateInput) return;
    
    // Set min attribute to today's date (prevent past dates)
    const today = new Date();
    const todayString = today.toISOString().split('T')[0]; // Format: YYYY-MM-DD
    leadTimeDateInput.setAttribute('min', todayString);
    
    leadTimeDateInput.addEventListener('change', () => {
        const targetDate = new Date(leadTimeDateInput.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Reset to midnight for accurate day calculation
        
        if (targetDate >= today) {
            const diffTime = targetDate - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            leadTimeDaysDisplay.textContent = `(${diffDays} days from today)`;
            leadTimeDaysDisplay.style.color = diffDays < 7 ? '#ff6600' : '#00ff00'; // Orange if rush, green if normal
        } else {
            leadTimeDaysDisplay.textContent = '(Date in the past!)';
            leadTimeDaysDisplay.style.color = '#ff0000';
        }
        
        // Trigger gating logic check
        checkGatingLogic();
    });
}

// ============================================================================
// PRICE BREAKS
// ============================================================================

function setupPriceBreaks() {
    const checkbox = document.getElementById('price-breaks-checkbox');
    const container = document.getElementById('price-breaks-container');
    const addBtn = document.getElementById('add-price-break-btn');
    
    if (!checkbox || !container) return;
    
    // Toggle visibility
    checkbox.addEventListener('change', () => {
        container.style.display = checkbox.checked ? 'block' : 'none';
        if (checkbox.checked) {
            renderPriceBreakTags();
        }
    });
    
    // Add new price break
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            const newQty = prompt('Enter quantity for new price break:', '50');
            if (newQty && !isNaN(newQty) && parseInt(newQty) > 0) {
                priceBreaks.push(parseInt(newQty));
                priceBreaks.sort((a, b) => a - b); // Keep sorted
                renderPriceBreakTags();
            }
        });
    }
}

function renderPriceBreakTags() {
    const tagsContainer = document.getElementById('price-breaks-tags');
    if (!tagsContainer) return;
    
    tagsContainer.innerHTML = '';
    
    priceBreaks.forEach((qty, index) => {
        const tag = document.createElement('div');
        tag.style.cssText = `
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background-color: #2a2a2a;
            border: 2px solid #ffaa00;
            border-radius: 4px;
            color: #ffaa00;
            font-weight: bold;
            cursor: pointer;
        `;
        
        const qtySpan = document.createElement('span');
        qtySpan.textContent = `${qty} units`;
        
        const removeBtn = document.createElement('span');
        removeBtn.textContent = '×';
        removeBtn.style.cssText = `
            font-size: 1.3em;
            cursor: pointer;
            color: #ff6600;
        `;
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            priceBreaks.splice(index, 1);
            renderPriceBreakTags();
        });
        
        tag.appendChild(qtySpan);
        tag.appendChild(removeBtn);
        
        // Edit on click
        tag.addEventListener('click', () => {
            const newQty = prompt('Edit quantity:', qty);
            if (newQty && !isNaN(newQty) && parseInt(newQty) > 0) {
                priceBreaks[index] = parseInt(newQty);
                priceBreaks.sort((a, b) => a - b);
                renderPriceBreakTags();
            }
        });
        
        tagsContainer.appendChild(tag);
    });
}

export function getPriceBreaks() {
    const checkbox = document.getElementById('price-breaks-checkbox');
    return checkbox && checkbox.checked ? priceBreaks : null;
}

// ============================================================================
// OUTSIDE PROCESSING (TRAVELER TAGS)
// ============================================================================

async function loadOutsideProcessingOptions() {
    try {
        const response = await fetch('/api/tags');
        const data = await response.json();
        
        if (data.success && data.tags) {
            // Filter for process routing tags (Traveler Tags)
            outsideProcessingOptions = data.tags.filter(tag => 
                tag && tag.name && (
                    tag.name.includes('Anodize') || 
                    tag.name.includes('Heat Treat') || 
                    tag.name.includes('Powder Coat') || 
                    tag.name.includes('Black Oxide') || 
                    tag.name.includes('Chromate') || 
                    tag.name.includes('Outside Process') ||
                    tag.name.includes('Wire EDM') ||
                    tag.name.includes('Surface Grind')
                )
            );
            
            renderOutsideProcessingBadges();
        }
    } catch (error) {
        console.error('[RFQ] Error loading outside processing options:', error);
    }
}

function renderOutsideProcessingBadges() {
    const container = document.getElementById('outside-processing-badges');
    if (!container) return;
    
    container.innerHTML = '';
    
    outsideProcessingOptions.forEach(tag => {
        const badge = document.createElement('label');
        badge.style.cssText = `
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background-color: #2a2a2a;
            border: 2px solid #444444;
            border-radius: 4px;
            color: #cccccc;
            cursor: pointer;
            transition: all 0.2s;
        `;
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.dataset.tagId = tag.id;
        checkbox.style.cssText = 'width: 16px; height: 16px; cursor: pointer;';
        
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                badge.style.borderColor = '#ff6600';
                badge.style.color = '#ff6600';
            } else {
                badge.style.borderColor = '#444444';
                badge.style.color = '#cccccc';
            }
        });
        
        const labelText = document.createElement('span');
        labelText.textContent = tag.name;
        
        badge.appendChild(checkbox);
        badge.appendChild(labelText);
        container.appendChild(badge);
    });
}

export function getOutsideProcessing() {
    const container = document.getElementById('outside-processing-badges');
    if (!container) return [];
    
    const selected = [];
    container.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
        const label = checkbox.parentElement.querySelector('span').textContent;
        selected.push(label);
    });
    
    return selected;
}

// ============================================================================
// QUALITY REQUIREMENTS
// ============================================================================

export function getQualityRequirements() {
    return {
        cmm: document.getElementById('quality-cmm')?.checked || false,
        as9102: document.getElementById('quality-as9102')?.checked || false,
        material_certs: document.getElementById('quality-material-certs')?.checked || false,
        notes: document.getElementById('quality-notes')?.value || ''
    };
}

// ============================================================================
// PART MARKING
// ============================================================================

function setupPartMarking() {
    const typeSelect = document.getElementById('part-marking-type');
    const contentInput = document.getElementById('part-marking-content');
    
    if (!typeSelect || !contentInput) return;
    
    typeSelect.addEventListener('change', () => {
        contentInput.disabled = typeSelect.value === '';
        if (typeSelect.value === '') {
            contentInput.value = '';
        }
    });
}

export function getPartMarking() {
    const type = document.getElementById('part-marking-type')?.value || '';
    const content = document.getElementById('part-marking-content')?.value || '';
    
    return type ? { type, content } : null;
}

// ============================================================================
// RFQ REQUIREMENTS COLLAPSE
// ============================================================================

function setupRFQRequirementsCollapse() {
    const header = document.getElementById('rfq-requirements-header');
    const content = document.getElementById('rfq-requirements-content');
    const toggle = document.getElementById('rfq-requirements-toggle');
    
    if (!header || !content || !toggle) return;
    
    header.addEventListener('click', () => {
        const isHidden = content.style.display === 'none';
        content.style.display = isHidden ? 'block' : 'none';
        toggle.textContent = isHidden ? '▲' : '▼';
    });
}

// ============================================================================
// GATING LOGIC (FALSE ANCHOR PREVENTION)
// ============================================================================

function setupGatingLogic() {
    // Monitor critical fields
    const materialSelect = document.getElementById('material-select');
    const quantityInput = document.getElementById('quantity-input');
    const leadTimeDateInput = document.getElementById('lead-time-date');
    
    if (materialSelect) materialSelect.addEventListener('change', checkGatingLogic);
    if (quantityInput) quantityInput.addEventListener('input', checkGatingLogic);
    if (leadTimeDateInput) leadTimeDateInput.addEventListener('change', checkGatingLogic);
    
    // Initial check
    checkGatingLogic();
}

function checkGatingLogic() {
    const material = document.getElementById('material-select')?.value;
    const quantity = document.getElementById('quantity-input')?.value;
    const leadTime = document.getElementById('lead-time-date')?.value;
    
    const allCriticalFieldsFilled = material && quantity && parseInt(quantity) > 0 && leadTime;
    
    // Enable/disable Economics section
    const economicsSection = document.getElementById('economics-section');
    if (economicsSection) {
        if (allCriticalFieldsFilled) {
            economicsSection.classList.remove('gated');
            economicsSection.style.opacity = '1';
            economicsSection.style.pointerEvents = 'auto';
        } else {
            economicsSection.classList.add('gated');
            economicsSection.style.opacity = '0.5';
            economicsSection.style.pointerEvents = 'none';
        }
    }
    
    return allCriticalFieldsFilled;
}

export function isRFQComplete() {
    return checkGatingLogic();
}

// ============================================================================
// TED VIEW: PATTERN MATCHING
// ============================================================================

export async function fetchPatternSuggestions(genesisHash, customerId) {
    const material = document.getElementById('material-select')?.value;
    const quantity = parseInt(document.getElementById('quantity-input')?.value) || 1;
    const leadTimeDateInput = document.getElementById('lead-time-date');
    
    let leadTimeDays = null;
    if (leadTimeDateInput && leadTimeDateInput.value) {
        const targetDate = new Date(leadTimeDateInput.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const diffTime = targetDate - today;
        leadTimeDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
    
    try {
        const response = await fetch('/api/pattern_suggestions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                genesis_hash: genesisHash,
                customer_id: customerId,
                material: material,
                quantity: quantity,
                lead_time_days: leadTimeDays,
                ops_mode: state.getOpsMode()
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.has_patterns) {
            displayTedView(data.suggestions);
        } else {
            hideTedView();
        }
        
        return data;
    } catch (error) {
        console.error('[RFQ] Error fetching pattern suggestions:', error);
        hideTedView();
        return null;
    }
}

function displayTedView(suggestions) {
    const banner = document.getElementById('ted-view-banner');
    const suggestionsContainer = document.getElementById('ted-view-suggestions');
    
    if (!banner || !suggestionsContainer) return;
    
    suggestionsContainer.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const suggestionDiv = document.createElement('div');
        suggestionDiv.style.cssText = `
            padding: 12px;
            background-color: #1a1a1a;
            border-left: 3px solid ${getConfidenceColor(suggestion.confidence)};
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        `;
        
        suggestionDiv.addEventListener('mouseenter', () => {
            suggestionDiv.style.backgroundColor = '#2a2a2a';
        });
        
        suggestionDiv.addEventListener('mouseleave', () => {
            suggestionDiv.style.backgroundColor = '#1a1a1a';
        });
        
        // Tag name and confidence
        const header = document.createElement('div');
        header.style.cssText = 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;';
        
        const tagName = document.createElement('span');
        tagName.textContent = suggestion.tag;
        tagName.style.cssText = 'color: #00ff00; font-weight: bold; font-size: 1em;';
        
        const confidence = document.createElement('span');
        confidence.textContent = `${Math.round(suggestion.confidence * 100)}% confidence`;
        confidence.style.cssText = `color: ${getConfidenceColor(suggestion.confidence)}; font-size: 0.85em;`;
        
        header.appendChild(tagName);
        header.appendChild(confidence);
        
        // Reason
        const reason = document.createElement('div');
        reason.textContent = suggestion.reason;
        reason.style.cssText = 'color: #aaaaaa; font-size: 0.85em; line-height: 1.5;';
        
        // Apply button
        const applyBtn = document.createElement('button');
        applyBtn.textContent = 'Apply This Tag';
        applyBtn.style.cssText = `
            margin-top: 8px;
            padding: 6px 12px;
            background-color: #00ff00;
            color: #000000;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        `;
        
        applyBtn.addEventListener('mouseenter', () => {
            applyBtn.style.backgroundColor = '#00cc00';
        });
        
        applyBtn.addEventListener('mouseleave', () => {
            applyBtn.style.backgroundColor = '#00ff00';
        });
        
        applyBtn.addEventListener('click', () => {
            applyPatternTag(suggestion.tag);
            // Success feedback is now handled inside applyPatternTag()
        });
        
        suggestionDiv.appendChild(header);
        suggestionDiv.appendChild(reason);
        suggestionDiv.appendChild(applyBtn);
        
        suggestionsContainer.appendChild(suggestionDiv);
    });
    
    banner.style.display = 'block';
}

function hideTedView() {
    const banner = document.getElementById('ted-view-banner');
    if (banner) {
        banner.style.display = 'none';
    }
}

function getConfidenceColor(confidence) {
    if (confidence >= 0.8) return '#00ff00'; // Green (High)
    if (confidence >= 0.6) return '#ffaa00'; // Amber (Medium)
    return '#ff6600'; // Orange (Low)
}

/**
 * Apply a suggested pattern tag to the variance section
 * CONSTITUTION-COMPLIANT: Slider-Driven workflow (not price-driven)
 * 
 * Flow:
 * 1. Show variance section if hidden
 * 2. Generate sliders (creates UI elements for all active tags)
 * 3. Set the suggested tag's slider to default value (50%)
 * 4. Trigger recalculation (slider-driven price update)
 * 5. Show success feedback (green toast, not red error)
 * 
 * @param {string} tagName - The Universal 9 tag name (e.g., "Rush Job")
 */
function applyPatternTag(tagName) {
    console.log(`[RFQ] Applying pattern tag: "${tagName}"`);
    
    // STEP 1: Show variance section (if hidden)
    const varianceSection = document.getElementById('variance-section');
    if (!varianceSection) {
        console.error('[RFQ] Variance section not found in DOM');
        return;
    }
    
    if (varianceSection.style.display === 'none') {
        varianceSection.style.display = 'block';
        console.log('[RFQ] Variance section revealed');
    }
    
    // STEP 2: Generate sliders (lazy-loaded, so force creation)
    // This creates slider UI elements for all tags in state.activeMarkups
    variance.generateSliders();
    console.log('[RFQ] Sliders generated');
    
    // STEP 3: Find the slider for this specific tag
    const sliders = document.querySelectorAll('.variance-slider');
    let targetSlider = null;
    
    for (const slider of sliders) {
        if (slider.dataset.tag === tagName) {
            targetSlider = slider;
            break;
        }
    }
    
    if (!targetSlider) {
        console.warn(`[RFQ] Tag "${tagName}" not found in active tags. Is it in the Universal 9?`);
        ui.showToast(`⚠️ Could not apply "${tagName}". Tag may need to be activated in settings.`);
        return;
    }
    
    // STEP 4: Set slider to suggested value (50% of variance)
    // This triggers the slider's input event, which recalculates the final price
    targetSlider.value = 50;
    targetSlider.dispatchEvent(new Event('input', { bubbles: true }));
    
    // STEP 5: Scroll to variance section (smooth UX)
    varianceSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // STEP 6: Success feedback (GREEN toast, not RED error)
    ui.showToast(`✨ Smart Apply: Added "${tagName}" at +50%`);
    
    // Hide Ted View banner since we acted on the suggestion
    hideTedView();
    
    console.log(`[RFQ] ✅ Tag "${tagName}" applied successfully`);
}

// ============================================================================
// DATA EXTRACTION (FOR SAVE QUOTE)
// ============================================================================

export function getRFQData() {
    const leadTimeDateInput = document.getElementById('lead-time-date');
    const targetPriceInput = document.getElementById('target-price-input');
    
    let leadTimeDays = null;
    if (leadTimeDateInput && leadTimeDateInput.value) {
        const targetDate = new Date(leadTimeDateInput.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const diffTime = targetDate - today;
        leadTimeDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
    
    return {
        lead_time_date: leadTimeDateInput?.value || null,
        lead_time_days: leadTimeDays,
        target_price_per_unit: targetPriceInput?.value ? parseFloat(targetPriceInput.value) : null,
        price_breaks_json: getPriceBreaks() ? JSON.stringify(getPriceBreaks()) : null,
        outside_processing_json: JSON.stringify(getOutsideProcessing()),
        quality_requirements_json: JSON.stringify(getQualityRequirements()),
        part_marking_json: getPartMarking() ? JSON.stringify(getPartMarking()) : null
    };
}

// ============================================================================
// PRICE BREAKS TABLE
// ============================================================================

export function updatePriceBreaksTable(anchorPrice, setupCost) {
    const checkbox = document.getElementById('price-breaks-checkbox');
    const tableContainer = document.getElementById('price-breaks-table-container');
    const tableBody = document.getElementById('price-breaks-table-body');
    
    if (!checkbox || !tableContainer || !tableBody) return;
    
    if (!checkbox.checked || priceBreaks.length === 0) {
        tableContainer.style.display = 'none';
        return;
    }
    
    tableContainer.style.display = 'block';
    tableBody.innerHTML = '';
    
    // Get current per-unit price from final price input
    const finalPriceInput = document.getElementById('final-price-input');
    const basePerUnitPrice = finalPriceInput ? parseFloat(finalPriceInput.value) || anchorPrice : anchorPrice;
    
    // Calculate price for quantity 1 (baseline)
    const baselineTotal = basePerUnitPrice;
    
    priceBreaks.forEach((qty, index) => {
        // Calculate per-unit price with setup amortization
        const setupPerUnit = setupCost / qty;
        const materialLaborPerUnit = basePerUnitPrice - (setupCost / 1); // Remove single-unit setup cost
        const perUnitPrice = materialLaborPerUnit + setupPerUnit;
        const totalPrice = perUnitPrice * qty;
        
        // Calculate savings vs. buying quantity 1 individually
        const savingsPercent = qty > 1 ? ((baselineTotal * qty - totalPrice) / (baselineTotal * qty)) * 100 : 0;
        
        const row = document.createElement('tr');
        row.style.cssText = 'border-bottom: 1px solid #333333;';
        
        // Highlight current quantity
        const currentQty = parseInt(document.getElementById('quantity-input')?.value) || 1;
        if (qty === currentQty) {
            row.style.backgroundColor = '#2a2a2a';
            row.style.borderLeft = '3px solid #00ff00';
        }
        
        row.innerHTML = `
            <td style="padding: 12px 8px; color: #ffffff; font-weight: ${qty === currentQty ? 'bold' : 'normal'};">${qty} units</td>
            <td style="padding: 12px 8px; text-align: right; color: #00ff00; font-family: 'Courier New', monospace;">$${perUnitPrice.toFixed(2)}</td>
            <td style="padding: 12px 8px; text-align: right; color: #ffffff; font-family: 'Courier New', monospace;">$${totalPrice.toFixed(2)}</td>
            <td style="padding: 12px 8px; text-align: right; color: ${savingsPercent > 0 ? '#00ff00' : '#aaaaaa'}; font-size: 0.9em;">
                ${savingsPercent > 0 ? `-${savingsPercent.toFixed(1)}%` : '—'}
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Monitor price changes to update the table
export function initPriceBreaksTableMonitoring() {
    const finalPriceInput = document.getElementById('final-price-input');
    const quantityInput = document.getElementById('quantity-input');
    const checkbox = document.getElementById('price-breaks-checkbox');
    
    if (finalPriceInput) {
        finalPriceInput.addEventListener('input', () => {
            // Get anchor and setup cost from the system
            const anchorPrice = parseFloat(document.getElementById('system-anchor-price')?.textContent.replace('$', '')) || 0;
            const setupCost = parseFloat(document.getElementById('setup-cost-value')?.textContent.replace('$', '')) || 0;
            updatePriceBreaksTable(anchorPrice, setupCost);
        });
    }
    
    if (quantityInput) {
        quantityInput.addEventListener('input', () => {
            const anchorPrice = parseFloat(document.getElementById('system-anchor-price')?.textContent.replace('$', '')) || 0;
            const setupCost = parseFloat(document.getElementById('setup-cost-value')?.textContent.replace('$', '')) || 0;
            updatePriceBreaksTable(anchorPrice, setupCost);
        });
    }
    
    if (checkbox) {
        checkbox.addEventListener('change', () => {
            const anchorPrice = parseFloat(document.getElementById('system-anchor-price')?.textContent.replace('$', '')) || 0;
            const setupCost = parseFloat(document.getElementById('setup-cost-value')?.textContent.replace('$', '')) || 0;
            updatePriceBreaksTable(anchorPrice, setupCost);
        });
    }
}

// ============================================================================
// PATTERN MATCHING TRIGGERS (TED VIEW) - Phase 5.5
// ============================================================================

let patternMatchingDebounceTimer = null;

function setupPatternMatchingTriggers() {
    console.log('[RFQ] Setting up pattern matching triggers...');
    
    // Trigger pattern matching when critical fields change
    const customerInput = document.getElementById('customer-input');
    const materialSelect = document.getElementById('material-select');
    const quantityInput = document.getElementById('quantity-input');
    const leadTimeDateInput = document.getElementById('lead-time-date');
    
    // Debounced pattern matching function
    const triggerPatternMatching = () => {
        if (patternMatchingDebounceTimer) {
            clearTimeout(patternMatchingDebounceTimer);
        }
        
        patternMatchingDebounceTimer = setTimeout(() => {
            performPatternMatching();
        }, 500); // Wait 500ms after user stops typing
    };
    
    // Attach listeners
    if (customerInput) {
        customerInput.addEventListener('change', triggerPatternMatching);
    }
    
    if (materialSelect) {
        materialSelect.addEventListener('change', triggerPatternMatching);
    }
    
    if (quantityInput) {
        quantityInput.addEventListener('input', triggerPatternMatching);
    }
    
    if (leadTimeDateInput) {
        leadTimeDateInput.addEventListener('change', triggerPatternMatching);
    }
    
    console.log('[RFQ] Pattern matching triggers installed');
}

async function performPatternMatching() {
    console.log('[RFQ] Performing pattern matching...');
    
    // Get current quote data
    const customerInput = document.getElementById('customer-input');
    const customerId = customerInput?.dataset.selectedId || null;
    
    const material = document.getElementById('material-select')?.value;
    const quantity = parseInt(document.getElementById('quantity-input')?.value) || 0;
    
    const leadTimeDateInput = document.getElementById('lead-time-date');
    let leadTimeDays = null;
    if (leadTimeDateInput && leadTimeDateInput.value) {
        const targetDate = new Date(leadTimeDateInput.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const diffTime = targetDate - today;
        leadTimeDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
    
    // Get Genesis Hash (if available)
    // For File Mode: stored in state after upload
    // For Napkin Mode: need to check parametric module
    let genesisHash = null;
    
    // Try to get from state (File Mode)
    try {
        const state = await import('./state.js');
        genesisHash = state.getCurrentGenesisHash?.() || null;
    } catch (error) {
        console.log('[RFQ] Could not get genesis hash from state');
    }
    
    // Skip if no material or quantity (insufficient data)
    if (!material || quantity === 0) {
        console.log('[RFQ] Insufficient data for pattern matching (no material or quantity)');
        hideTedView();
        return;
    }
    
    // Call pattern matching API
    try {
        await fetchPatternSuggestions(genesisHash, customerId);
    } catch (error) {
        console.error('[RFQ] Pattern matching failed:', error);
        hideTedView();
    }
}

