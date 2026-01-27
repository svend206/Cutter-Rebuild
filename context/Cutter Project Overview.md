---
doc_id: cutter_project_overview
doc_type: context
status: draft
version: 1.0
date: 2026-01-26
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [context, overview]
---

# The Cutter — Project Overview

## What This Is

The Cutter is a light ERP for small machine shops, paired with the Guild — a shop-only market intelligence network.

The ERP covers estimating, shop floor tracking, quality, and shipping. It exports to QuickBooks and does not include a financial module.

The Guild provides market intelligence that individual shops cannot see on their own: what other shops are paying for material, how lead times are shifting by capability, and how much competitive attention a given geometry is receiving.

Together, the Cutter and the Guild reduce information asymmetry and preserve operational reality.

## Who It’s For

The Cutter is built for small to mid-sized contract machine shops, below a size threshold still to be defined.

It is designed for shops that:

- run on legacy ERP systems that feel heavy, slow, and brittle,
- operate on spreadsheets, whiteboards, paper travelers, and tribal knowledge,
- or rely heavily on gut instinct and verbal updates.

It is for owners who have experienced the gap between what they hear in meetings and what is actually happening on the floor, and for estimators who must price work without visibility into the market they are competing in.

## Why It Exists

Two structural problems drive this project.

### 1. Information Asymmetry

When a shop quotes a job, the buyer already knows the competitive landscape — they solicited multiple quotes. The shop does not.

The shop does not know:

- how many other shops are quoting the same part,
- whether its material pricing is competitive,
- or whether its promised lead time is realistic given current market conditions.

The Guild exists to give shops access to the same category of information buyers already possess.

### 2. The Thermocline of Truth

In any organization with distributed groups, information is synthesized as it moves upward. Details become summaries. Summaries become narratives.

By the time information reaches the person who must live with the consequences of a decision, the underlying operational reality may be inaccessible.

The Cutter exists to ensure that decision-makers retain direct access to demonstrated operational reality — not just their agents’ interpretations of it.

## Core Philosophy: Physics Over Reports

The thermocline exists because work and recording are separate acts. The gap between doing and documenting is where interpretation enters and reality degrades.

The Cutter closes that gap by making physical state the primary source of operational truth. Software does not ask what happened. It observes what is happening.

To conceal a delay, work would have to be physically concealed. To misrepresent utilization, observation would have to be defeated. Software does not decide what is true; it records what physics makes unavoidable.

The map is continuously constrained by the territory.

## The Operating System: Four Physical Constraints

Complex ERP modules are replaced with simple, finite, physical logic.

### Scheduling — The Dentist Appointment Model

Machine time is treated like a dentist’s chair. Capacity is finite.

Time slots are sold explicitly. If a slot is full, it cannot be booked. There is no algorithmic reshuffling of hundreds of jobs to preserve the illusion of flexibility.

When capacity is unavailable, the system refuses the booking.

Each refusal is recorded as a Capacity Refusal Event — a durable fact that demand exceeded supply at a specific moment.

These refusals become assets:

- Internally, they justify capital investment and hiring.
- At the Guild level, aggregated refusal signals reveal market tightness before prices move.

### Inventory — The Visual Supermarket Model

Inventory management focuses on emptiness, not counts.

Standard stock uses a two-bin system. When the first bin is empty, it triggers replenishment. If the bin is not empty, there is enough inventory.

This removes counting friction and eliminates false precision.

### Workflow — The Painted Floor Model

Floor space is the primary constraint.

Each machine queue is represented by a painted square sized to fit a fixed number of carts. If the square is full, upstream production must stop.

Bottlenecks become physically undeniable, forcing resolution instead of concealment in reports.

### Costing — The Shop Rate Blending Model

The system does not optimize around profit per part.

Total shop cost is compared to total invoiced hours. The business sells machine time plus material. If the blended hourly rate covers overhead, the shop is profitable.

Granular per-part accounting is replaced with business-level reality.

## The Observation Layer (Mobile-First, Hardware-Optional)

The Cutter observes the shop. Operators do not log events.

### Day One: The Phone as Sensor

On day one, observation is mobile-first.

Machines have QR codes.

Jobs have tagged travelers.

Operators scan to claim active work.

The phone’s presence establishes location.

The camera captures physical state when required.

This is physical observation, not abstract data entry. The human with a phone is the most resilient sensor in the system.

This approach enables immediate adoption and supports the Coffee Break Handoff.

### Day One Hundred: Hardware as Augmentation

As shops mature, hardware sensors can be added:

- current clamps for spindle activity,
- BLE beacons for automatic location,
- fixed cameras for status detection.

Hardware reduces friction but is never a prerequisite. Observation improves progressively without blocking adoption.

The system favors resilience over purity.

## What Humans Still Enter

Physics captures the shop floor. Three surfaces require human input, each entered by someone with a direct business incentive to be accurate.

- Estimating: quotes, assumptions, labor estimates, and lead-time promises. Genesis hash events fire here, feeding the Guild.
- Purchasing: material orders, pricing, and receipts.
- Shipping: what shipped, to whom, and when.

When a traveler is created, it is bound to a specific tag. From that moment forward, observation tracks the job through the shop.

## Operator Anonymity

The system does not record operator identity at the operation level.

This is not a privacy feature. It is a data integrity constraint.

Once data can be used to rank, compare, or punish individuals, it becomes strategically manipulated. Manipulated data is useless.

By removing attribution, the system preserves signal quality. Accountability remains a human responsibility, enforced socially and managerially — not algorithmically.

## State, Time, and Visual Decay

Operational states exist only through explicit affirmation.

Every state carries a timestamp. As time passes without reaffirmation, certainty decays.

The interface reflects this decay visually:

- colors desaturate,
- edges soften,
- surfaces weather.

This decay represents age, not severity. Nothing flashes. Nothing alarms.

To restore certainty, a human must explicitly reaffirm the state.

Time is made visceral without judgment.

## Shipping as Defensive Evidence

Shipping is not just logistics. It is custody transfer.

The Shipping module is an Evidence Generator.

To generate a shipping label, the system requires:

- a pack-out photo,
- a recorded weight,
- a timestamp,
- and carrier identification.

These elements are combined into a Defensive Packet: an immutable record of the physical state at handoff.

When disputes arise, the shop does not argue. It sends the packet.

Reality is portable.

## What Makes It Different

The Guild takes sides. It explicitly serves machine shops. Buyers and suppliers are not constituents.

Operational data is treated like financial data. Events are recorded immutably and are not smoothed, overwritten, or quietly edited.

Refusals are first-class facts. Constraints and impossibilities are preserved as evidence.

Interpretation remains human work. The system assigns no priority, generates no alerts, and declares no health.

Adoption takes ten minutes. The Coffee Break Handoff allows a shop to go live mid-week:

- open jobs and WIP are imported,
- work is bound to tags,
- legacy becomes read-only,
- new reality is observed immediately.

There is no parallel run, no operator training shutdown, and no big-bang reconciliation.

## How It’s Used

Estimators work at computers, pricing jobs with Guild intelligence and historical context.

Operators move carts, run machines, and make parts. They do not interact with the system.

Owners define standing queries and review them on their cadence. Time-in-condition accumulates without interpretation.

## The Guild

The Guild is a shop-only market intelligence network.

Genesis hash intelligence shows how many other shops are quoting the same geometry.

Material pricing reflects what shops are actually paying.

Lead-time distributions show realistic delivery expectations by capability.

Capacity refusal aggregates show where demand exceeds supply.

Access is restricted to shops. Customers and suppliers cannot see Guild intelligence. This asymmetry is intentional.

## The Competitive Landscape

JobBOSS, E2, and M1 are feature-complete and heavy. Their data is used for benchmarking, not competitive intelligence.

ProShop is modern and opinionated but lacks network intelligence.

Paperless Parts operates at the estimating layer and analyzes geometry, but taking the side of shops would structurally conflict with its neutral positioning.

Spreadsheets and whiteboards remain the true incumbent.

## Why the Cutter Wins

The Cutter’s moat is political, not technical.

Taking the side of shops constrains addressable market but unlocks intelligence competitors cannot deploy without breaking their positioning.

The observation-first architecture cannot be retrofitted. Competing systems rely on negotiated human input with unknown levels of delay, gaming, and omission. The Cutter’s data is grounded in observed physical reality.

## What Victory Looks Like

Year one: Adoption driven by zero operator burden and immediate quoting value.

Year three: Guild density makes market intelligence indispensable. Pricing blind becomes a liability.

Year five: A shop changes hands. Operational history is audited with the same rigor as financials. Reality itself becomes an asset.
