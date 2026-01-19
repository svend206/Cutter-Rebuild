/**
 * stock.js - Commercial Stock Size Management
 * 
 * "The Bob Reality Check" - Snaps dimensions to actual purchasable stock sizes
 * from suppliers like McMaster-Carr, OnlineMetals, etc.
 */

// Standard plate/bar thicknesses (inches) - Common industrial sizes
const STANDARD_THICKNESSES = [
    0.0625,  // 1/16"
    0.125,   // 1/8"
    0.1875,  // 3/16"
    0.25,    // 1/4"
    0.375,   // 3/8"
    0.5,     // 1/2"
    0.625,   // 5/8"
    0.75,    // 3/4"
    1.0,     // 1"
    1.25,    // 1-1/4"
    1.5,     // 1-1/2"
    2.0,     // 2"
    2.5,     // 2-1/2"
    3.0,     // 3"
    4.0,     // 4"
    5.0,     // 5"
    6.0      // 6"
];

// Standard width/length sizes (inches)
// Most suppliers sell in 0.5" increments up to 12", then 1" increments
const STANDARD_WIDTHS = [
    0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0, 
    4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 
    10.5, 11.0, 11.5, 12.0, 13.0, 14.0, 15.0, 16.0, 18.0, 20.0, 
    24.0, 30.0, 36.0, 48.0
];

/**
 * Snap a dimension to the nearest commercial stock size (always rounds UP)
 * @param {number} dimension - The dimension to snap (inches)
 * @param {string} axis - 'x', 'y', or 'z' (z is typically thickness)
 * @returns {number} - Snapped dimension
 */
export function snapToStandardSize(dimension, axis = 'x') {
    if (!dimension || dimension <= 0) return 0;
    
    // Use thickness list for Z-axis, width list for X/Y
    const sizeList = (axis === 'z') ? STANDARD_THICKNESSES : STANDARD_WIDTHS;
    
    // Find the smallest standard size that is >= the required dimension
    // (Bob needs stock that FITS the part, so we always round UP)
    for (let i = 0; i < sizeList.length; i++) {
        if (sizeList[i] >= dimension) {
            return sizeList[i];
        }
    }
    
    // If larger than our biggest standard size, round up to nearest inch
    return Math.ceil(dimension);
}

/**
 * Snap all three dimensions of a stock envelope
 * @param {object} dims - {x, y, z}
 * @returns {object} - {x, y, z} with snapped values
 */
export function snapStockDimensions(dims) {
    // Sort dimensions to identify which is likely thickness (smallest = Z)
    const sorted = [
        { axis: 'x', val: dims.x },
        { axis: 'y', val: dims.y },
        { axis: 'z', val: dims.z }
    ].sort((a, b) => a.val - b.val);
    
    // Smallest dimension = thickness (use thickness list)
    // Larger two = width/length (use width list)
    return {
        x: snapToStandardSize(dims.x, (sorted[0].axis === 'x') ? 'z' : 'x'),
        y: snapToStandardSize(dims.y, (sorted[0].axis === 'y') ? 'z' : 'y'),
        z: snapToStandardSize(dims.z, (sorted[0].axis === 'z') ? 'z' : 'x')
    };
}

/**
 * Apply snapped dimensions to the DOM inputs with visual feedback
 * @param {object} snapped - {x, y, z}
 */
export function applySnappedDimensions(snapped) {
    const inputs = {
        x: document.getElementById('stock-x'),
        y: document.getElementById('stock-y'),
        z: document.getElementById('stock-z')
    };
    
    ['x', 'y', 'z'].forEach(axis => {
        const input = inputs[axis];
        if (!input) return;
        
        const oldValue = parseFloat(input.value);
        const newValue = snapped[axis];
        
        // Only update if changed
        if (Math.abs(oldValue - newValue) > 0.001) {
            input.value = newValue.toFixed(3);
            
            // Visual feedback: briefly flash orange to show it adjusted
            input.style.transition = 'background-color 0.3s ease';
            input.style.backgroundColor = '#ff660033'; // Light orange tint
            
            setTimeout(() => {
                input.style.backgroundColor = '';
            }, 600);
            
            console.log(`📏 Stock ${axis.toUpperCase()} adjusted: ${oldValue.toFixed(3)}" → ${newValue.toFixed(3)}" (standard size)`);
        }
    });
}

/**
 * Get recommended stock size for a part (with margin)
 * @param {object} partBbox - {x, y, z} part dimensions
 * @param {number} margin - Extra margin to add (default 0.1" = 100 thou)
 * @returns {object} - {x, y, z} recommended stock size
 */
export function recommendStockSize(partBbox, margin = 0.1) {
    return snapStockDimensions({
        x: partBbox.x + margin,
        y: partBbox.y + margin,
        z: partBbox.z + margin
    });
}

/**
 * Format dimension for display (fractional inches)
 * @param {number} decimal - Decimal inches
 * @returns {string} - e.g., "1-1/2" or "0.375"
 */
export function formatDimension(decimal) {
    // Common fractional equivalents
    const fractions = {
        0.0625: '1/16',
        0.125: '1/8',
        0.1875: '3/16',
        0.25: '1/4',
        0.375: '3/8',
        0.5: '1/2',
        0.625: '5/8',
        0.75: '3/4',
        0.875: '7/8'
    };
    
    const whole = Math.floor(decimal);
    const frac = decimal - whole;
    
    // Check if fractional part matches a common fraction
    const fracStr = fractions[parseFloat(frac.toFixed(4))];
    
    if (fracStr) {
        return whole > 0 ? `${whole}-${fracStr}"` : `${fracStr}"`;
    }
    
    return `${decimal.toFixed(3)}"`;
}

