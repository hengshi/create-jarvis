# Source Skills

Source skills help agents access and interpret company digital assets.

## When to create a source skill

Create or propose a source skill when a source is:
- repeatedly consulted,
- structurally important,
- confusing without guidance,
- or needed to unlock a high-value workflow.

Typical sources:
- docs and wiki systems
- issue trackers
- meeting notes / minutes
- customer feedback systems
- analytics or BI tools
- support systems
- incident records
- release notes or changelogs

## What a source skill should do

A strong source skill should tell an agent:
- why this source matters,
- how to access it,
- how to search it efficiently,
- how to interpret its structure or taxonomy,
- what kinds of tasks it is best for,
- where to write back if the source participates in the JARVIS loop,
- what freshness or access constraints matter,
- and what must be linked or summarized instead of copied.

## What a source skill should not do

It should not:
- duplicate the source content wholesale,
- pretend to be the source of truth if it is only a router,
- hardcode company details without labeling them as company-specific,
- or persist secret values, private exports, or raw records in JARVIS.

## Minimum useful structure

For each important source, try to capture:
- source name
- source type
- owner
- access path
- auth or tool expectations
- search / navigation strategy
- routing rules
- update triggers
- constraints or caveats
- redaction boundary
- freshness expectation

## Dump prevention

Source skills route to source truth. They do not move the source into JARVIS. Keep raw docs, issues, transcripts, tickets, analytics exports, or customer records in the owning source unless there is an explicit approved export boundary.

## Quality bar

A source skill is useful when a new agent can read it and immediately know:
- whether this source is relevant,
- how to get to the right material quickly,
- and how to avoid wasting time or misreading the source.
