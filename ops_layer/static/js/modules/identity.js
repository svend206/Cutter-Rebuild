/**
 * identity.js - Customer/Contact Autocomplete (Phase 4: Guild Intelligence)
 * Handles smart entity selection with forgiving free-text fallback
 */

// Debounce timers
const debounceTimers = {};

/**
 * Initialize identity autocomplete fields
 */
export function initIdentity() {
    const customerInput = document.getElementById('customer-input');
    const customerResults = document.getElementById('customer-results');
    const contactInput = document.getElementById('contact-input');
    const contactResults = document.getElementById('contact-results');
    
    if (!customerInput || !contactInput) {
        console.warn('[IDENTITY] Customer/Contact inputs not found. Skipping initialization.');
        return;
    }
    
    // Setup Customer autocomplete
    setupAutocomplete(
        customerInput,
        customerResults,
        '/api/customers/search',
        (selected) => {
            // On customer selection
            customerInput.value = selected.name;
            customerInput.dataset.selectedId = selected.id;
            customerInput.dataset.selectedDomain = selected.domain || '';
            
            // Enable contact input
            contactInput.disabled = false;
            contactInput.dataset.customerId = selected.id;
            
            console.log(`[IDENTITY] Customer selected: ${selected.name} (ID: ${selected.id})`);
        },
        (input) => {
            // Format result item for customer
            return `<strong>${input.name}</strong>${input.domain ? ` <span style="color: #aaaaaa;">(${input.domain})</span>` : ''}`;
        }
    );
    
    // Setup Contact autocomplete
    setupAutocomplete(
        contactInput,
        contactResults,
        '/api/contacts/search',
        (selected) => {
            // On contact selection
            contactInput.value = selected.name;
            contactInput.dataset.selectedId = selected.id;
            contactInput.dataset.selectedEmail = selected.email || '';
            
            console.log(`[IDENTITY] Contact selected: ${selected.name} (ID: ${selected.id})`);
        },
        (input) => {
            // Format result item for contact
            return `<strong>${input.name}</strong>${input.email ? ` <span style="color: #aaaaaa;">(${input.email})</span>` : ''}`;
        },
        () => {
            // Get customer filter
            const customerId = contactInput.dataset.customerId;
            return customerId ? `&customer_id=${customerId}` : '';
        }
    );
    
    // Handle customer input changes (typing/clearing)
    customerInput.addEventListener('input', () => {
        // If user types over a selected customer, clear the ID
        if (customerInput.dataset.selectedId) {
            delete customerInput.dataset.selectedId;
            delete customerInput.dataset.selectedDomain;
        }
        
        // Enable/disable contact field based on whether customer has text
        if (customerInput.value.trim()) {
            // Customer has text → Enable contact input (even for new customers)
            contactInput.disabled = false;
            contactInput.placeholder = 'Enter contact name...';
        } else {
            // Customer is empty → Disable and clear contact
            contactInput.disabled = true;
            contactInput.placeholder = 'Select customer first...';
            contactInput.value = '';
            delete contactInput.dataset.selectedId;
            delete contactInput.dataset.selectedEmail;
            delete contactInput.dataset.customerId;
        }
    });
    
    console.log('[IDENTITY] Customer/Contact autocomplete initialized');
}

/**
 * Setup autocomplete for an input field
 * @param {HTMLElement} input - The input element
 * @param {HTMLElement} resultsDiv - The results container
 * @param {string} apiEndpoint - The API endpoint to fetch results
 * @param {Function} onSelect - Callback when item is selected
 * @param {Function} formatItem - Function to format result item HTML
 * @param {Function} getExtraParams - Function to get additional query params
 */
function setupAutocomplete(input, resultsDiv, apiEndpoint, onSelect, formatItem = null, getExtraParams = null) {
    if (!input || !resultsDiv) return;
    
    // Input event - debounced search
    input.addEventListener('input', () => {
        const query = input.value.trim();
        
        // Clear previous timer
        if (debounceTimers[input.id]) {
            clearTimeout(debounceTimers[input.id]);
        }
        
        // Hide results if query too short
        if (query.length < 2) {
            resultsDiv.style.display = 'none';
            return;
        }
        
        // Debounce: Wait 300ms after user stops typing
        debounceTimers[input.id] = setTimeout(() => {
            fetchResults(query, apiEndpoint, resultsDiv, onSelect, formatItem, getExtraParams);
        }, 300);
    });
    
    // Blur event - hide results after delay
    input.addEventListener('blur', () => {
        // Delay to allow click on result item
        setTimeout(() => {
            resultsDiv.style.display = 'none';
        }, 200);
    });
    
    // Focus event - show results if they exist
    input.addEventListener('focus', () => {
        if (resultsDiv.children.length > 0) {
            resultsDiv.style.display = 'block';
        }
    });
    
    // Keyboard support - Enter key dismisses dropdown when no results
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && resultsDiv.style.display === 'block') {
            resultsDiv.style.display = 'none';
            e.preventDefault(); // Prevent form submission
        }
    });
}

/**
 * Fetch autocomplete results from API
 */
async function fetchResults(query, apiEndpoint, resultsDiv, onSelect, formatItem, getExtraParams) {
    try {
        const extraParams = getExtraParams ? getExtraParams() : '';
        const response = await fetch(`${apiEndpoint}?q=${encodeURIComponent(query)}${extraParams}`);
        
        if (!response.ok) {
            console.error('[IDENTITY] Search failed:', response.statusText);
            return;
        }
        
        const data = await response.json();
        const results = data.results || [];
        
        // Clear previous results
        resultsDiv.innerHTML = '';
        
        if (results.length === 0) {
            // Show helpful, non-interactive message
            resultsDiv.innerHTML = '<div class="autocomplete-no-results" style="padding: 12px; color: #aaaaaa; font-style: italic; cursor: default; pointer-events: none;">No existing match found. Press Enter or click outside to create new entry.</div>';
            resultsDiv.style.display = 'block';
            return;
        }
        
        // Render results
        results.forEach(item => {
            const div = document.createElement('div');
            div.innerHTML = formatItem ? formatItem(item) : item.name;
            div.style.cursor = 'pointer';
            
            // Click handler
            div.addEventListener('mousedown', (e) => {
                e.preventDefault(); // Prevent blur from firing first
                onSelect(item);
                resultsDiv.style.display = 'none';
            });
            
            resultsDiv.appendChild(div);
        });
        
        resultsDiv.style.display = 'block';
        
    } catch (error) {
        console.error('[IDENTITY] Autocomplete error:', error);
    }
}

