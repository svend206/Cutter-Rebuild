import { onFailure } from './failure_events.js';

const DEFAULT_SELECTOR = '[data-failure-disclosure]';
const DEFAULT_AUTO_DISMISS_MS = 5000;
let isFailureDisclosureInitialized = false;
let activeUnsubscribe = null;

function findDisclosureTargets(selector = DEFAULT_SELECTOR) {
    if (typeof document === 'undefined') {
        return [];
    }

    return Array.from(document.querySelectorAll(selector));
}

function ensureDismissHandler(target) {
    if (!target || !target.addEventListener || !target.dataset) {
        return;
    }

    if (target.dataset.failureDismissBound === 'true') {
        return;
    }

    target.addEventListener('click', () => {
        if (target.classList && target.classList.remove) {
            target.classList.remove('visible');
        }
    });

    target.dataset.failureDismissBound = 'true';
}

export function buildFailureDisclosureHandler(target, { autoDismissMs = DEFAULT_AUTO_DISMISS_MS } = {}) {
    ensureDismissHandler(target);

    return (failure) => {
        if (!target) {
            return;
        }

        const message = failure?.user_text || 'Failure occurred.';
        target.textContent = message;

        if (target.dataset) {
            target.dataset.failureCode = failure?.code || '';
            target.dataset.failureScope = failure?.scope || '';
        }

        if (target.classList && target.classList.add) {
            target.classList.add('visible');
        }

        if (autoDismissMs && target.classList && target.classList.remove) {
            setTimeout(() => {
                target.classList.remove('visible');
            }, autoDismissMs);
        }
    };
}

export function registerFailureDisclosure({ selector, autoDismissMs } = {}) {
    const targets = findDisclosureTargets(selector);
    if (targets.length === 0) {
        return () => {};
    }

    const handlers = targets.map((target) =>
        buildFailureDisclosureHandler(target, { autoDismissMs })
    );

    const compositeHandler = (failure) => {
        handlers.forEach((handler) => handler(failure));
    };

    return onFailure(compositeHandler);
}

export function initFailureDisclosure({ selector, autoDismissMs } = {}) {
    if (isFailureDisclosureInitialized) {
        return activeUnsubscribe || (() => {});
    }

    isFailureDisclosureInitialized = true;
    activeUnsubscribe = registerFailureDisclosure({ selector, autoDismissMs });
    return activeUnsubscribe;
}
