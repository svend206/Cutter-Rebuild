/**
 * api.js - Backend Communication Module
 */

import * as state from './state.js';
import * as rfq from './rfq.js';

export async function calculateQuote(formData) {
    formData.append('ops_mode', state.getOpsMode());
    const response = await fetch('/quote', { method: 'POST', body: formData });
    if (!response.ok) throw new Error('Quote calculation failed');
    return await response.json();
}

export async function recalculateQuote(data) {
    // Read CURRENT values from DOM (includes user's edited stock dimensions)
    const stockX = parseFloat(document.getElementById('stock-x')?.value) || 0;
    const stockY = parseFloat(document.getElementById('stock-y')?.value) || 0;
    const stockZ = parseFloat(document.getElementById('stock-z')?.value) || 0;
    const quantity = parseInt(document.getElementById('quantity-input')?.value) || 1;
    const handlingTime = parseFloat(document.getElementById('handling-time')?.value) || 0.5;
    
    const payload = {
        material_name: document.getElementById('material-select')?.value || data.material,
        stock_x: stockX,
        stock_y: stockY,
        stock_z: stockZ,
        part_volume: data.geometry?.volume,
        setup_time: document.getElementById('setup-time')?.value,
        shop_rate: document.getElementById('shop-rate')?.value,
        // Phase 5: complexity_factor removed (always 1.0 for pure physics)
        quantity: quantity,
        handling_time: handlingTime,
        ops_mode: state.getOpsMode()
    };
    
    const response = await fetch('/recalculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    if (!response.ok) throw new Error('Recalculation failed');
    const newPrices = await response.json();
    
    // FIX BUG 1: Update stock dimensions with CURRENT DOM values (don't revert to old values)
    return { 
        ...data, 
        ...newPrices, 
        physics_price: newPrices,
        stock: {
            x: stockX,
            y: stockY,
            z: stockZ,
            volume: stockX * stockY * stockZ
        }
    };
}

export async function saveQuote(data, options) {
    // 1. Get Quote ID
    const quoteIdInput = document.getElementById('quote-id-input');
    const customQuoteId = quoteIdInput ? quoteIdInput.value.trim() : '';
    
    // 2. Get Price (Clean formatting)
    const finalPrice = parseFloat(document.getElementById('total-price')?.textContent.replace('$','').replace(/[^\d.]/g, '')) || 0;
    
    // 3. Get Anchor Price (Physics Floor)
    const anchorPrice = data.physics_price?.total_price || data.price?.total_price || finalPrice;

    // 4. Get Database ID for Smart Save (Edit vs. New)
    const dbId = state.getCurrentDbId();

    // 4b. PHASE 4: Extract Customer/Contact Identity (Guild Intelligence)
    const customerInput = document.getElementById('customer-input');
    const contactInput = document.getElementById('contact-input');
    
    const customerName = customerInput?.value.trim() || 'Unknown';
    const customerId = customerInput?.dataset.selectedId || null;
    const customerDomain = customerInput?.dataset.selectedDomain || null;
    
    const contactName = contactInput?.value.trim() || 'Unknown';
    const contactId = contactInput?.dataset.selectedId || null;
    const contactEmail = contactInput?.dataset.selectedEmail || null;

    // 5. Construct Full Payload
    const payload = {
        id: dbId,  // Smart Save: Include DB ID for UPDATE vs INSERT
        filename: data.filename || 'Unknown',
        fingerprint: data.fingerprint || [],
        genesis_hash: data.genesis_hash || null,  // Phase 5.5: The "ISBN" (File Mode)
        final_price: finalPrice,
        anchor_price: anchorPrice,
        setup_time: parseFloat(document.getElementById('setup-time')?.value) || 60,
        handling_time: parseFloat(document.getElementById('handling-time')?.value) || 0.5,
        material: document.getElementById('material-select')?.value || 'Unknown',
        tag_weights: options.tagWeights || {},
        process_routing: Array.from(options.selectedTravelers || []),
        source_type: options.isManualMode ? 'manual' : 'file',
        reference_image: options.referenceImagePath,
        quote_id: customQuoteId,
        // PHASE 4: Identity (Both ID and raw text for forgiving resolution)
        customer_id: customerId,
        customer_name: customerName,
        customer_domain: customerDomain,
        contact_id: contactId,
        contact_name: contactName,
        contact_email: contactEmail,
        // PHASE 5: RFQ-First Fields
        ...rfq.getRFQData()
    };
    
    // Phase 5.5: Add parametric shape config if in Napkin Mode
    if (options.isManualMode) {
        try {
            const parametric = await import('./parametric.js');
            const shapeConfig = parametric.getCurrentShapeConfig();
            if (shapeConfig && shapeConfig.type && shapeConfig.volume > 0) {
                payload.shape_config = shapeConfig;
                console.log('[API] Including shape config for Genesis Hash:', shapeConfig);
            }
        } catch (error) {
            console.warn('[API] Could not get parametric shape config:', error);
        }
    }
    
    // 6. Add Glass Box Data (Phase 4: O-Score Tracking)
    if (options.glassBoxData) {
        payload.system_price_anchor = options.glassBoxData.system_price_anchor;
        payload.final_quoted_price = options.glassBoxData.final_quoted_price;
        payload.variance_attribution = options.glassBoxData.variance_attribution;
    }
    
    console.log("Saving Quote Payload:", payload);

    const response = await fetch('/save_quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
        const text = await response.text();
        throw new Error(`Save failed: ${text}`);
    }
    
    const result = await response.json();
    
    // 6. Update State: Store returned ID for subsequent saves
    if (result.id) {
        state.setCurrentDbId(result.id);
        console.log(`📌 Smart Save: Current DB ID = ${result.id}`);
    }
    
    // 7. Refresh sidebar quote history (Phase 5)
    try {
        const sidebar = await import('./sidebar.js');
        sidebar.refreshQuoteHistory();
    } catch (error) {
        console.warn('[API] Could not refresh sidebar history:', error);
    }
    
    return result;
}

export async function loadMaterials() {
    try {
        const res = await fetch('/materials');
        const data = await res.json();
        const select = document.getElementById('material-select');
        if (select && data.materials) {
            select.innerHTML = '<option value="">Select Material...</option>'; 
            data.materials.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                select.appendChild(opt);
            });
        }
    } catch(e) { console.error("Mat load error", e); }
}

export async function fetchHistory() {
    const res = await fetch('/history');
    const data = await res.json();
    return data.history || [];
}

export async function fetchTags() {
    try {
        const response = await fetch('/tags');
        const data = await response.json();
        
        if (data.tags && Array.isArray(data.tags)) {
            // Populate state.activeMarkups with tag names and their default markups
            const markups = {};
            data.tags.forEach(tag => {
                if (tag.is_active) {
                    markups[tag.name] = tag.default_markup || 0;
                }
            });
            
            // Use setter to update state
            state.setActiveMarkups(markups);
            console.log('[TAGS] Loaded pricing tags:', Object.keys(markups));
            return data.tags;
        } else {
            console.warn('[TAGS] No tags returned from backend');
            return [];
        }
    } catch (error) {
        console.error('[TAGS] Failed to fetch tags:', error);
        return [];
    }
}

// --- Partner Mode (Win/Loss/Sync) ---

export async function updateQuoteStatus(payload) {
    const response = await fetch('/update_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function exportGuildPacket() {
    const response = await fetch('/export_guild_packet');
    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `guild_packet_${new Date().toISOString().slice(0,10)}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        return true;
    }
    throw new Error('Export failed');
}

export async function getPendingExports() {
    const res = await fetch('/pending_exports');
    return await res.json();
}

// --- Quote ID Validation ---

export async function checkQuoteId(quoteId) {
    /**
     * Check if a Quote ID already exists in the database.
     * Returns: { exists: boolean, quote_id: string }
     */
    if (!quoteId || quoteId.trim() === '') {
        return { exists: false, quote_id: '' };
    }
    
    try {
        const response = await fetch(`/check_quote_id/${encodeURIComponent(quoteId)}`);
        if (!response.ok) {
            console.error('Failed to check quote ID');
            return { exists: false, quote_id: quoteId };
        }
        return await response.json();
    } catch (error) {
        console.error('Error checking quote ID:', error);
        return { exists: false, quote_id: quoteId };
    }
}
