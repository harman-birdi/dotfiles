---
name: integrations
description: Work on Vanta integrations (connectors) in the obsidian repo — new connectors, new resources or fields on an existing connector, sync bugs, or mock integrations for demos. Use when the task mentions an integration, connector, fetcher, IntBuilder, resource sync, or a third-party vendor API.
---

# Integration work in obsidian

## Before you write code

1. **Classify the task**, then tell me which one it is:
   - (a) new connector · (b) new resource or field on an existing connector · (c) sync bug ·
   (d) mock integration for a demo.
   - For (d), use the `mock-an-integration` and `generate-mock-data` skills from the
     `demo-domains` plugin, not this skill. See the Guru card "How to Mock an Integration".
2. **Find the platform** that the connector uses. New work should use the **new integration
   platform** (IntBuilder / fetcher v2). Legacy connectors on fetcher v1 cannot use IntBuilder.
   Confirm which platform applies from the code, and cite the file. Do not assume.
3. **Find a precedent.** Locate 1–2 existing connectors that solve a similar problem, such as the
   same auth type, pagination style, or resource type. Read them before you design anything. Follow
   their patterns unless I agree to diverge.
4. **Check the vendor API.** Note the auth method, the required scopes, the rate limits, the
   pagination, and the sandbox access. If there is no sandbox access, say so early. Procurement
   for a sandbox can take weeks.
5. **Write acceptance criteria.** They cover the resources and fields that sync, the expected counts
   on a fixture, and the Vanta tests that must pass or fail. Get my OK on them.

## Verifiers to use (cheapest first)

- Typecheck and lint for the touched packages.
- Unit tests for translation and mapping logic. Add property-style cases for empty, partial,
  and malformed vendor responses.
- **Recorded fixtures / contract tests** for vendor payloads. Never call live vendor APIs in tests.
- Snapshot or golden-file diffs of translated output when you change an existing connector.
- A preview environment walkthrough of the connect flow, if the UI changes. Attach screenshots.

Find the exact commands for each verifier in the repo: `package.json` scripts, `justfile`, or the
nearest `AGENTS.md`. Record what you found in the "Repo notes" section at the end of this file, so
the next session does not have to search again. Ask me before you edit this skill.

## Rules

- Ship behind a **feature flag**, scoped to the target customer(s), unless I say otherwise.
- Do not log credentials, tokens, or customer resource data.
- Changes to shared integration-platform primitives affect every connector. Stop and flag them.
  The Integration Platform team owns those primitives.
- A new connector, or a major change, needs the Integration Certification Review before launch.
  Remind me when the work gets close to done.

## PR description must include

The connector and platform version · the feature flag name · the verifiers that ran, with counts ·
what is *not* verified (for example, "live vendor API not exercised") · how AI was used.

## Repo notes (append as you learn; keep it short)

<!-- Example: - Run connector unit tests: `<command>` (found in <file>) -->
