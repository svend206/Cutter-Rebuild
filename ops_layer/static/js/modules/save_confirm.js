/**
 * save_confirm.js - Save Confirmation Modal with Duplicate Detection
 * Handles "Save to History" confirmation, duplicate detection, and overwrite/rename logic
 */

import * as state from './state.js';
import * as api from './api.js';

// Track the last saved state to detect duplicates
let lastSavedState = null;

/**
 * Show the save confirmation modal
 * @param {Object} quoteData - The current quote data to save
 * @param {Object} options - Save options (tags, travelers, etc.)
 * @returns {Promise<boolean>} - True if save was successful, false if cancelled
 */
export async function showSaveConfirmation(quoteData, options) {
    const modal = document.getElementById('save-confirm-modal');
    const messageDiv = document.getElementById('save-confirm-message');
    const quoteIdInput = document.getElementById('save-confirm-quote-id');
    const hintDiv = document.getElementById('save-confirm-quote-id-hint');
    const actionsDiv = document.getElementById('save-confirm-actions');
    
    if (!modal || !messageDiv || !quoteIdInput || !actionsDiv) {
        console.error('[SAVE] Save confirmation modal elements not found');
        return false;
    }
    
    // Get current quote ID from the main form
    const currentQuoteIdInput = document.getElementById('quote-id-input');
    const currentQuoteId = currentQuoteIdInput ? currentQuoteIdInput.value.trim() : '';
    
    // Check if this is a duplicate save (same data as last save)
    const isDuplicate = checkIfDuplicate(quoteData, options);
    
    // Populate modal based on duplicate status
    if (isDuplicate) {
        messageDiv.innerHTML = `
            <div style="background-color: #3a1a1a; padding: 15px; border-radius: 4px; border-left: 4px solid #ff6600; margin-bottom: 15px;">
                <p style="margin: 0 0 10px 0; color: #ff6600; font-weight: bold;">⚠️ Duplicate Detected</p>
                <p style="margin: 0; font-size: 0.95em;">
                    This quote appears identical to the one you just saved. 
                    Would you like to <strong>overwrite</strong> the existing quote or <strong>save as a new revision</strong>?
                </p>
            </div>
            <div style="background-color: #1a1a1a; padding: 12px; border-radius: 4px; margin-bottom: 15px;">
                <p style="margin: 0; font-size: 0.9em; color: #aaaaaa;">
                    <strong style="color: #ffffff;">Last saved as:</strong> ${lastSavedState.quote_id || 'Unknown'}
                </p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #aaaaaa;">
                    <strong style="color: #ffffff;">Price:</strong> $${lastSavedState.final_price.toFixed(2)}
                </p>
            </div>
        `;
        
        quoteIdInput.value = currentQuoteId || lastSavedState.quote_id || '';
        hintDiv.textContent = 'Keep the same ID to overwrite, or change it to save as a new quote.';
        
        actionsDiv.innerHTML = `
            <button class="button secondary" id="save-cancel-btn" style="min-width: 100px;">Cancel</button>
            <button class="button" id="save-overwrite-btn" style="min-width: 120px; background-color: #ff6600;">Overwrite</button>
            <button class="button" id="save-new-btn" style="min-width: 120px;">Save as New</button>
        `;
    } else {
        // First save or data has changed
        messageDiv.innerHTML = `
            <p style="margin: 0; font-size: 0.95em;">
                Confirm the Quote ID / Reference for this quote. This will be saved to your history.
            </p>
        `;
        
        quoteIdInput.value = currentQuoteId || generateDefaultQuoteId();
        hintDiv.textContent = 'Leave blank for auto-generated format (Q-YYYYMMDD-###).';
        
        actionsDiv.innerHTML = `
            <button class="button secondary" id="save-cancel-btn" style="min-width: 100px;">Cancel</button>
            <button class="button" id="save-confirm-btn" style="min-width: 120px;">Save</button>
        `;
    }
    
    // Show modal
    modal.style.display = 'flex';
    
    // Return a promise that resolves when user makes a choice
    return new Promise((resolve) => {
        // Close button
        const closeBtn = document.getElementById('close-save-confirm');
        const cancelBtn = document.getElementById('save-cancel-btn');
        const confirmBtn = document.getElementById('save-confirm-btn');
        const overwriteBtn = document.getElementById('save-overwrite-btn');
        const newBtn = document.getElementById('save-new-btn');
        
        const cleanup = () => {
            modal.style.display = 'none';
            if (closeBtn) closeBtn.removeEventListener('click', handleClose);
            if (cancelBtn) cancelBtn.removeEventListener('click', handleClose);
            if (confirmBtn) confirmBtn.removeEventListener('click', handleConfirm);
            if (overwriteBtn) overwriteBtn.removeEventListener('click', handleOverwrite);
            if (newBtn) newBtn.removeEventListener('click', handleNew);
        };
        
        const handleClose = () => {
            cleanup();
            resolve(false);
        };
        
        const handleConfirm = async () => {
            const finalQuoteId = quoteIdInput.value.trim();
            
            // Update the main form's quote ID
            if (currentQuoteIdInput) {
                currentQuoteIdInput.value = finalQuoteId;
            }
            
            cleanup();
            
            // Perform the save
            const success = await performSave(quoteData, options);
            resolve(success);
        };
        
        const handleOverwrite = async () => {
            // Keep the same quote ID (overwrite existing)
            const finalQuoteId = quoteIdInput.value.trim();
            
            if (currentQuoteIdInput) {
                currentQuoteIdInput.value = finalQuoteId;
            }
            
            cleanup();
            
            // Perform the save (will update existing record due to same ID)
            const success = await performSave(quoteData, options);
            resolve(success);
        };
        
        const handleNew = async () => {
            // Generate a new quote ID
            const newQuoteId = generateDefaultQuoteId();
            quoteIdInput.value = newQuoteId;
            
            if (currentQuoteIdInput) {
                currentQuoteIdInput.value = newQuoteId;
            }
            
            cleanup();
            
            // Clear the DB ID to force a new INSERT
            state.setCurrentDbId(null);
            
            // Perform the save
            const success = await performSave(quoteData, options);
            resolve(success);
        };
        
        // Attach event listeners
        if (closeBtn) closeBtn.addEventListener('click', handleClose);
        if (cancelBtn) cancelBtn.addEventListener('click', handleClose);
        if (confirmBtn) confirmBtn.addEventListener('click', handleConfirm);
        if (overwriteBtn) overwriteBtn.addEventListener('click', handleOverwrite);
        if (newBtn) newBtn.addEventListener('click', handleNew);
        
        // Focus the quote ID input
        quoteIdInput.focus();
        quoteIdInput.select();
    });
}

/**
 * Check if the current quote data is identical to the last saved state
 * @param {Object} quoteData - Current quote data
 * @param {Object} options - Save options
 * @returns {boolean} - True if duplicate, false otherwise
 */
function checkIfDuplicate(quoteData, options) {
    if (!lastSavedState) {
        return false; // No previous save
    }
    
    // Get current values
    const currentPrice = parseFloat(document.getElementById('total-price')?.textContent.replace('$','').replace(/[^\d.]/g, '')) || 0;
    const currentMaterial = document.getElementById('material-select')?.value || 'Unknown';
    const currentSetupTime = parseFloat(document.getElementById('setup-time')?.value) || 60;
    const currentHandlingTime = parseFloat(document.getElementById('handling-time')?.value) || 0.5;
    
    // Compare key fields
    const priceMatch = Math.abs(currentPrice - lastSavedState.final_price) < 0.01;
    const materialMatch = currentMaterial === lastSavedState.material;
    const setupMatch = Math.abs(currentSetupTime - lastSavedState.setup_time) < 0.01;
    const handlingMatch = Math.abs(currentHandlingTime - lastSavedState.handling_time) < 0.01;
    const filenameMatch = (quoteData.filename || 'Unknown') === lastSavedState.filename;
    
    // Compare tags (pricing tags)
    const currentTagsJson = JSON.stringify(options.tagWeights || {});
    const lastTagsJson = JSON.stringify(lastSavedState.tag_weights || {});
    const tagsMatch = currentTagsJson === lastTagsJson;
    
    // Compare travelers (process routing) - FIXED: Convert Set to sorted array for comparison
    const currentTravelersArray = Array.from(options.selectedTravelers || []).sort();
    const lastTravelersArray = (lastSavedState.process_routing || []).sort();
    const currentTravelersJson = JSON.stringify(currentTravelersArray);
    const lastTravelersJson = JSON.stringify(lastTravelersArray);
    const travelersMatch = currentTravelersJson === lastTravelersJson;
    
    console.log('[DUPLICATE CHECK] Comparison:', {
        priceMatch, materialMatch, setupMatch, handlingMatch, filenameMatch, tagsMatch, travelersMatch,
        currentTravelers: currentTravelersArray,
        lastTravelers: lastTravelersArray
    });
    
    return priceMatch && materialMatch && setupMatch && handlingMatch && filenameMatch && tagsMatch && travelersMatch;
}

/**
 * Perform the actual save operation
 * @param {Object} quoteData - Quote data to save
 * @param {Object} options - Save options
 * @returns {Promise<boolean>} - True if successful, false otherwise
 */
async function performSave(quoteData, options) {
    try {
        const result = await api.saveQuote(quoteData, options);
        
        // Update last saved state
        lastSavedState = {
            quote_id: document.getElementById('quote-id-input')?.value.trim() || '',
            final_price: parseFloat(document.getElementById('total-price')?.textContent.replace('$','').replace(/[^\d.]/g, '')) || 0,
            material: document.getElementById('material-select')?.value || 'Unknown',
            setup_time: parseFloat(document.getElementById('setup-time')?.value) || 60,
            handling_time: parseFloat(document.getElementById('handling-time')?.value) || 0.5,
            filename: quoteData.filename || 'Unknown',
            tag_weights: options.tagWeights || {},
            process_routing: Array.from(options.selectedTravelers || [])
        };
        
        return true;
    } catch (error) {
        console.error('[SAVE] Save failed:', error);
        return false;
    }
}

/**
 * Generate a default quote ID
 * @returns {string} - Default quote ID in format Q-YYYYMMDD-###
 */
function generateDefaultQuoteId() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const random = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
    return `Q-${year}${month}${day}-${random}`;
}

/**
 * Reset the last saved state (e.g., when starting a new quote)
 */
export function resetLastSavedState() {
    lastSavedState = null;
    console.log('[SAVE] Last saved state cleared');
}

