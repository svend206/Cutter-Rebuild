/**
 * state.js - Central State Management
 */

// Global State Variables
export let currentQuoteData = null;
export let isManualMode = false;
export let selectedFile = null;
export let selectedTags = new Set();
export let tagWeights = {};
export let selectedTravelers = new Set();
export let activeMarkups = {}; // { tagName: percentage }
export let referenceImagePath = null;
export let recalculateTimeout = null;
export let currentDbId = null; // Database PK for Smart Save (Edit vs. New)
export let currentGenesisHash = null; // Phase 5.5: The "ISBN" of current part
export let opsMode = 'execution'; // Explicit default: execution | planning

// Setters
export function setCurrentQuoteData(data) { 
    currentQuoteData = data;
    // Phase 5.5: Store Genesis Hash if present
    if (data && data.genesis_hash) {
        currentGenesisHash = data.genesis_hash;
        console.log('[STATE] Genesis Hash stored:', currentGenesisHash.substring(0, 16) + '...');
    }
}
export function setIsManualMode(bool) { isManualMode = bool; }
export function setSelectedFile(file) { selectedFile = file; }
export function setReferenceImagePath(path) { referenceImagePath = path; }
export function setCurrentDbId(id) { currentDbId = id; }
export function setCurrentGenesisHash(hash) { 
    currentGenesisHash = hash;
    console.log('[STATE] Genesis Hash updated:', hash ? hash.substring(0, 16) + '...' : 'null');
}
export function setActiveMarkups(markups) { 
    activeMarkups = markups; 
    console.log('[STATE] activeMarkups updated:', Object.keys(activeMarkups));
}
export function setOpsMode(mode) {
    if (mode !== 'execution' && mode !== 'planning') {
        console.warn('[STATE] Invalid opsMode ignored:', mode);
        return;
    }
    opsMode = mode;
    console.log('[STATE] opsMode set to:', opsMode);
}

export function getIsManualMode() { return isManualMode; }
export function getCurrentQuoteData() { return currentQuoteData; }
export function getSelectedFile() { return selectedFile; }
export function getCurrentDbId() { return currentDbId; }
export function getCurrentGenesisHash() { return currentGenesisHash; }
export function getOpsMode() { return opsMode; }

// Tag Helpers
export function addTag(tagName, weight = 1.0) {
    selectedTags.add(tagName);
    tagWeights[tagName] = weight;
}

export function removeTag(tagName) {
    selectedTags.delete(tagName);
    delete tagWeights[tagName];
}

export function toggleTraveler(travelerName) {
    if (selectedTravelers.has(travelerName)) {
        selectedTravelers.delete(travelerName);
    } else {
        selectedTravelers.add(travelerName);
    }
}

// Clear all tags (for new quote)
export function clearAllTags() {
    selectedTags.clear();
    tagWeights = {};
    // Note: Don't clear activeMarkups - those are the available tags from backend
    console.log('🧹 All pricing tags cleared');
}

// Clear all travelers (for new quote)
export function clearAllTravelers() {
    selectedTravelers.clear();
    console.log('🧹 All traveler tags cleared');
}

// Clear entire quote state (for new quote)
export function resetQuoteState() {
    currentQuoteData = null;
    selectedFile = null;
    currentDbId = null;
    currentGenesisHash = null;
    referenceImagePath = null;
    clearAllTags();
    clearAllTravelers();
    console.log('🔄 Quote state fully reset');
}
