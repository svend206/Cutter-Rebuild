const failureListeners = new Set();
const FAILURE_HANDLER_EXCEPTION_CODE = 'FAILURE_HANDLER_EXCEPTION';
const FAILURE_DISCLOSURE_SELECTOR = '[data-failure-disclosure]';
let isEmittingHandlerFailure = false;
let isRenderingFallbackFailure = false;

export function emitFailure({ code, scope, user_text }) {
    const event = {
        code,
        scope,
        user_text,
        timestamp: new Date().toISOString()
    };

    failureListeners.forEach((handler) => {
        try {
            handler(event);
        } catch (error) {
            console.error('[FAILURE_EVENT_HANDLER_ERROR]', error);
            emitHandlerFailure(error);
            renderFailureFallback(error);
        }
    });

    return event;
}

function emitHandlerFailure(error) {
    if (isEmittingHandlerFailure) {
        console.error('[FAILURE_EVENT_HANDLER_REENTRANT]', error);
        return;
    }

    isEmittingHandlerFailure = true;
    try {
        emitFailure({
            code: FAILURE_HANDLER_EXCEPTION_CODE,
            scope: 'system',
            user_text: `failure handler exception: ${error?.message || 'unknown error'}`
        });
    } finally {
        isEmittingHandlerFailure = false;
    }
}

function renderFailureFallback(error) {
    if (isRenderingFallbackFailure) {
        console.error('[FAILURE_FALLBACK_REENTRANT]', error);
        return;
    }

    if (typeof document === 'undefined') {
        return;
    }

    isRenderingFallbackFailure = true;
    try {
        const targets = Array.from(document.querySelectorAll(FAILURE_DISCLOSURE_SELECTOR));
        if (targets.length === 0) {
            return;
        }

        const message = `failure handler exception: ${error?.message || 'unknown error'}`;
        targets.forEach((target) => {
            if (!target) {
                return;
            }

            target.textContent = message;
            if (target.dataset) {
                target.dataset.failureCode = FAILURE_HANDLER_EXCEPTION_CODE;
                target.dataset.failureScope = 'system';
            }
            if (target.classList && target.classList.add) {
                target.classList.add('visible');
            }
        });
    } catch (fallbackError) {
        console.error('[FAILURE_FALLBACK_ERROR]', fallbackError);
    } finally {
        isRenderingFallbackFailure = false;
    }
}

export function onFailure(handler) {
    failureListeners.add(handler);
    return () => failureListeners.delete(handler);
}
