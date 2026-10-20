# RetailInsight — Customer Feedback Dashboard

Portfolio prototype using entirely fictional retail customer feedback data. There are **two different artifacts** in this repository.

## 1. Interactive browser demonstration

**[View the web demo](https://rugfrog.github.io/RetailInsight-PowerBI/)**

Hosted with GitHub Pages from [docs/index.html](docs/index.html). Includes functional filters, sentiment faces, trends, customer feedback tables and downloadable CSV. The browser demo is written in HTML/JavaScript — it is **not** a published Power BI report.

## 2. Editable Power BI project (PBIP)

The actual Power BI source files are committed in the repository:

- [RetailInsight.pbip](RetailInsight.pbip) — Power BI Desktop project entry point
- [RetailInsight.Report](RetailInsight.Report) — report visuals, layouts and definitions
- [RetailInsight.SemanticModel](RetailInsight.SemanticModel) — TMDL data model, queries and DAX measures

The source files have not been opened or runtime-validated in Power BI Desktop or the Power BI/Fabric service. They are an **untested first build**, not a verified deployed report.

See [the Power BI audit](POWERBI_AUDIT.md) for source repairs, static validation results, fixture totals, unresolved runtime checks and the deployment route. The repair branch adds Calendar/Store relationships, corrects sentiment-filter measures, and adds week/county slicers; these still require verification in Power BI.

The report now follows the owner's supplied design reference, with a dark sidebar, compact KPI panels, sentiment faces, native charts/map/tables, and two report pages. See [design implementation and reopen instructions](DESIGN_REFERENCE.md). The new design's Desktop rendering still needs verification.

### How to view the *real* Power BI report in a browser

GitHub Pages cannot directly render PBIP/PBIX files. Two options:

1. **Fabric Git integration** — in an eligible Microsoft Fabric workspace, connect this GitHub repository, sync the report and semantic model, refresh the model and open the report in the Fabric/Power BI browser UI. Your Fabric administrator must allow Git integration, and a supported workspace/capacity is required.
2. **Power BI Desktop / Service** — clone/download the project, open `RetailInsight.pbip` in Power BI Desktop, verify the report, then publish it to Power BI Service. From there you can use **Publish to web** for public embedding if your tenant allows it, since all data here is fictional.

For workspace Git sync, use the two item folders (`RetailInsight.Report`, `RetailInsight.SemanticModel`). There is no requirement for GitHub Pages to be enabled to sync report definitions.

## Portfolio representation

Describe this as a **fictional retail analytics demonstration**. Don't claim the HTML page is a deployed Power BI report, or that this repository contains confidential data from ASDA, Medallia, or other companies.

Copyright © repository owner. All rights reserved.
