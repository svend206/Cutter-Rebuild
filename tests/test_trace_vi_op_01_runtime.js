// Scope note: This runtime test relies on repo-level ESM ("type": "module") in package.json.
// No additional tooling is introduced for TRACE-VI-OP-01.

import { initFailureDisclosure } from '../ops_layer/static/js/modules/failure_disclosure.js';
import { calculateManualQuote } from '../ops_layer/static/js/modules/manual.js';
import {
    validateManualQuoteInputs,
    MANUAL_QUOTE_FAILURE_CODES
} from '../ops_layer/static/js/modules/manual_validation.js';

function assert(condition, message) {
    if (!condition) {
        console.error(`FAIL: ${message}`);
        process.exit(1);
    }
}

function createClassList() {
    return {
        visible: false,
        add() {
            this.visible = true;
        },
        remove() {
            this.visible = false;
        }
    };
}

function createDisclosureTarget() {
    return {
        textContent: '',
        dataset: {},
        classList: createClassList(),
        addEventListener() {}
    };
}

function createInput(value = '') {
    return { value: `${value}` };
}

function bindDocument({ target, elementsById }) {
    global.document = {
        querySelectorAll(selector) {
            if (selector === '[data-failure-disclosure]') {
                return [target];
            }
            return [];
        },
        getElementById(id) {
            return elementsById[id] || null;
        }
    };
}

const target = createDisclosureTarget();
const elementsById = {};
bindDocument({ target, elementsById });

const unsubscribe = initFailureDisclosure({ autoDismissMs: 0 });

// Unit visibility check (event emission + disclosure handling)
const materialResult = validateManualQuoteInputs({ material: '', partVol: 1 });
assert(materialResult === false, 'material validation should refuse');
assert(
    target.dataset.failureCode === MANUAL_QUOTE_FAILURE_CODES.MISSING_MATERIAL,
    'missing material code should be emitted'
);
assert(
    target.textContent === 'input invalid: material is required',
    'disclosure should render missing material message'
);
assert(
    target.classList.visible === true,
    'disclosure should become visible'
);

// Point-of-use integration check (calculateManualQuote)
target.textContent = '';
target.dataset = {};
target.classList.visible = false;

Object.assign(elementsById, {
    'stock-x': createInput('1'),
    'stock-y': createInput('1'),
    'stock-z': createInput('1'),
    'material-select': createInput(''),
    'quantity-input': createInput('1'),
    'setup-time': createInput('60'),
    'shop-rate': createInput('75'),
    'handling-time': createInput('0.5'),
    'reference-name-input': createInput('Manual Quote'),
    'part-volume-error': { style: { display: 'none' } }
});

await calculateManualQuote();

assert(
    target.dataset.failureCode === MANUAL_QUOTE_FAILURE_CODES.MISSING_MATERIAL,
    'point-of-use failure should be emitted'
);
assert(
    target.dataset.failureScope === 'manual_quote',
    'point-of-use failure scope should be recorded'
);
assert(
    target.textContent === 'input invalid: material is required',
    'point-of-use disclosure should render message'
);
assert(
    target.classList.visible === true,
    'point-of-use disclosure should become visible'
);

unsubscribe();
