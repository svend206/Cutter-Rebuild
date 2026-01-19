/**
 * main.js - Application Entry Point
 * 
 * This is the main entry point for Project Cutter.
 * It imports all modules and wires up event listeners.
 */

// Verify Three.js is loaded (must be loaded before modules that use it)
console.log("Three.js loaded:", typeof THREE !== 'undefined');
console.log("STLLoader loaded:", typeof THREE !== 'undefined' && typeof THREE.STLLoader !== 'undefined');

if (typeof THREE === 'undefined') {
    console.error("ERROR: THREE is not defined! Check if /static/js/vendor/three.min.js loaded correctly.");
}
if (typeof THREE !== 'undefined' && typeof THREE.STLLoader === 'undefined') {
    console.error("ERROR: THREE.STLLoader is not defined! Check if /static/js/vendor/STLLoader.js loaded correctly.");
}

// Import modules
import * as state from './modules/state.js';
import * as api from './modules/api.js';
import * as viewer from './modules/viewer.js';
import * as manual from './modules/manual.js';
import * as ui from './modules/ui.js';
import * as variance from './modules/variance.js';
import * as saveConfirm from './modules/save_confirm.js';
import * as sidebar from './modules/sidebar.js'; // Phase 4: Sidebar navigation
import * as identity from './modules/identity.js'; // Phase 4: Customer/Contact autocomplete
import * as rfq from './modules/rfq.js'; // Phase 5: RFQ-First workflow
import * as parametric from './modules/parametric.js'; // Phase 5.5: Parametric Configurator
import * as outcome from './modules/outcome.js'; // Quote outcome tracking
import * as customers from './modules/customers.js'; // Phase 5.6: Customer Management

// Get DOM elements (these are used across modules)
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const fileName = document.getElementById('file-name');
const calculateBtn = document.getElementById('calculate-btn');
const resultCard = document.getElementById('result-card');
const errorMessage = document.getElementById('error-message');
const loading = document.getElementById('loading');
const historyAlert = document.getElementById('history-alert');
const tagZone = document.getElementById('tag-zone');
const tagBadges = document.getElementById('tag-badges');
const saveButton = document.getElementById('save-button');
const toast = document.getElementById('toast');

// Recalculate debounce timeout (module-level variable)
let recalculateTimeout = null;

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing Project Cutter...');
    
    // UX: Auto-select text on all number inputs when focused
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('focus', function() {
            this.select();
        });
    });
    
    // Phase 4: Initialize Sidebar (Desktop only, hidden on mobile)
    sidebar.initSidebar();
    
    // Phase 4: Initialize Identity Autocomplete (Guild Intelligence)
    identity.initIdentity();
    
    // Phase 4: Initialize Variance UI (Price Stack interactions)
    variance.initVarianceUI();
    
    // Phase 5: Initialize RFQ Module (RFQ-First workflow)
    rfq.initRFQ();
    
    // Phase 5.5: Initialize Parametric Configurator (Napkin Mode shape builder)
    parametric.initParametricConfigurator();
    
    // Phase 5.6: Initialize Quick-Fix Buttons (Unit Verification - Enhanced UX)
    ui.initQuickFixButtons();
    
    // Phase 5.6: Initialize Customers Module
    customers.initCustomers();
    
    // Initialize Three.js viewer
    viewer.initViewer();
    
    // Load initial data
    await api.loadMaterials();
    await api.fetchTags();
    
    // Load unclosed quotes for landing page
    await outcome.loadUnclosedQuotes();
    ui.loadHistory();
    // PHASE 1 REMEDIATION: ui.loadGuildCredits() removed - Guild display violates firewall
    
    // Set up event listeners
    setupEventListeners();
    
    // Make customers functions available globally
    window.loadCustomers = customers.loadCustomers;
    
    console.log('Project Cutter initialized.');
});

/**
 * Set up all event listeners
 */
function setupEventListeners() {
    // File upload handlers
    if (uploadZone) {
        uploadZone.addEventListener('click', () => {
            if (fileInput) fileInput.click();
        });
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
    }
    
    // Drag and drop
    if (uploadZone) {
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }
    
    // Calculate button
    if (calculateBtn) {
        calculateBtn.addEventListener('click', async () => {
            const file = state.getSelectedFile();
            
            if (!file) {
                ui.showError('Please select a file first.');
                return;
            }
            
            console.log(`🔄 Calculate button clicked. Processing: ${file.name}`);
            
            // Reset DB ID for new quote (not editing)
            state.setCurrentDbId(null);
            
            // Disable button during calculation to prevent double-clicks
            calculateBtn.disabled = true;
            
            try {
                await calculateQuote();
            } catch (error) {
                console.error('Calculation failed:', error);
                ui.showError(error.message || 'Failed to calculate quote.');
            } finally {
                // Re-enable button after calculation (success or failure)
                calculateBtn.disabled = false;
            }
        });
    }
    
    // ==== NEW LANDING SCREEN FLOW ====
    // Landing Screen: File Mode Choice
    const fileModeChoiceBtn = document.getElementById('file-mode-choice-btn');
    if (fileModeChoiceBtn) {
        fileModeChoiceBtn.addEventListener('click', () => {
            state.setCurrentDbId(null); // Reset for new quote
            manual.initFileMode();
        });
    }
    
    // Landing Screen: Manual Mode Choice
    const manualModeChoiceBtn = document.getElementById('manual-mode-choice-btn');
    if (manualModeChoiceBtn) {
        manualModeChoiceBtn.addEventListener('click', () => {
            state.setCurrentDbId(null); // Reset for new quote
            manual.initManualMode();
        });
    }
    
    // Home Button (Return to Landing Screen from any mode)
    const homeBtn = document.getElementById('home-btn');
    if (homeBtn) {
        homeBtn.addEventListener('click', () => {
            manual.showLandingScreen();
        });
    }
    
    // Save button
    if (saveButton) {
        saveButton.addEventListener('click', async () => {
            await handleSaveQuote();
        });
    }
    
    // Recalculate listeners (for inputs that trigger recalculation)
    setupRecalculateListeners();
    
    // Tag modal handlers (set up in ui.js)
    ui.setupTagModalHandlers();
    
    // Quote ID validation (set up in ui.js)
    ui.setupQuoteIdValidation();
    
    // Market Intelligence help modal (set up in ui.js)
    ui.setupMarketHelpModal();
    
    // Traveler badge handlers (set up in ui.js)
    ui.setupTravelerHandlers();
    
    // History table handlers (set up in ui.js)
    ui.setupHistoryHandlers();
    
    // Sticky HUD visibility (set up in ui.js)
    ui.setupStickyHud();
}

/**
 * Handle file selection
 * NOTE: Does NOT auto-calculate. User must click "Calculate Quote" button.
 */
function handleFile(file) {
    state.setSelectedFile(file);
    
    if (fileName) {
        fileName.textContent = file.name;
    }
    
    // Enable Calculate button now that we have a file
    if (calculateBtn) {
        calculateBtn.disabled = false;
    }
    
    // Clear any previous errors
    if (errorMessage) {
        errorMessage.classList.remove('visible');
    }
    
    console.log(`File selected: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`);
    console.log('✅ Calculate button enabled. User can now click "Calculate Quote".');
}

/**
 * Calculate quote from uploaded file
 */
async function calculateQuote() {
    console.log('📍 calculateQuote() called');
    
    const file = state.getSelectedFile();
    console.log('📍 File from state:', file ? file.name : 'NULL');
    
    if (!file) {
        console.error('❌ No file in state!');
        ui.showError('Please select a file first.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    console.log('📍 FormData created, sending to backend...');
    
    try {
        const data = await api.calculateQuote(formData);
        console.log('📍 Response received from backend:', data);
        
        state.setCurrentQuoteData(data);
        console.log('📍 Quote data stored in state');
        
        // Display results
        console.log('📍 Calling displayResult()...');
        ui.displayResult(data);
        console.log('✅ displayResult() completed');
        
        // OPTIMIZATION PASS 1: Load 3D model from streaming URL
        if (data.model_url) {
            console.log('📍 Loading 3D model from:', data.model_url);
            viewer.loadModelFromUrl(data.model_url);
        } else if (data.geometry && data.geometry.model_base64) {
            // Fallback for legacy Base64 (deprecated)
            console.log('📍 Loading 3D model from Base64 (legacy)');
            viewer.loadModelFromBase64(data.geometry.model_base64);
        } else {
            console.warn('⚠️ No model data in response');
        }
        
    } catch (error) {
        console.error('❌ calculateQuote() error:', error);
        ui.showError(error.message || 'Failed to calculate quote.');
    }
}

/**
 * Handle save quote
 */
async function handleSaveQuote() {
    if (!state.getCurrentQuoteData()) {
        ui.showError('No quote data to save.');
        return;
    }
    
    // Phase 4: Validate Glass Box variance (if visible)
    const varianceSliders = document.getElementById('variance-sliders');
    if (varianceSliders && varianceSliders.style.display !== 'none') {
        if (!variance.validateVariance()) {
            ui.showError('Variance attribution must sum to exactly 100% before saving.');
            return;
        }
    }
    
    try {
        // Get Glass Box data (if present)
        const glassBoxData = variance.getGlassBoxData();
        
        // Prepare save options
        const saveOptions = {
            selectedTags: state.selectedTags,
            tagWeights: state.tagWeights,
            selectedTravelers: state.selectedTravelers,
            isManualMode: state.getIsManualMode(),
            referenceImagePath: state.referenceImagePath,
            glassBoxData: glassBoxData  // NEW: Phase 4 Glass Box tracking
        };
        
        // Show save confirmation modal (handles duplicate detection)
        const success = await saveConfirm.showSaveConfirmation(state.getCurrentQuoteData(), saveOptions);
        
        if (success) {
            ui.showToast('Saved!');
            ui.loadHistory();
            
            // DON'T clear tags after save - user might still be working on this quote
            // Tags will be cleared when user starts a new quote (Back to Home, new file, etc.)
            console.log('✅ Quote saved. Tags preserved for duplicate detection.');
        }
        
    } catch (error) {
        ui.showError(error.message || 'Failed to save quote.');
    }
}

/**
 * Set up listeners for inputs that trigger recalculation
 */
function setupRecalculateListeners() {
    // Material select
    const materialSelect = document.getElementById('material-select');
    if (materialSelect) {
        materialSelect.addEventListener('change', () => {
            // CRITICAL: Unlock price when material changes (fundamental physics change)
            variance.unlockPrice();
            
            if (state.getIsManualMode()) {
                manual.calculateManualQuote();
            } else {
                performRecalculate();
            }
        });
    }
    
    // Wire Stock Dimensions for BOTH modes (unified behavior)
    ['stock-x', 'stock-y', 'stock-z'].forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            // Debounce during typing (don't snap on every keystroke)
            input.oninput = () => {
                ui.debounceSlider('stockDims', () => {
                    if (state.getIsManualMode()) {
                        // NAPKIN MODE: Snap → Update Part Vol → Recalc
                        manual.updateStockDimensions();
                    } else {
                        // FILE MODE: Snap → Update Stock Vol Display → Recalc
                        manual.snapStockToStandard();
                        manual.updateStockVolumeDisplay(); // FIX BUG 2: Update volume display
                        performRecalculate();
                    }
                }, 500); // Wait 500ms after user stops typing
            };
            
            // Snap immediately when user leaves the field (blur)
            input.addEventListener('blur', () => {
                if (state.getIsManualMode()) {
                    manual.updateStockDimensions();
                } else {
                    manual.snapStockToStandard();
                    manual.updateStockVolumeDisplay(); // FIX BUG 2: Update volume display
                    performRecalculate();
                }
            });
        }
    });
    
    // PHASE 5: Complexity slider removed (Glass Box integrity)
    // Rationale: Complexity should be explained via variance tags, not baked into anchor.
    // The anchor price must be pure physics. Bob's intuition goes in variance attribution.
    
    // Setup time - Debounced
    const setupTimeInput = document.getElementById('setup-time');
    if (setupTimeInput) {
        setupTimeInput.addEventListener('input', () => {
            ui.debounceSlider('setupTime', () => {
                if (state.getIsManualMode()) {
                    manual.calculateManualQuote();
                } else {
                    performRecalculate();
                }
            });
        });
    }
    
    // Quantity input - Debounced
    const quantityInput = document.getElementById('quantity-input');
    if (quantityInput) {
        quantityInput.addEventListener('input', () => {
            ui.debounceSlider('quantity', () => {
                if (state.getIsManualMode()) {
                    manual.calculateManualQuote();
                } else {
                    performRecalculate();
                }
            });
        });
    }
    
    // Handling time (Load/Unload) - Debounced
    const handlingTimeInput = document.getElementById('handling-time');
    if (handlingTimeInput) {
        handlingTimeInput.addEventListener('input', () => {
            ui.debounceSlider('handlingTime', () => {
                if (state.getIsManualMode()) {
                    manual.calculateManualQuote();
                } else {
                    performRecalculate();
                }
            });
        });
    }
    
    // Shop rate - Debounced
    const shopRateInput = document.getElementById('shop-rate');
    if (shopRateInput) {
        shopRateInput.addEventListener('input', () => {
            ui.debounceSlider('shopRate', () => {
                if (state.getIsManualMode()) {
                    manual.calculateManualQuote();
                } else {
                    performRecalculate();
                }
            });
        });
    }
    
    // Phase 5.5: Removal Rate Slider REMOVED (replaced by parametric configurator)
    // Part volume is now calculated physically from shape dimensions, not manual input
    
    // Glass Box: Final Price Input (Phase 4: Variance Attribution)
    const finalPriceInput = document.getElementById('final-price-input');
    if (finalPriceInput) {
        finalPriceInput.addEventListener('input', () => {
            variance.handlePriceChange();
        });
    }
}

/**
 * Perform recalculation (file mode)
 */
async function performRecalculate() {
    if (!state.getCurrentQuoteData()) {
        return;
    }
    
    // Clear existing timeout
    if (recalculateTimeout) {
        clearTimeout(recalculateTimeout);
    }
    
    // Debounce recalculation
    recalculateTimeout = setTimeout(async () => {
        try {
            const data = await api.recalculateQuote(state.getCurrentQuoteData());
            state.setCurrentQuoteData(data);
            ui.displayResult(data);
        } catch (error) {
            console.error('Recalculation error:', error);
        }
    }, 300);
}

// Export for use in other modules if needed
export { handleFile, calculateQuote, performRecalculate };

