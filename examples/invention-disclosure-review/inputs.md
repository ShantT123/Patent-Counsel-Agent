# Fictional disclosure — Lantern

All names and technical assertions below are fictional evaluation material.

## S-001 §1 — Architecture note

Our team calls the update-checking component Lantern. Each cache update carries a monotonically increasing generation number. A cache reader remembers the largest generation number it has accepted for a key and rejects an update carrying a smaller number. We call this behavior "don't let yesterday overwrite today". The cache is replicated across regions. We have not specified how generation numbers are assigned across regions or what happens after reader state is lost.

## S-001 §2 — Interview note

We call the record containing the key, value, and generation number a parcel. TTL appears on the diagram but nobody has defined the acronym in these materials. We have not measured latency or asserted novelty. The deployment is intended for a shopping-cart service; the update check itself does not depend on shopping carts.

## S-002 §1 — Intake context

No technology bucket list was attached. The attorney has not yet answered whether a list exists. No public research tools or external source pages are included in this fixture. This is a document-only fallback example, not a researched market report.
