/**
 * customers.js - Customer Management Module
 * Handles customer list, details, and CRUD operations
 * Phase 5.6 - Node 1 Perfection
 */

let currentCustomerId = null;
let customersData = [];

/**
 * Initialize Customers View
 */
export function initCustomers() {
    // Add Customer button
    const addBtn = document.getElementById('add-customer-btn');
    if (addBtn) {
        addBtn.addEventListener('click', openAddCustomerModal);
    }
    
    // Customer search
    const searchInput = document.getElementById('customer-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterCustomers, 300));
    }
    
    // Customer form submit
    const customerForm = document.getElementById('customer-form');
    if (customerForm) {
        customerForm.addEventListener('submit', handleCustomerSubmit);
    }
    
    // Contact form submit
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactSubmit);
    }
    
    console.log('[CUSTOMERS] Module initialized');
}

/**
 * Load and display all customers
 */
export async function loadCustomers() {
    try {
        const response = await fetch('/api/customers');
        const data = await response.json();
        
        if (!data.success) {
            console.error('[CUSTOMERS] Failed to load:', data.error);
            return;
        }
        
        customersData = data.customers || [];
        renderCustomerTable(customersData);
        
    } catch (error) {
        console.error('[CUSTOMERS] Error loading customers:', error);
    }
}

/**
 * Render customer table
 */
function renderCustomerTable(customers) {
    const tbody = document.getElementById('customer-table-body');
    const emptyState = document.getElementById('customer-empty-state');
    
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (customers.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        return;
    }
    
    if (emptyState) emptyState.style.display = 'none';
    
    customers.forEach(customer => {
        const row = createCustomerRow(customer);
        tbody.appendChild(row);
    });
}

/**
 * Create a customer table row
 */
function createCustomerRow(customer) {
    const row = document.createElement('tr');
    row.dataset.customerId = customer.id;
    row.classList.add('customer-row');
    
    row.innerHTML = `
        <td><strong>${escapeHtml(customer.company_name)}</strong><br>
            <small style="color: #888;">${customer.domain || ''}</small></td>
        <td>${customer.parts_count}</td>
        <td>${customer.contacts_count}</td>
        <td>${customer.quotes_count}</td>
        <td>${customer.jobs_count}</td>
        <td>${formatDate(customer.last_active)}</td>
        <td>
            <button class="icon-button" onclick="window.editCustomer(${customer.id})">✏️</button>
            <button class="icon-button" onclick="window.deleteCustomer(${customer.id})">🗑️</button>
        </td>
    `;
    
    // Click row to expand/collapse details
    row.addEventListener('click', (e) => {
        // Don't expand if clicking action buttons
        if (e.target.classList.contains('icon-button')) return;
        
        toggleCustomerDetails(customer.id, row);
    });
    
    return row;
}

/**
 * Toggle customer details (expand/collapse row)
 */
async function toggleCustomerDetails(customerId, row) {
    const existingDetails = row.nextElementSibling;
    
    // If details already open, close them
    if (existingDetails && existingDetails.classList.contains('customer-details')) {
        existingDetails.remove();
        return;
    }
    
    // Load and show details
    try {
        const response = await fetch(`/api/customer/${customerId}`);
        const data = await response.json();
        
        if (!data.success) {
            console.error('[CUSTOMERS] Failed to load details:', data.error);
            return;
        }
        
        const detailsRow = createCustomerDetailsRow(data.customer);
        row.after(detailsRow);
        
    } catch (error) {
        console.error('[CUSTOMERS] Error loading customer details:', error);
    }
}

/**
 * Create expanded customer details row
 */
function createCustomerDetailsRow(customer) {
    const detailsRow = document.createElement('tr');
    detailsRow.classList.add('customer-details');
    
    const td = document.createElement('td');
    td.colSpan = 7;
    
    td.innerHTML = `
        <div class="detail-section">
            <h4>📋 Parts (${customer.parts.length})</h4>
            <ul class="detail-list">
                ${customer.parts.map(part => `
                    <li>
                        <span>• ${escapeHtml(part.filename || part.genesis_hash.substring(0, 8))} 
                        - ${part.total_quotes} quotes</span>
                    </li>
                `).join('') || '<li style="color: #888;">No parts yet</li>'}
            </ul>
        </div>
        
        <div class="detail-section">
            <h4>👥 Contacts (${customer.contacts.length}) 
                <button class="icon-button" onclick="window.openAddContactModal(${customer.id})">➕ Add</button>
            </h4>
            <ul class="detail-list">
                ${customer.contacts.map(contact => `
                    <li>
                        <span>
                            • ${escapeHtml(contact.name)} 
                            ${contact.email ? `(${escapeHtml(contact.email)})` : ''} 
                            - ${contact.quote_count} quotes
                            ${contact.is_primary ? '<span style="color: #ffaa00;">★</span>' : ''}
                        </span>
                        <div class="detail-actions">
                            <button class="icon-button" onclick="window.editContact(${contact.id})">✏️</button>
                            <button class="icon-button" onclick="window.deleteContact(${contact.id})">🗑️</button>
                        </div>
                    </li>
                `).join('') || '<li style="color: #888;">No contacts yet</li>'}
            </ul>
        </div>
        
        <div class="detail-section">
            <h4>📊 Activity Summary</h4>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="summary-value">${customer.summary.total_quotes}</span>
                    <span class="summary-label">Total Quotes</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value" style="color: #44ff44;">${customer.summary.won_count}</span>
                    <span class="summary-label">Won</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value" style="color: #ff4444;">${customer.summary.lost_count}</span>
                    <span class="summary-label">Lost</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value" style="color: #ffaa00;">${customer.summary.unclosed_count}</span>
                    <span class="summary-label">Unclosed</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value">$${customer.summary.total_revenue.toFixed(2)}</span>
                    <span class="summary-label">Revenue</span>
                </div>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>📜 Recent History (Last 10)</h4>
            <ul class="detail-list">
                ${customer.history.map(item => `
                    <li>
                        <span>${escapeHtml(item.quote_id)} | $${item.price ? item.price.toFixed(2) : '0.00'} | 
                        ${escapeHtml(item.status) || 'Unclosed'} | ${escapeHtml(item.contact_name || '')}</span>
                        <span style="color: #888;">${formatDate(item.date)}</span>
                    </li>
                `).join('') || '<li style="color: #888;">No history yet</li>'}
            </ul>
        </div>
    `;
    
    detailsRow.appendChild(td);
    return detailsRow;
}

/**
 * Filter customers by search query
 */
function filterCustomers() {
    const query = document.getElementById('customer-search').value.toLowerCase();
    
    if (!query) {
        renderCustomerTable(customersData);
        return;
    }
    
    const filtered = customersData.filter(customer => {
        return customer.company_name.toLowerCase().includes(query) ||
               (customer.domain && customer.domain.toLowerCase().includes(query));
    });
    
    renderCustomerTable(filtered);
}

/**
 * Open Add Customer Modal
 */
function openAddCustomerModal() {
    document.getElementById('customer-modal-title').textContent = 'Add Customer';
    document.getElementById('customer-modal-id').value = '';
    document.getElementById('customer-modal-company').value = '';
    document.getElementById('customer-modal-domain').value = '';
    document.getElementById('customer-modal').style.display = 'flex';
}

/**
 * Open Edit Customer Modal
 */
window.editCustomer = async function(customerId) {
    try {
        const response = await fetch(`/api/customer/${customerId}`);
        const data = await response.json();
        
        if (!data.success) {
            alert('Failed to load customer details');
            return;
        }
        
        const customer = data.customer;
        document.getElementById('customer-modal-title').textContent = 'Edit Customer';
        document.getElementById('customer-modal-id').value = customer.id;
        document.getElementById('customer-modal-company').value = customer.company_name;
        document.getElementById('customer-modal-domain').value = customer.domain || '';
        document.getElementById('customer-modal').style.display = 'flex';
        
    } catch (error) {
        console.error('[CUSTOMERS] Error loading customer for edit:', error);
        alert('Failed to load customer');
    }
};

/**
 * Close Customer Modal
 */
window.closeCustomerModal = function() {
    document.getElementById('customer-modal').style.display = 'none';
};

/**
 * Handle Customer Form Submit
 */
async function handleCustomerSubmit(e) {
    e.preventDefault();
    
    const customerId = document.getElementById('customer-modal-id').value;
    const companyName = document.getElementById('customer-modal-company').value;
    const domain = document.getElementById('customer-modal-domain').value;
    
    try {
        const url = customerId ? `/api/customer/${customerId}` : '/api/customer';
        const method = customerId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                company_name: companyName,
                domain: domain || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.closeCustomerModal();
            await loadCustomers();
            showToast(customerId ? 'Customer updated' : 'Customer created', 'success');
        } else {
            showToast('Failed to save customer: ' + data.error, 'error');
        }
        
    } catch (error) {
        console.error('[CUSTOMERS] Error saving customer:', error);
        showToast('Failed to save customer', 'error');
    }
}

/**
 * Delete Customer
 */
window.deleteCustomer = async function(customerId) {
    if (!confirm('Delete this customer? This will not delete their quotes, but will break the relationship.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/customer/${customerId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadCustomers();
            showToast('Customer deleted', 'success');
        } else {
            showToast('Failed to delete customer', 'error');
        }
        
    } catch (error) {
        console.error('[CUSTOMERS] Error deleting customer:', error);
        showToast('Failed to delete customer', 'error');
    }
};

/**
 * Open Add Contact Modal
 */
window.openAddContactModal = function(customerId) {
    currentCustomerId = customerId;
    document.getElementById('contact-modal-title').textContent = 'Add Contact';
    document.getElementById('contact-modal-id').value = '';
    document.getElementById('contact-modal-customer-id').value = customerId;
    document.getElementById('contact-modal-name').value = '';
    document.getElementById('contact-modal-email').value = '';
    document.getElementById('contact-modal-phone').value = '';
    document.getElementById('contact-modal').style.display = 'flex';
};

/**
 * Open Edit Contact Modal
 */
window.editContact = async function(contactId) {
    // Would need to fetch contact details first
    // Simplified for now - just open modal with empty fields
    document.getElementById('contact-modal-title').textContent = 'Edit Contact';
    document.getElementById('contact-modal-id').value = contactId;
    document.getElementById('contact-modal').style.display = 'flex';
};

/**
 * Close Contact Modal
 */
window.closeContactModal = function() {
    document.getElementById('contact-modal').style.display = 'none';
};

/**
 * Handle Contact Form Submit
 */
async function handleContactSubmit(e) {
    e.preventDefault();
    
    const contactId = document.getElementById('contact-modal-id').value;
    const customerId = document.getElementById('contact-modal-customer-id').value || currentCustomerId;
    const contactName = document.getElementById('contact-modal-name').value;
    const email = document.getElementById('contact-modal-email').value;
    const phone = document.getElementById('contact-modal-phone').value;
    
    try {
        const url = contactId ? `/api/contact/${contactId}` : `/api/customer/${customerId}/contact`;
        const method = contactId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contact_name: contactName,
                email: email || null,
                phone: phone || null,
                is_primary: false
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.closeContactModal();
            await loadCustomers();
            showToast(contactId ? 'Contact updated' : 'Contact created', 'success');
        } else {
            showToast('Failed to save contact: ' + data.error, 'error');
        }
        
    } catch (error) {
        console.error('[CUSTOMERS] Error saving contact:', error);
        showToast('Failed to save contact', 'error');
    }
}

/**
 * Delete Contact
 */
window.deleteContact = async function(contactId) {
    if (!confirm('Delete this contact?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/contact/${contactId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadCustomers();
            showToast('Contact deleted', 'success');
        } else {
            showToast('Failed to delete contact', 'error');
        }
        
    } catch (error) {
        console.error('[CUSTOMERS] Error deleting contact:', error);
        showToast('Failed to delete contact', 'error');
    }
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleDateString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

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

