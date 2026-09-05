---
name: dataverse-people-lookup
description: >-
  Look up a person's job title, office location, and reporting manager using
  the Dataverse MCP pipeline. Use when the user asks "Who is someone's
  manager?", "What is someone's title?", "Where is someone located?",
  "What does someone do?", or any people/employee/org-chart lookup query.
---

# Dataverse People Lookup

Answer people-related queries (title, location, manager) by driving the
four-step Dataverse MCP pipeline end-to-end.

## When to Use

- "What is [name]'s title, location, and manager?"
- "Who does [name] report to?"
- "Where is [name] based?"
- "What role does [name] have?"
- Any combination of the above for one or more people.

## Workflow

Use the `CallMcpTool` tool with `server: "user-DataverseMCP"` for every step.

### Step 1 — Identify the data product

```
toolName: identify_dataproducts
arguments: { "user_query": "<the user's question verbatim>" }
```

Inspect the returned list. Pick the first (most relevant) data product name
for the next step. If more than one data product is flagged (cross-domain),
follow the ordering instructions in the response.

### Step 2 — Shortlist tables

```
toolName: shortlist_tables
arguments: {
  "data_product": "<data product from Step 1>",
  "user_query": "<the user's question verbatim>"
}
```

The response is a list of table objects with `name`, `schema`, and
`description`. Save the full list for Step 3.

### Step 3 — Generate SQL

```
toolName: get_sql
arguments: {
  "data_product": "<data product from Step 1>",
  "tables_list": <table list from Step 2>,
  "user_query": "<the user's question verbatim>"
}
```

The response contains a `sql` field. Extract the SQL string for Step 4.

### Step 4 — Execute SQL

```
toolName: execute_sql
arguments: { "sql": "<SQL from Step 3>" }
```

The response contains `columns`, `data`, and `row_count`.

## Presenting Results

After Step 4, format the answer for the user:

- **Single person** — present as a short summary:

> **Jane Doe**
> - Title: Senior Data Engineer
> - Location: London
> - Manager: John Smith

- **Multiple people** — use a bullet list with the same structure per person.

- If any field is null or missing, say "Not available" instead of omitting it.

## Error Handling

- If Step 1 returns no data products, tell the user the query could not be
  mapped to a known data domain and ask them to rephrase.
- If Step 4 returns `row_count: 0`, tell the user no matching records were
  found and suggest checking the spelling of the person's name.
- If any step fails with an error, surface the `error` message to the user
  and suggest retrying or refining the query.

## Important Notes

- Always pass the user's original question as `user_query` — do not
  paraphrase or simplify it, because the downstream LLM uses it for context.
- Do **not** skip steps or call `execute_sql` directly for people lookups;
  the full pipeline ensures correct table selection and business-rule
  compliance.
- For follow-up questions ("What about their email?"), restart from Step 1 to
  ensure proper context is applied.
