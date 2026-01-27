import { emitFailure } from './failure_events.js';

export const MANUAL_QUOTE_FAILURE_CODES = {
    MISSING_MATERIAL: 'MANUAL_QUOTE_MISSING_MATERIAL',
    MISSING_PART_VOLUME: 'MANUAL_QUOTE_MISSING_PART_VOLUME'
};

const FAILURE_MESSAGES = {
    [MANUAL_QUOTE_FAILURE_CODES.MISSING_MATERIAL]: 'input invalid: material is required',
    [MANUAL_QUOTE_FAILURE_CODES.MISSING_PART_VOLUME]:
        'input invalid: part volume missing (shape not configured)'
};

export function validateManualQuoteInputs({ material, partVol }) {
    if (!material) {
        emitFailure({
            code: MANUAL_QUOTE_FAILURE_CODES.MISSING_MATERIAL,
            scope: 'manual_quote',
            user_text: FAILURE_MESSAGES[MANUAL_QUOTE_FAILURE_CODES.MISSING_MATERIAL]
        });
        return false;
    }

    if (partVol === 0) {
        emitFailure({
            code: MANUAL_QUOTE_FAILURE_CODES.MISSING_PART_VOLUME,
            scope: 'manual_quote',
            user_text: FAILURE_MESSAGES[MANUAL_QUOTE_FAILURE_CODES.MISSING_PART_VOLUME]
        });
        return false;
    }

    return true;
}
