/**
 * Sidebar Module (Phase 4: The Cockpit)
 * Handles sidebar toggle, state persistence, and Three.js viewer resize dispatch
 */

const STORAGE_KEY = 'sidebarState';
const TRANSITION_DURATION = 300; // Must match CSS transition (300ms)

/**
 * Initialize the sidebar functionality
 */
export function initSidebar() {
    const sidebar = document.getElementById('main-sidebar');
    const collapseToggle = document.querySelector('.collapse-toggle');
    
    if (!sidebar || !collapseToggle) {
        console.warn('[SIDEBAR] Sidebar elements not found. Skipping initialization.');
        return;
    }
    
    // Restore saved state from localStorage
    const savedState = localStorage.getItem(STORAGE_KEY);
    if (savedState === 'collapsed') {
        sidebar.classList.add('collapsed');
    }
    
    // Toggle handler
    collapseToggle.addEventListener('click', () => {
        const isCollapsed = sidebar.classList.toggle('collapsed');
        
        // Persist state
        localStorage.setItem(STORAGE_KEY, isCollapsed ? 'collapsed' : 'expanded');
        
        // CRITICAL: Dispatch resize event after transition completes
        // This forces Three.js viewer to recalculate canvas dimensions
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
            console.log('[SIDEBAR] Resize event dispatched for Three.js viewer');
        }, TRANSITION_DURATION);
    });
    
    // Navigation item click handlers
    const navItems = document.querySelectorAll('.nav-item[data-view]');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            handleNavigation(view);
            
            // Update active state
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });
    
    // Initialize quote history panel
    initQuoteHistory();
    
    console.log('[SIDEBAR] Sidebar initialized');
}

/**
 * Handle navigation between views
 * @param {string} view - The view to navigate to (home, quote, parts, customers, config)
 */
function handleNavigation(view) {
    console.log(`[SIDEBAR] Navigating to: ${view}`);
    
    switch (view) {
        case 'home':
            showDashboard();
            break;
        case 'quote':
            showLandingScreen();
            break;
        case 'parts':
            showPartsLibrary();
            break;
        case 'customers':
            showCustomers();
            break;
        case 'config':
            showConfiguration();
            break;
        default:
            console.warn(`[SIDEBAR] Unknown view: ${view}`);
    }
}

/**
 * Show the landing screen (File Mode / Napkin Mode choice)
 */
function showLandingScreen() {
    // Hide all sections and mode-specific elements
    const sectionsToHide = [
        'quote-metadata',
        'physics-section',
        'configuration-section',
        'economics-section',
        'viewer-section',
        'evidence-locker',      // Hide Evidence Locker when returning to landing
        'upload-zone',          // Hide File Mode upload zone
        'file-input',           // Hide file input
        'calculate-btn',        // Hide calculate button
        'loading',              // Hide loading indicator
        'error-message',        // Hide error message
        'result-card',          // Hide result card
        'traveler-zone',        // FIX: Hide traveler tags (shown in File/Napkin Mode)
        'tag-zone',             // FIX: Hide pricing tags (shown in File/Napkin Mode)
        'home-btn',             // FIX: Hide home button (not needed on landing)
        'shape-configurator',   // FIX: Hide Napkin Mode shape selector
        'file-mode-guide',      // FIX: Hide file mode guide
        'bob-guide'             // FIX: Hide Bob's guide
    ];
    
    sectionsToHide.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.style.display = 'none';
    });
    
    // Also hide .button-center container (doesn't have ID)
    const buttonCenter = document.querySelector('.button-center');
    if (buttonCenter) buttonCenter.style.display = 'none';
    
    // Show landing screen
    const landingScreen = document.getElementById('landing-screen');
    if (landingScreen) {
        landingScreen.style.display = 'flex';
    }
    
    // Clear any active quote data
    clearQuoteForm();
    
    console.log('[SIDEBAR] Landing screen shown');
}

/**
 * Clear the quote form (reset to initial state)
 */
function clearQuoteForm() {
    // Clear identity fields
    const customerInput = document.getElementById('customer-input');
    const contactInput = document.getElementById('contact-input');
    const referenceInput = document.getElementById('reference-name-input');
    const quoteIdInput = document.getElementById('quote-id-input');
    
    if (customerInput) {
        customerInput.value = '';
        customerInput.dataset.selectedId = '';
    }
    if (contactInput) {
        contactInput.value = '';
        contactInput.dataset.selectedId = '';
        contactInput.disabled = true;
    }
    if (referenceInput) referenceInput.value = '';
    if (quoteIdInput) quoteIdInput.value = '';
    
    // Clear RFQ fields
    const materialSelect = document.getElementById('material-select');
    const quantityInput = document.getElementById('quantity-input');
    const leadTimeInput = document.getElementById('lead-time-date');
    const targetPriceInput = document.getElementById('target-price-input');
    
    if (materialSelect) materialSelect.value = '';
    if (quantityInput) quantityInput.value = '1';
    if (leadTimeInput) leadTimeInput.value = '';
    if (targetPriceInput) targetPriceInput.value = '';
    
    // Clear price breaks
    const priceBreaksCheckbox = document.getElementById('price-breaks-checkbox');
    if (priceBreaksCheckbox) priceBreaksCheckbox.checked = false;
    
    // Clear configuration fields
    const setupTimeInput = document.getElementById('setup-time');
    const handlingTimeInput = document.getElementById('handling-time');
    const shopRateInput = document.getElementById('shop-rate');
    
    if (setupTimeInput) setupTimeInput.value = '60';
    if (handlingTimeInput) handlingTimeInput.value = '0.5';
    if (shopRateInput) shopRateInput.value = '75';
    
    // Clear final price
    const finalPriceInput = document.getElementById('final-price-input');
    if (finalPriceInput) finalPriceInput.value = '';
    
    console.log('[SIDEBAR] Quote form cleared');
}

// ============================================================================
// QUOTE HISTORY PANEL
// ============================================================================

/**
 * Initialize the quote history panel in sidebar
 */
function initQuoteHistory() {
    const historyToggle = document.getElementById('history-toggle');
    const historyList = document.getElementById('sidebar-history-list');
    const toggleIcon = document.getElementById('history-toggle-icon');
    
    if (!historyToggle || !historyList) {
        console.warn('[SIDEBAR] History panel elements not found');
        return;
    }
    
    // Toggle collapse/expand
    historyToggle.addEventListener('click', () => {
        const isHidden = historyList.style.display === 'none';
        historyList.style.display = isHidden ? 'block' : 'none';
        toggleIcon.textContent = isHidden ? '▼' : '▶';
    });
    
    // Load recent quotes
    loadRecentQuotes();
    
    console.log('[SIDEBAR] Quote history panel initialized');
}

/**
 * Load recent quotes from the API
 */
async function loadRecentQuotes() {
    const historyList = document.getElementById('sidebar-history-list');
    if (!historyList) return;
    
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        if (!data.history || data.history.length === 0) {
            historyList.innerHTML = `
                <div style="padding: 12px; text-align: center; color: #888; font-size: 0.85em;">
                    No quotes yet
                </div>
            `;
            return;
        }
        
        // Render quote items (most recent first, limit to 10)
        const recentQuotes = data.history.slice(0, 10);
        historyList.innerHTML = recentQuotes.map(quote => renderQuoteItem(quote)).join('');
        
        // Add click handlers for quote items (load quote)
        historyList.querySelectorAll('.quote-item').forEach(item => {
            item.addEventListener('click', () => {
                const quoteId = item.dataset.quoteId;
                loadQuote(quoteId);
            });
        });
        
        // Add click handlers for PDF buttons (prevent event bubbling)
        historyList.querySelectorAll('.pdf-download-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent triggering quote load
                const quoteId = btn.dataset.quoteId;
                downloadQuotePDF(quoteId);
            });
        });
        
        // Add click handlers for Traveler buttons (gated by status)
        historyList.querySelectorAll('.traveler-download-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent triggering quote load
                const quoteId = btn.dataset.quoteId;
                const isWon = btn.dataset.isWon === 'true';
                const quoteString = btn.dataset.quoteString;
                
                if (isWon) {
                    // Quote is Won - directly download traveler
                    downloadTravelerPDF(quoteId);
                } else {
                    // Quote is NOT Won - show confirmation dialog
                    handleTravelerGating(quoteId, quoteString);
                }
            });
        });
        
        // Add click handlers for Status badges (The "Deal Closer")
        historyList.querySelectorAll('.status-badge').forEach(badge => {
            badge.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent triggering quote load
                const quoteId = badge.dataset.quoteId;
                const currentStatus = badge.dataset.status;
                openStatusModal(quoteId, currentStatus);
            });
        });
        
        console.log(`[SIDEBAR] Loaded ${recentQuotes.length} recent quotes`);
        
    } catch (error) {
        console.error('[SIDEBAR] Error loading quote history:', error);
        historyList.innerHTML = `
            <div style="padding: 12px; text-align: center; color: #ff6600; font-size: 0.85em;">
                Error loading quotes
            </div>
        `;
    }
}

/**
 * Render a single quote item for the sidebar
 */
function renderQuoteItem(quote) {
    const date = new Date(quote.timestamp || quote.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    const price = parseFloat(quote.final_quoted_price || 0).toFixed(2);
    const material = quote.material || 'Unknown';
    const reference = quote.reference_name || quote.filename || quote.quote_id || 'Untitled';
    
    // Status badge styling
    const status = quote.status || 'Draft';
    let statusColor = '#888888'; // Default gray
    let statusBgColor = '#2a2a2a';
    
    if (status === 'Won') {
        statusColor = '#00ff00';
        statusBgColor = '#1a3a1a';
    } else if (status === 'Lost') {
        statusColor = '#ff4444';
        statusBgColor = '#3a1a1a';
    } else if (status === 'Sent') {
        statusColor = '#00aaff';
        statusBgColor = '#1a2a3a';
    }
    
    // Check if quote is Won (for Traveler gating)
    const isWon = status === 'Won';
    
    // Traveler button styling based on status
    const travelerBgColor = isWon ? '#00aa00' : '#555555';
    const travelerHoverColor = isWon ? '#00cc00' : '#666666';
    const travelerOpacity = isWon ? '1' : '0.5';
    const travelerCursor = isWon ? 'pointer' : 'help';
    
    return `
        <div class="quote-item" data-quote-id="${quote.id}" style="
            padding: 12px;
            margin-bottom: 8px;
            background-color: #2a2a2a;
            border-left: 3px solid #ff6600;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        " onmouseenter="this.style.backgroundColor='#333333'" onmouseleave="this.style.backgroundColor='#2a2a2a'">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="color: #ffaa00; font-weight: bold; font-size: 0.85em;">${quote.quote_id || 'Q-???'}</span>
                <span class="status-badge" data-quote-id="${quote.id}" data-status="${status}" style="
                    padding: 2px 8px;
                    background-color: ${statusBgColor};
                    color: ${statusColor};
                    border: 1px solid ${statusColor};
                    border-radius: 3px;
                    font-size: 0.7em;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.2s;
                " onmouseenter="this.style.transform='scale(1.05)'" onmouseleave="this.style.transform='scale(1)'" title="Click to update status">
                    ${status.toUpperCase()}
                </span>
            </div>
            <div style="color: #ffffff; font-size: 0.9em; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${reference}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #00ff00; font-weight: bold; font-size: 0.9em;">$${price}</span>
                <span style="color: #aaaaaa; font-size: 0.75em;">${material}</span>
            </div>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #444444; display: flex; gap: 8px;">
                <button class="pdf-download-btn" data-quote-id="${quote.id}" style="
                    padding: 4px 8px;
                    background-color: #ff6600;
                    color: #1a1a1a;
                    border: none;
                    border-radius: 3px;
                    font-size: 0.75em;
                    font-weight: bold;
                    cursor: pointer;
                    transition: background-color 0.2s;
                " onmouseenter="this.style.backgroundColor='#ff8833'" onmouseleave="this.style.backgroundColor='#ff6600'">
                    📄 PDF
                </button>
                <button class="traveler-download-btn" data-quote-id="${quote.id}" data-is-won="${isWon}" data-quote-string="${quote.quote_id || 'Q-???'}" style="
                    padding: 4px 8px;
                    background-color: ${travelerBgColor};
                    color: #ffffff;
                    border: none;
                    border-radius: 3px;
                    font-size: 0.75em;
                    font-weight: bold;
                    cursor: ${travelerCursor};
                    opacity: ${travelerOpacity};
                    transition: background-color 0.2s;
                " onmouseenter="this.style.backgroundColor='${travelerHoverColor}'" onmouseleave="this.style.backgroundColor='${travelerBgColor}'">
                    🔧 Traveler
                </button>
            </div>
        </div>
    `;
}

/**
 * Load a quote by ID and populate the form
 */
async function loadQuote(quoteId) {
    console.log(`[SIDEBAR] Loading quote: ${quoteId}`);
    
    try {
        const response = await fetch(`/api/quote/${quoteId}`);
        
        if (!response.ok) {
            console.error(`[SIDEBAR] HTTP error: ${response.status}`);
            const errorData = await response.json();
            console.error('[SIDEBAR] Error response:', errorData);
            alert(`Error loading quote: ${errorData.error || 'Unknown error'}`);
            return;
        }
        
        const data = await response.json();
        console.log('[SIDEBAR] Quote data received:', data);
        
        if (!data.success || !data.quote) {
            console.error('[SIDEBAR] Invalid response format:', data);
            alert(`Error loading quote: ${data.error || 'Invalid response format'}`);
            return;
        }
        
        const quote = data.quote;
        
        // Hide landing screen
        const landingScreen = document.getElementById('landing-screen');
        if (landingScreen) landingScreen.style.display = 'none';
        
        // Show quote-metadata section
        const quoteMetadata = document.getElementById('quote-metadata');
        if (quoteMetadata) quoteMetadata.style.display = 'block';
        
        // Show result-card (parent container for all sections)
        const resultCard = document.getElementById('result-card');
        if (resultCard) resultCard.style.display = 'block';
        
        // Show all flow sections
        const sectionsToShow = [
            'physics-section',
            'configuration-section',
            'economics-section'
        ];
        
        sectionsToShow.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'block';
        });
        
        // Hide mode-specific elements that shouldn't be visible when loading a saved quote
        const elementsToHide = [
            'upload-zone',  // File Mode upload area
            'file-input',  // File input
            'calculate-btn',  // Calculate button (we already have the calculated price)
            'evidence-locker'  // Evidence locker
        ];
        
        elementsToHide.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });
        
        // If the quote has a 3D file, show the viewer and load the model
        if (quote.filename) {
            const viewerSection = document.getElementById('viewer-section');
            if (viewerSection) viewerSection.style.display = 'block';
            
            // Load the 3D model
            console.log('[SIDEBAR] Loading 3D model:', quote.filename);
            const viewer = await import('./viewer.js');
            const modelUrl = `/uploads/${quote.filename}`;
            viewer.loadModelFromUrl(modelUrl);
        }
        
        // Populate form fields
        populateQuoteForm(quote);
        
        console.log('[SIDEBAR] Quote loaded successfully');
        
    } catch (error) {
        console.error('[SIDEBAR] Error loading quote:', error);
        alert('Error loading quote');
    }
}

/**
 * Download PDF for a quote
 * @param {number} quoteId - The quote ID
 */
function downloadQuotePDF(quoteId) {
    console.log(`[SIDEBAR] Downloading PDF for quote: ${quoteId}`);
    
    // Open PDF in new tab (browser will handle download/display based on settings)
    const pdfUrl = `/api/quote/${quoteId}/pdf`;
    window.open(pdfUrl, '_blank');
}

/**
 * Download Traveler PDF for a quote (shop floor work order)
 * @param {number} quoteId - The quote ID
 */
function downloadTravelerPDF(quoteId) {
    console.log(`[SIDEBAR] Downloading Traveler PDF for quote: ${quoteId}`);
    
    // Open Traveler PDF in new tab
    const travelerUrl = `/api/quote/${quoteId}/traveler`;
    window.open(travelerUrl, '_blank');
}

/**
 * Handle gating logic for Traveler generation (non-Won quotes)
 * @param {number} quoteId - The quote ID
 * @param {string} quoteString - The quote ID string for display (e.g., "Q-20260104-001")
 */
async function handleTravelerGating(quoteId, quoteString) {
    // Show confirmation dialog
    const confirmed = confirm(
        `Mark Quote ${quoteString} as WON to generate Traveler?\n\n` +
        `Travelers (Work Orders) should only be generated for jobs you've won.\n\n` +
        `Click OK to mark as Won and generate Traveler.`
    );
    
    if (!confirmed) {
        console.log(`[SIDEBAR] User cancelled Traveler generation for quote: ${quoteId}`);
        return;
    }
    
    // User confirmed - mark as Won
    try {
        const success = await markQuoteAsWon(quoteId);
        
        if (success) {
            // Refresh sidebar to update button styling
            loadRecentQuotes();
            
            // Small delay to let UI update, then open traveler
            setTimeout(() => {
                downloadTravelerPDF(quoteId);
            }, 300);
        } else {
            alert('Failed to mark quote as Won. Please try again.');
        }
    } catch (error) {
        console.error('[SIDEBAR] Error in Traveler gating:', error);
        alert('Error marking quote as Won. Please try again.');
    }
}

/**
 * Mark a quote as Won (update status in database)
 * @param {number} quoteId - The quote ID
 * @returns {Promise<boolean>} - True if successful
 */
async function markQuoteAsWon(quoteId) {
    console.log(`[SIDEBAR] Marking quote as Won: ${quoteId}`);
    
    try {
        const response = await fetch(`/api/quote/${quoteId}/mark_won`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.error(`[SIDEBAR] HTTP error: ${response.status}`);
            return false;
        }
        
        const data = await response.json();
        
        if (data.success) {
            console.log(`[SIDEBAR] Quote ${quoteId} marked as Won successfully`);
            return true;
        } else {
            console.error('[SIDEBAR] Server returned error:', data.error);
            return false;
        }
        
    } catch (error) {
        console.error('[SIDEBAR] Network error marking quote as Won:', error);
        return false;
    }
}

/**
 * Populate the quote form with data from a saved quote
 */
function populateQuoteForm(quote) {
    // Identity fields
    if (quote.customer_name) {
        const customerInput = document.getElementById('customer-input');
        if (customerInput) {
            customerInput.value = quote.customer_name;
            customerInput.dataset.selectedId = quote.customer_id || '';
        }
    }
    
    if (quote.contact_name) {
        const contactInput = document.getElementById('contact-input');
        if (contactInput) {
            contactInput.value = quote.contact_name;
            contactInput.dataset.selectedId = quote.contact_id || '';
            contactInput.disabled = false;
        }
    }
    
    // Quote metadata
    const referenceInput = document.getElementById('reference-name-input');
    const quoteIdInput = document.getElementById('quote-id-input');
    
    if (referenceInput) referenceInput.value = quote.reference_name || quote.filename || '';
    if (quoteIdInput) quoteIdInput.value = quote.quote_id || '';
    
    // RFQ fields
    const materialSelect = document.getElementById('material-select');
    const quantityInput = document.getElementById('quantity-input');
    
    if (materialSelect) materialSelect.value = quote.material || '';
    if (quantityInput) quantityInput.value = quote.quantity || 1;
    
    // Configuration fields
    const setupTimeInput = document.getElementById('setup-time');
    const shopRateInput = document.getElementById('shop-rate');
    
    if (setupTimeInput) setupTimeInput.value = quote.setup_time || 60;
    if (shopRateInput) shopRateInput.value = quote.shop_rate || 75;
    
    // Final price
    const finalPriceInput = document.getElementById('final-price-input');
    if (finalPriceInput && quote.final_quoted_price) {
        finalPriceInput.value = parseFloat(quote.final_quoted_price).toFixed(2);
    }
    
    console.log('[SIDEBAR] Form populated with quote data');
}

/**
 * Refresh the quote history list (call after saving a new quote)
 */
export function refreshQuoteHistory() {
    loadRecentQuotes();
}

/**
 * Programmatically set sidebar state
 * @param {boolean} collapsed - Whether sidebar should be collapsed
 */
export function setSidebarState(collapsed) {
    const sidebar = document.getElementById('main-sidebar');
    if (!sidebar) return;
    
    if (collapsed) {
        sidebar.classList.add('collapsed');
    } else {
        sidebar.classList.remove('collapsed');
    }
    
    localStorage.setItem(STORAGE_KEY, collapsed ? 'collapsed' : 'expanded');
    
    // Dispatch resize event
    setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
    }, TRANSITION_DURATION);
}

/**
 * Get current sidebar state
 * @returns {boolean} - True if collapsed
 */
export function isSidebarCollapsed() {
    const sidebar = document.getElementById('main-sidebar');
    return sidebar ? sidebar.classList.contains('collapsed') : false;
}

// ============================================================================
// STATUS UPDATE MODAL (THE "DEAL CLOSER")
// ============================================================================

/**
 * Open the status update modal for a quote
 * @param {number} quoteId - The quote ID
 * @param {string} currentStatus - Current status of the quote
 */
function openStatusModal(quoteId, currentStatus) {
    console.log(`[SIDEBAR] Opening status modal for quote ${quoteId} (current: ${currentStatus})`);
    
    const modal = document.getElementById('deal-closer-modal');
    if (!modal) {
        console.error('[SIDEBAR] Status modal not found in DOM');
        return;
    }
    
    // Store quote ID in modal
    modal.dataset.quoteId = quoteId;
    modal.dataset.currentStatus = currentStatus;
    
    // Update modal header
    const modalHeader = modal.querySelector('.modal-header h3');
    if (modalHeader) {
        modalHeader.textContent = `Close Quote #${quoteId}`;
    }
    
    // Update current status display
    const currentStatusDisplay = modal.querySelector('#current-status-display');
    if (currentStatusDisplay) {
        currentStatusDisplay.textContent = currentStatus;
    }
    
    // Reset form
    resetStatusModalForm();
    
    // Show modal
    modal.style.display = 'flex';
}

/**
 * Close the status modal
 */
function closeStatusModal() {
    const modal = document.getElementById('deal-closer-modal');
    if (modal) {
        modal.style.display = 'none';
        resetStatusModalForm();
    }
}

/**
 * Reset the status modal form to default state
 */
function resetStatusModalForm() {
    // Hide all conditional sections
    const wonSection = document.getElementById('won-section');
    const lostSection = document.getElementById('lost-section');
    
    if (wonSection) wonSection.style.display = 'none';
    if (lostSection) lostSection.style.display = 'none';
    
    // Clear inputs
    const finalPriceInput = document.getElementById('final-agreed-price-input');
    const winNotesInput = document.getElementById('win-notes-input');
    const lossReasonSelect = document.getElementById('loss-reason-select');
    
    if (finalPriceInput) finalPriceInput.value = '';
    if (winNotesInput) winNotesInput.value = '';
    if (lossReasonSelect) lossReasonSelect.value = '';
}

/**
 * Handle status action button clicks
 * @param {string} action - The action to perform ('won', 'lost', 'draft')
 */
async function handleStatusAction(action) {
    const modal = document.getElementById('deal-closer-modal');
    if (!modal) return;
    
    const quoteId = modal.dataset.quoteId;
    const currentStatus = modal.dataset.currentStatus;
    
    console.log(`[SIDEBAR] Status action: ${action} for quote ${quoteId}`);
    
    if (action === 'won') {
        // Show Won section
        const wonSection = document.getElementById('won-section');
        const lostSection = document.getElementById('lost-section');
        
        if (wonSection) wonSection.style.display = 'block';
        if (lostSection) lostSection.style.display = 'none';
        
    } else if (action === 'lost') {
        // Show Lost section
        const wonSection = document.getElementById('won-section');
        const lostSection = document.getElementById('lost-section');
        
        if (wonSection) wonSection.style.display = 'none';
        if (lostSection) lostSection.style.display = 'block';
        
    } else if (action === 'draft') {
        // Revert to Draft (no extra data needed)
        const confirmed = confirm(`Revert Quote #${quoteId} to Draft?\n\nThis will unlock the quote for editing and clear any closure data.`);
        if (confirmed) {
            await submitStatusUpdate(quoteId, 'Draft', {});
        }
    }
}

/**
 * Submit the status update to the backend
 * @param {number} quoteId - The quote ID
 * @param {string} newStatus - The new status
 * @param {object} data - Additional data (win_notes, loss_reason, final_agreed_price)
 */
async function submitStatusUpdate(quoteId, newStatus, data) {
    console.log(`[SIDEBAR] Submitting status update: ${newStatus}`, data);
    
    try {
        const response = await fetch(`/api/quote/${quoteId}/update_status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: newStatus,
                ...data
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('[SIDEBAR] Status update failed:', errorData);
            alert(`Error: ${errorData.error || 'Failed to update status'}`);
            return;
        }
        
        const result = await response.json();
        console.log('[SIDEBAR] Status update successful:', result);
        
        // Close modal
        closeStatusModal();
        
        // Refresh sidebar to show updated status
        loadRecentQuotes();
        
        // Show success message
        alert(`Quote #${quoteId} marked as ${newStatus}`);
        
    } catch (error) {
        console.error('[SIDEBAR] Network error updating status:', error);
        alert('Network error. Please try again.');
    }
}

/**
 * Confirm Won action
 */
async function confirmWon() {
    const modal = document.getElementById('deal-closer-modal');
    if (!modal) return;
    
    const quoteId = modal.dataset.quoteId;
    
    // Get form data
    const finalPriceInput = document.getElementById('final-agreed-price-input');
    const winNotesInput = document.getElementById('win-notes-input');
    
    const finalPrice = finalPriceInput ? parseFloat(finalPriceInput.value) : null;
    const winNotes = winNotesInput ? winNotesInput.value.trim() : '';
    
    // Build data object
    const data = {};
    if (finalPrice && finalPrice > 0) {
        data.final_agreed_price = finalPrice;
    }
    if (winNotes) {
        data.win_notes = winNotes;
    }
    
    await submitStatusUpdate(quoteId, 'Won', data);
}

/**
 * Confirm Lost action
 */
async function confirmLost() {
    const modal = document.getElementById('deal-closer-modal');
    if (!modal) return;
    
    const quoteId = modal.dataset.quoteId;
    
    // Get loss reason
    const lossReasonSelect = document.getElementById('loss-reason-select');
    const lossReason = lossReasonSelect ? lossReasonSelect.value : '';
    
    if (!lossReason) {
        alert('Please select a loss reason');
        return;
    }
    
    // Build data object
    const data = {
        loss_reason: lossReason
    };
    
    await submitStatusUpdate(quoteId, 'Lost', data);
}

// Export functions for global access (called from HTML onclick)
window.openStatusModal = openStatusModal;
window.closeStatusModal = closeStatusModal;
window.handleStatusAction = handleStatusAction;
window.confirmWon = confirmWon;
window.confirmLost = confirmLost;

// ============================================================================
// MULTI-VIEW NAVIGATION (Phase 5.6)
// ============================================================================

/**
 * Show Customers view
 */
function showCustomers() {
    hideAllViews();
    
    const customersView = document.getElementById('customers-view');
    if (customersView) {
        customersView.style.display = 'block';
        
        // Load customers data
        if (window.loadCustomers) {
            window.loadCustomers();
        }
    }
    
    console.log('[SIDEBAR] Customers view shown');
}

/**
 * Hide all views (including new customers view)
 */
function hideAllViews() {
    const views = [
        'landing-screen',
        'customers-view',
        'result-card',
        'quote-metadata',
        'physics-section',
        'configuration-section',
        'economics-section',
        'viewer-section'
    ];
    
    views.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    });
}

/**
 * Show Dashboard (stub - to be implemented)
 */
function showDashboard() {
    hideAllViews();
    // For now, show landing screen (same as New Quote)
    // TODO: Create proper dashboard view
    showLandingScreen();
    console.log('[SIDEBAR] Dashboard (landing) shown');
}

/**
 * Show Parts Library (stub - to be implemented)
 */
function showPartsLibrary() {
    hideAllViews();
    alert('Parts Library - Coming Soon');
    console.log('[SIDEBAR] Parts Library (not yet implemented)');
}

/**
 * Show Configuration (stub - to be implemented)
 */
function showConfiguration() {
    hideAllViews();
    alert('Configuration - Coming Soon');
    console.log('[SIDEBAR] Configuration (not yet implemented)');
}

