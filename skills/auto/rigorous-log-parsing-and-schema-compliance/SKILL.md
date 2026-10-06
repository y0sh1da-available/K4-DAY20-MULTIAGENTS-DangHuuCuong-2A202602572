---
name: rigorous-log-parsing-and-schema-compliance
description: WHEN parsing structured/unstructured log files or generating triage JSON artifacts to ensure correct metadata headers, field transformations, and sorting rules.
---
- Include all mandatory top-level metadata and schema version keys in output JSON files.
- Transform service names according to normalization rules (e.g. lower-case with hyphens replaced by underscores).
- Sort aggregated event lists correctly across multiple keys (e.g. service name then timestamp ascending).
- Verify all parsed fields (levels, exceptions, repeat counts, UTC timestamps) against expected output structures.
