---
doc_id: ui_reality_report
doc_type: context
status: active
version: 1.0
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [ui, reality, report, context]
---

# UI Reality Report (Factual Inventory)

## Entrypoints
- UI entrypoint: `/` renders `ops_layer/templates/index.html`.
  Evidence: `ops_layer/app.py` (2748-2749)

## Surfaces
- Sidebar navigation lists: Dashboard, New Quote, Parts Library, Customers, Configuration.
  Evidence: `ops_layer/templates/index.html` (27-67)
- Customers view exists as a dedicated page container.
  Evidence: `ops_layer/templates/index.html` (1521-1566)
- Parts Library and Configuration views are present in navigation but display a “Coming Soon” alert.
  Evidence: `ops_layer/static/js/modules/sidebar.js` (955-967)

## Actions
- Landing screen offers two choices: “I Have a 3D File” and “Manual Entry.”
  Evidence: `ops_layer/templates/index.html` (109-122)
- File mode supports drag/drop upload and a Calculate Quote button.
  Evidence: `ops_layer/templates/index.html` (156-169)
- Manual/Napkin mode offers a shape selector with multiple part shapes and dimension inputs.
  Evidence: `ops_layer/templates/index.html` (552-673)
- Quote context inputs include customer search, contact search, reference name, and quote ID.
  Evidence: `ops_layer/templates/index.html` (192-236)
- RFQ inputs include material, quantity, requested delivery date, price breaks, and target price.
  Evidence: `ops_layer/templates/index.html` (255-320)
- Customers view includes search and “Add Customer” button plus a table of customers.
  Evidence: `ops_layer/templates/index.html` (1522-1564)
- Sidebar quote history loads recent quotes, allows quote selection, and provides PDF/traveler actions.
  Evidence: `ops_layer/static/js/modules/sidebar.js` (220-276)

## Visible Signals
- “Market Intelligence” radar displays similar parts, median price, variance, and a status badge.
  Evidence: `ops_layer/templates/index.html` (414-444)
- Market Intelligence help modal contains guidance text and labeled SAFE/HIGH/LOW signals.
  Evidence: `ops_layer/templates/index.html` (446-483)
- “Pattern Detected (Guild Intelligence)” banner lists suggestions and confidence values.
  Evidence: `ops_layer/templates/index.html` (959-972), `ops_layer/static/js/modules/rfq.js` (386-467)
- Economics section shows a system anchor price and variance attribution controls.
  Evidence: `ops_layer/templates/index.html` (954-1037)

## Hidden/Absent Signals
- Parts Library and Configuration views are not implemented beyond an alert.
  Evidence: `ops_layer/static/js/modules/sidebar.js` (955-967)
- No dedicated Cutter Ledger or State Ledger UI surfaces are present in `index.html`.
  Evidence: `ops_layer/templates/index.html` (109-1569)

## Mode Evidence
- UI offers File Mode vs Manual Entry (Napkin Mode) as the primary mode selection.
  Evidence: `ops_layer/templates/index.html` (109-122)
- Ops mode state exists in client state with default `execution`, and is sent to API calls.
  Evidence: `ops_layer/static/js/modules/state.js` (17-47), `ops_layer/static/js/modules/api.js` (8-35)
- No UI control in `index.html` explicitly switches `ops_mode`.
  Evidence: `ops_layer/templates/index.html` (109-1569)

## Absence Visibility
- Unclosed quotes section shows “Age (days)” for quotes awaiting outcomes.
  Evidence: `ops_layer/templates/index.html` (125-145)

## Notes (Facts Only)
- The UI is single-page (`index.html`) with view switching handled in JavaScript.
  Evidence: `ops_layer/app.py` (2748-2749), `ops_layer/static/js/modules/sidebar.js` (66-88)
