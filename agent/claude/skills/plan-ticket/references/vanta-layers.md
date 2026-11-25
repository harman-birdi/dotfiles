# Vanta layers map (v0, 2026-11-25)

A running map of obsidian (Vanta's monorepo) as layers, top = what customers touch, bottom = where
it runs. Every plan copies the diagram below and marks the parts the work touches with
`class <id> hit` (changed) or `class <id> near` (read or depended on, not changed).

**This is a living file.** When a plan finds a part that is missing, misnamed or wrong, fix it here
in the same PR as the plan (or tell Harman), and add a line to the changelog at the bottom. Keep
node ids stable: plans refer to them.

Sources for v0: [Vanta Architecture](https://app.getguru.com/card/irpd9eyT/Vanta-Architecture) (Guru,
marked partly out of date), [Code Structure](https://app.getguru.com/card/TR4nAL8c/Code-Structure),
[Guide 1: Migrating a Fetcher to V2](https://app.getguru.com/card/T8xkE7Ac/Guide-1-Migrating-a-Fetcher-to-V2),
[Schemas in V2](https://docs.google.com/document/d/1HbzgXCwq1U9HLA2FrVj4NOst3dBYfcCHGPmBIKv_dos),
[Demo Domains Foundations](https://docs.google.com/document/d/1gp18uS9dDZ5xlmYVuCQmtNg5yZZBHUhRdRJ-EBd-ZQ8).
Paths are where to start looking, not guarantees. Code is the ground truth: check with Glob/Grep.

```mermaid
flowchart TB
  classDef hit fill:#ffe1d6,stroke:#d4502a,stroke-width:3px,color:#1d1b26
  classDef near fill:#fff4cc,stroke:#b08900,stroke-width:2px,color:#1d1b26
  classDef layer fill:none,stroke:#9a96a8,stroke-dasharray:4 3

  subgraph L1["1 · Customer surfaces"]
    direction LR
    webclient["Web app UI<br/>apps/web-client (React, Alpaca)"]
    trust["Trust Center"]
    pubapi["Public API + MCP"]
    agentapp["Vanta Agent<br/>(osquery on laptops)"]
  end

  subgraph L2["2 · API and auth"]
    direction LR
    web["web: GraphQL monolith<br/>apps/web"]
    authsvc["auth-service<br/>OAuth callbacks"]
    apisvc["api-service<br/>ad-hoc scoped calls"]
    osq["osquery-server / writer"]
  end

  subgraph L3["3 · Product logic"]
    direction LR
    domainpk["Domain packages<br/>packages/* (controls, policies, risk…)"]
    servercommon["server-common<br/>(wide waist: avoid adding)"]
    creds["Credentials and linking<br/>apps/web/src/credentials"]
  end

  subgraph L4["4 · Integrations and ingestion"]
    direction LR
    sched["task-scheduler<br/>queues fetches"]
    rfv1["Fetcher v1<br/>apps/resource-fetcher/src/specific-resources"]
    cdc["Fetcher v2 / CDC service<br/>apps/cloud-data-capture-service"]
    plugin["v2 plugin per vendor<br/>packages/cloud-data-capture-plugin-*"]
    conv["v2 → v1 converter<br/>sink-vanta-resource-converter"]
    mocks["Demo-domain mocks<br/>packages/mock-data-source"]
  end

  subgraph L5["5 · Evaluation"]
    direction LR
    oplog["oplog-watcher"]
    tests["test-runner<br/>Vanta tests"]
  end

  subgraph L6["6 · Notifications and jobs"]
    direction LR
    notif["notification + email jobs"]
    lambdas["Lambdas<br/>customer-lifecycle-manager…"]
  end

  subgraph L7["7 · Data"]
    direction LR
    mongo[("Mongo<br/>v1 resources, app data")]
    v2db[("v2 store + schema registry")]
    queues[("SQS / Kafka")]
    s3[("S3")]
  end

  subgraph L8["8 · Infra and delivery"]
    direction LR
    tf["Terraform · ECS Fargate"]
    cf["Cloudflare (web assets)"]
    ci["CI: Buildkite / GitHub"]
  end

  %% Layers stack top to bottom. Only same-layer arrows here, so each layer stays one row;
  %% how data moves between layers belongs in the plan's flow diagram, not this map.
  sched --> rfv1
  sched --> cdc
  cdc --> plugin --> conv
  oplog --> tests
  %% Invisible links keep each layer's boxes in one row.
  webclient ~~~ trust ~~~ pubapi ~~~ agentapp
  web ~~~ authsvc ~~~ apisvc ~~~ osq
  domainpk ~~~ servercommon ~~~ creds
  rfv1 ~~~ mocks
  notif ~~~ lambdas
  mongo ~~~ v2db ~~~ queues ~~~ s3
  tf ~~~ cf ~~~ ci
  L1 ~~~ L2 ~~~ L3 ~~~ L4 ~~~ L5 ~~~ L6 ~~~ L7 ~~~ L8
  class L1,L2,L3,L4,L5,L6,L7,L8 layer
```

## Node ids (use these with `class <id> hit|near`)

| Layer | Ids |
| --- | --- |
| 1 Customer surfaces | `webclient` `trust` `pubapi` `agentapp` |
| 2 API and auth | `web` `authsvc` `apisvc` `osq` |
| 3 Product logic | `domainpk` `servercommon` `creds` |
| 4 Integrations | `sched` `rfv1` `cdc` `plugin` `conv` `mocks` |
| 5 Evaluation | `oplog` `tests` |
| 6 Notifications | `notif` `lambdas` |
| 7 Data | `mongo` `v2db` `queues` `s3` |
| 8 Infra | `tf` `cf` `ci` |

## How a plan uses it

1. Copy the whole mermaid block into the plan's "Where this lands" section.
2. Add one line per affected node at the end: `class plugin,conv hit` and `class tests,mongo near`.
3. Under the diagram, one sentence per `hit` node: what changes there, with the file path you found.
4. If a part you need isn't on the map, add a node to the plan's copy, mark it `hit`, and list it
   under "Map updates" so the map gets fixed.

## Changelog

- 2026-11-25 v0: first cut from Guru and v2 docs (Harman + Claude). Not yet checked against the code.
