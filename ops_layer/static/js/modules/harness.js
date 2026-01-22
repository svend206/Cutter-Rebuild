let currentMode = "execution";

const modeCurrent = document.getElementById("mode-current");
const modeRadios = document.querySelectorAll("input[name='ops-mode']");
const modePanels = document.querySelectorAll("[data-mode]");

function setMode(mode) {
    currentMode = mode;
    if (modeCurrent) {
        modeCurrent.textContent = mode;
    }
    modePanels.forEach((panel) => {
        const requiredMode = panel.getAttribute("data-mode");
        panel.style.display = requiredMode === mode ? "block" : "none";
    });
}

modeRadios.forEach((radio) => {
    radio.addEventListener("change", (event) => {
        setMode(event.target.value);
    });
});

setMode(currentMode);

function apiFetch(url, options = {}) {
    const headers = options.headers || {};
    headers["X-Ops-Mode"] = currentMode;
    if (options.body && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }
    return fetch(url, { ...options, headers });
}

function showResult(targetId, payload) {
    const target = document.getElementById(targetId);
    if (!target) return;
    target.textContent = JSON.stringify(payload, null, 2);
}

function requireMode(expected, targetId) {
    if (currentMode !== expected) {
        showResult(targetId, { error: `Requires ops_mode ${expected}` });
        return false;
    }
    return true;
}

function parseJsonInput(value, fieldName) {
    if (!value) return null;
    try {
        return JSON.parse(value);
    } catch (error) {
        throw new Error(`${fieldName} must be valid JSON`);
    }
}

document.getElementById("ops-action-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!requireMode("execution", "ops-action-result")) return;

    const subjectRef = document.getElementById("ops-subject-ref").value.trim();
    const carrier = document.getElementById("ops-carrier").value.trim();
    const eventDataRaw = document.getElementById("ops-event-data").value.trim();

    try {
        const payload = { subject_ref: subjectRef };
        if (carrier) payload.carrier = carrier;
        if (eventDataRaw) {
            payload.event_data = parseJsonInput(eventDataRaw, "event_data");
        }

        const response = await apiFetch("/ops/carrier_handoff", {
            method: "POST",
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        showResult("ops-action-result", data);
    } catch (error) {
        showResult("ops-action-result", { error: error.message });
    }
});

document.getElementById("cutter-events-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!requireMode("planning", "cutter-events-result")) return;

    const subjectRef = document.getElementById("cutter-subject-ref").value.trim();
    const eventType = document.getElementById("cutter-event-type").value.trim();
    const limit = document.getElementById("cutter-limit").value.trim();

    const params = new URLSearchParams();
    if (subjectRef) params.append("subject_ref", subjectRef);
    if (eventType) params.append("event_type", eventType);
    if (limit) params.append("limit", limit);

    const response = await apiFetch(`/api/cutter/events?${params.toString()}`, { method: "GET" });
    const data = await response.json();
    showResult("cutter-events-result", data);
});

document.getElementById("state-declaration-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!requireMode("planning", "state-declaration-result")) return;

    const payload = {
        entity_ref: document.getElementById("state-entity-ref").value.trim(),
        scope_ref: document.getElementById("state-scope-ref").value.trim(),
        actor_ref: document.getElementById("state-actor-ref").value.trim(),
        declaration_kind: document.getElementById("state-declaration-kind").value,
        state_text: document.getElementById("state-text").value.trim()
    };

    const cutterEvidenceRef = document.getElementById("state-evidence-ref").value.trim();
    const evidenceRefsRaw = document.getElementById("state-evidence-refs").value.trim();
    const supersedesIdRaw = document.getElementById("state-supersedes-id").value.trim();

    if (cutterEvidenceRef) payload.cutter_evidence_ref = cutterEvidenceRef;
    if (evidenceRefsRaw) {
        try {
            const parsed = parseJsonInput(evidenceRefsRaw, "evidence_refs");
            if (!Array.isArray(parsed)) {
                throw new Error("evidence_refs must be a JSON array");
            }
            payload.evidence_refs = parsed;
        } catch (error) {
            showResult("state-declaration-result", { error: error.message });
            return;
        }
    }
    if (supersedesIdRaw) payload.supersedes_declaration_id = Number(supersedesIdRaw);

    const response = await apiFetch("/api/state/declarations", {
        method: "POST",
        body: JSON.stringify(payload)
    });
    const data = await response.json();
    showResult("state-declaration-result", data);
});

document.getElementById("state-list-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!requireMode("planning", "state-list-result")) return;

    const entityRef = document.getElementById("state-list-entity-ref").value.trim();
    const scopeRef = document.getElementById("state-list-scope-ref").value.trim();
    const actorRef = document.getElementById("state-list-actor-ref").value.trim();
    const limit = document.getElementById("state-list-limit").value.trim();

    const params = new URLSearchParams();
    if (entityRef) params.append("entity_ref", entityRef);
    if (scopeRef) params.append("scope_ref", scopeRef);
    if (actorRef) params.append("actor_ref", actorRef);
    if (limit) params.append("limit", limit);

    const response = await apiFetch(`/api/state/declarations?${params.toString()}`, { method: "GET" });
    const data = await response.json();
    showResult("state-list-result", data);
});

document.getElementById("reconcile-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!requireMode("planning", "reconcile-result")) return;

    const payload = {
        scope_ref: document.getElementById("reconcile-scope-ref").value.trim(),
        scope_kind: document.getElementById("reconcile-scope-kind").value,
        predicate_ref: document.getElementById("reconcile-predicate-ref").value.trim(),
        actor_ref: document.getElementById("reconcile-actor-ref").value.trim()
    };

    const predicateText = document.getElementById("reconcile-predicate-text").value.trim();
    if (predicateText) payload.predicate_text = predicateText;

    const response = await apiFetch("/api/reconcile", {
        method: "POST",
        body: JSON.stringify(payload)
    });
    const data = await response.json();
    showResult("reconcile-result", data);
});

document.getElementById("reconcile-list-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!requireMode("planning", "reconcile-list-result")) return;

    const scopeRef = document.getElementById("reconcile-list-scope-ref").value.trim();
    const scopeKind = document.getElementById("reconcile-list-scope-kind").value.trim();
    const predicateRef = document.getElementById("reconcile-list-predicate-ref").value.trim();
    const actorRef = document.getElementById("reconcile-list-actor-ref").value.trim();
    const limit = document.getElementById("reconcile-list-limit").value.trim();

    const params = new URLSearchParams();
    if (scopeRef) params.append("scope_ref", scopeRef);
    if (scopeKind) params.append("scope_kind", scopeKind);
    if (predicateRef) params.append("predicate_ref", predicateRef);
    if (actorRef) params.append("actor_ref", actorRef);
    if (limit) params.append("limit", limit);

    const response = await apiFetch(`/api/reconcile?${params.toString()}`, { method: "GET" });
    const data = await response.json();
    showResult("reconcile-list-result", data);
});

document.getElementById("refusal-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!requireMode("planning", "refusal-result")) return;

    const payload = {
        query_ref: document.getElementById("refusal-query-ref").value.trim(),
        actor_ref: document.getElementById("refusal-actor-ref").value.trim()
    };
    const queryText = document.getElementById("refusal-query-text").value.trim();
    if (queryText) payload.query_text = queryText;

    const response = await apiFetch("/api/query/refusal", {
        method: "POST",
        body: JSON.stringify(payload)
    });
    const data = await response.json();
    showResult("refusal-result", data);
});

document.getElementById("refusal-load-events").addEventListener("click", async () => {
    if (!requireMode("planning", "cutter-events-result")) return;
    const queryRef = document.getElementById("refusal-query-ref").value.trim();
    if (!queryRef) {
        showResult("cutter-events-result", { error: "query_ref is required" });
        return;
    }
    document.getElementById("cutter-subject-ref").value = `query:${queryRef}`;
    const params = new URLSearchParams();
    params.append("subject_ref", `query:${queryRef}`);
    const response = await apiFetch(`/api/cutter/events?${params.toString()}`, { method: "GET" });
    const data = await response.json();
    showResult("cutter-events-result", data);
});

