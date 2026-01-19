/**
 * outcome.js - Quote Outcome Wizard (Multi-Page Progressive Auto-Save)
 * 
 * Handles:
 * - Unclosed quotes table on landing page
 * - Multi-page wizard (Price → Lead Time → Terms → Other)
 * - Progressive auto-save after each page
 * - Back button overwrites with latest response
 * - NO_RESPONSE stays on exception list
 * 
 * Per wizard spec: Auto-saves immediately after each step, tracks original vs final values.
 */

// Wizard state
let currentQuoteId = null;
let currentQuoteIdStr = null;
let currentOutcome = null; // 'WON' | 'LOST' | 'NO_RESPONSE'
let wizardStep = 0; // 0=initial, 1=price, 2=leadtime, 3=terms, 4=other
let eventId = null; // For progressive updates

// Original values from quote (for pre-fill and change detection)
let originalPrice = null;
let originalLeadtime = null;
let originalTerms = null;

/**
 * Load and display unclosed quotes on landing page
 */
export async function loadUnclosedQuotes() {
    try {
        const response = await fetch('/api/unclosed_quotes');
        const data = await response.json();
        
        if (!data.success) {
            console.error('[Outcome] Failed to load unclosed quotes:', data.error);
            return;
        }
        
        const quotes = data.quotes || [];
        const count = quotes.length;
        
        // Update count badge (landing page)
        const countElement = document.getElementById('unclosed-count');
        if (countElement) {
            countElement.textContent = count;
        }
        
        // Show/hide section based on count
        const section = document.getElementById('unclosed-quotes-section');
        if (section) {
            section.style.display = count > 0 ? 'block' : 'none';
        }
        
        // Populate table
        const tbody = document.getElementById('unclosed-quotes-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (count === 0) {
            return;
        }
        
        quotes.forEach(quote => {
            const row = document.createElement('tr');
            row.style.cssText = 'border-bottom: 1px solid #333; cursor: pointer; transition: background-color 0.2s;';
            row.onmouseover = () => row.style.backgroundColor = '#333';
            row.onmouseout = () => row.style.backgroundColor = 'transparent';
            
            // Quote ID
            const idCell = document.createElement('td');
            idCell.style.padding = '12px';
            idCell.style.color = '#ffaa00';
            idCell.style.fontWeight = 'bold';
            idCell.textContent = quote.quote_id;
            row.appendChild(idCell);
            
            // Age (days)
            const ageCell = document.createElement('td');
            ageCell.style.padding = '12px';
            ageCell.style.color = quote.age_days > 7 ? '#ff4444' : '#ccc';
            ageCell.textContent = quote.age_days;
            row.appendChild(ageCell);
            
            // Customer
            const customerCell = document.createElement('td');
            customerCell.style.padding = '12px';
            customerCell.style.color = '#ccc';
            customerCell.textContent = quote.customer_name;
            row.appendChild(customerCell);
            
            // Price
            const priceCell = document.createElement('td');
            priceCell.style.padding = '12px';
            priceCell.style.color = '#fff';
            priceCell.style.textAlign = 'right';
            priceCell.textContent = `$${quote.final_quoted_price.toFixed(2)}`;
            row.appendChild(priceCell);
            
            // Actions
            const actionsCell = document.createElement('td');
            actionsCell.style.padding = '12px';
            actionsCell.style.textAlign = 'center';
            
            const wonBtn = document.createElement('button');
            wonBtn.textContent = 'Mark Won';
            wonBtn.style.cssText = 'padding: 6px 12px; background-color: #44ff44; border: none; color: #1a1a1a; border-radius: 4px; cursor: pointer; margin-right: 8px; font-weight: bold; font-size: 0.85em;';
            wonBtn.onclick = (e) => {
                e.stopPropagation();
                openWizard(quote.id, quote.quote_id, quote.final_quoted_price, quote.lead_time_days, quote.payment_terms_days);
            };
            
            const lostBtn = document.createElement('button');
            lostBtn.textContent = 'Mark Lost';
            lostBtn.style.cssText = 'padding: 6px 12px; background-color: #ff4444; border: none; color: #fff; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 0.85em;';
            lostBtn.onclick = (e) => {
                e.stopPropagation();
                openWizard(quote.id, quote.quote_id, quote.final_quoted_price, quote.lead_time_days, quote.payment_terms_days);
            };
            
            actionsCell.appendChild(wonBtn);
            actionsCell.appendChild(lostBtn);
            row.appendChild(actionsCell);
            
            // Row click opens wizard
            row.onclick = () => {
                openWizard(quote.id, quote.quote_id, quote.final_quoted_price, quote.lead_time_days, quote.payment_terms_days);
            };
            
            tbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('[Outcome] Error loading unclosed quotes:', error);
    }
}

/**
 * Open the wizard modal (Page 0: What happened?)
 */
export function openWizard(quoteId, quoteIdStr, price, leadtime, terms) {
    currentQuoteId = quoteId;
    currentQuoteIdStr = quoteIdStr;
    currentOutcome = null;
    wizardStep = 0;
    eventId = null;
    
    // Store original values for pre-fill and change detection
    originalPrice = price;
    originalLeadtime = leadtime || 0;
    originalTerms = terms || 30;
    
    // Populate quote info
    document.getElementById('outcome-quote-id').textContent = quoteIdStr;
    document.getElementById('outcome-quote-price').textContent = price.toFixed(2);
    document.getElementById('outcome-quote-leadtime').textContent = originalLeadtime;
    document.getElementById('outcome-quote-terms').textContent = originalTerms;
    
    // Reset wizard to Page 0
    showWizardPage(0);
    
    // Show modal
    const modal = document.getElementById('outcome-modal');
    modal.style.display = 'flex';
}

/**
 * Close wizard (X button or after completion)
 */
export function closeWizard() {
    const modal = document.getElementById('outcome-modal');
    modal.style.display = 'none';
    
    // Reset state
    currentQuoteId = null;
    currentOutcome = null;
    wizardStep = 0;
    eventId = null;
}

/**
 * Show a specific wizard page
 */
function showWizardPage(page) {
    wizardStep = page;
    
    // Hide all pages
    for (let i = 0; i <= 4; i++) {
        const pageEl = document.getElementById(`wizard-page-${i}`);
        if (pageEl) {
            pageEl.style.display = 'none';
        }
    }
    
    // Show current page
    const currentPage = document.getElementById(`wizard-page-${page}`);
    if (currentPage) {
        currentPage.style.display = 'block';
    }
    
    // Show/hide navigation
    const nav = document.getElementById('wizard-nav');
    if (page === 0) {
        nav.style.display = 'none'; // Page 0 doesn't need nav
    } else {
        nav.style.display = 'block';
        
        // Update Next button text for last page
        const nextBtn = document.getElementById('wizard-next-btn');
        if (page === 4) {
            nextBtn.textContent = 'Finish';
        } else {
            nextBtn.textContent = 'Next →';
        }
    }
    
    // Pre-fill values when showing pages 1-3
    if (page === 1) {
        document.getElementById('wizard-price-input').value = originalPrice.toFixed(2);
        // Update question based on outcome
        const question = document.getElementById('wizard-p1-question');
        if (currentOutcome === 'WON') {
            question.textContent = 'Did anything need to change in order to win this quote?';
        } else if (currentOutcome === 'LOST') {
            question.textContent = 'Did anything need to change in order to win this quote?';
        }
    } else if (page === 2) {
        document.getElementById('wizard-leadtime-input').value = originalLeadtime;
    } else if (page === 3) {
        document.getElementById('wizard-terms-input').value = originalTerms;
    }
}

/**
 * Select outcome (Page 0: Won / Lost / No Response)
 * Auto-saves immediately and either closes or shows wizard
 */
export async function selectOutcome(outcome) {
    currentOutcome = outcome;
    
    // Save outcome immediately (Step 0)
    const saved = await saveWizardStep(0, {
        outcome_type: outcome,
        original_price: originalPrice,
        original_leadtime: originalLeadtime,
        original_terms: originalTerms
    });
    
    if (!saved) {
        showToast('Failed to save outcome', 'error');
        return;
    }
    
    // NO_RESPONSE: Close immediately, stays on exception list
    if (outcome === 'NO_RESPONSE') {
        showToast('No Response saved. Quote remains on exception list.', 'info');
        closeWizard();
        await loadUnclosedQuotes();
        if (window.refreshSidebarHistory) {
            window.refreshSidebarHistory();
        }
        return;
    }
    
    // WON/LOST: Show wizard (Page 1: Price)
    showWizardPage(1);
}

/**
 * Wizard navigation: Next button
 */
export async function wizardNext() {
    // Collect current page data and save
    const pageData = {};
    
    if (wizardStep === 1) {
        // Price page
        const priceInput = parseFloat(document.getElementById('wizard-price-input').value);
        if (!isNaN(priceInput)) {
            pageData.final_price = priceInput;
        }
    } else if (wizardStep === 2) {
        // Lead time page
        const leadtimeInput = parseInt(document.getElementById('wizard-leadtime-input').value);
        if (!isNaN(leadtimeInput)) {
            pageData.final_leadtime = leadtimeInput;
        }
    } else if (wizardStep === 3) {
        // Terms page
        const termsInput = parseInt(document.getElementById('wizard-terms-input').value);
        if (!isNaN(termsInput)) {
            pageData.final_terms = termsInput;
        }
    } else if (wizardStep === 4) {
        // Other notes page
        const otherInput = document.getElementById('wizard-other-input').value.trim();
        if (otherInput) {
            pageData.other_notes = otherInput;
        }
    }
    
    // Save current step (progressive update)
    const saved = await saveWizardStep(wizardStep, pageData);
    if (!saved) {
        showToast('Failed to save step', 'error');
        return;
    }
    
    // Move to next page or finish
    if (wizardStep >= 4) {
        // Finished wizard
        showToast(`Outcome saved: ${currentOutcome === 'WON' ? 'Won' : 'Lost'}`, 'success');
        closeWizard();
        await loadUnclosedQuotes();
        if (window.refreshSidebarHistory) {
            window.refreshSidebarHistory();
        }
    } else {
        showWizardPage(wizardStep + 1);
    }
}

/**
 * Wizard navigation: Back button
 */
export function wizardBack() {
    if (wizardStep > 1) {
        showWizardPage(wizardStep - 1);
    }
}

/**
 * Wizard navigation: Skip button
 */
export async function wizardSkip() {
    // Just move to next page without saving current field
    if (wizardStep >= 4) {
        // Finish wizard
        showToast(`Outcome saved: ${currentOutcome === 'WON' ? 'Won' : 'Lost'}`, 'success');
        closeWizard();
        await loadUnclosedQuotes();
        if (window.refreshSidebarHistory) {
            window.refreshSidebarHistory();
        }
    } else {
        showWizardPage(wizardStep + 1);
    }
}

/**
 * Progressive auto-save wizard step
 * Returns true if saved successfully
 */
async function saveWizardStep(step, data) {
    if (!currentQuoteId || !currentOutcome) {
        console.error('[Wizard] Missing quote ID or outcome');
        return false;
    }
    
    try {
        // Get actor user ID from localStorage (if identity system is present)
        const userId = localStorage.getItem('current_user_id');
        
        // Build payload
        const payload = {
            outcome_type: currentOutcome,
            wizard_step: step,
            ...data
        };
        
        if (userId) {
            payload.actor_user_id = parseInt(userId);
        }
        
        if (eventId) {
            payload.event_id = eventId; // For progressive updates
        }
        
        const response = await fetch(`/api/quote/${currentQuoteId}/outcome/wizard`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (result.success) {
            eventId = result.event_id; // Store for next update
            console.log(`[Wizard] Saved step ${step}, event_id: ${eventId}`);
            return true;
        } else {
            console.error('[Wizard] Failed to save step:', result.error);
            return false;
        }
        
    } catch (error) {
        console.error('[Wizard] Error saving step:', error);
        return false;
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        padding: 16px 24px;
        background-color: ${type === 'success' ? '#44ff44' : type === 'error' ? '#ff4444' : '#ffaa00'};
        color: #1a1a1a;
        border-radius: 4px;
        font-weight: bold;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Make functions available globally for onclick handlers
window.openWizard = openWizard;
window.closeWizard = closeWizard;
window.selectOutcome = selectOutcome;
window.wizardNext = wizardNext;
window.wizardBack = wizardBack;
window.wizardSkip = wizardSkip;
