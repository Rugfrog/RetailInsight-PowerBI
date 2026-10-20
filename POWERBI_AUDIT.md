# RetailInsight Power BI audit — 20 October 2026

Status: **source repairs; runtime validation and deployment pending**.
Baseline: `693bfdd1bbcd94041ee1157e8f00da437f46dac9` on `main`.

## Existing implementation

The baseline contains one report page with 30 native Power BI objects: five KPI cards, four slicers, a line chart, a map, a feedback table, a response-volume bar chart, and text labels including happy/neutral/sad sentiment faces. It is a recoverable PBIP/PBIR/TMDL project. There is no reason to rebuild it from scratch.

The semantic model originally had one imported table, nine measures, a self-contained deterministic Power Query generator, and an empty relationships file. No imported data cache or published report URL is included. The GitHub Pages site is a separate HTML/JavaScript demonstration.

## Repairs in this branch

- Sentiment counts now intersect the selected sentiment using `KEEPFILTERS`, rather than replacing it. With only Negative selected, Positive and Neutral counts should be zero and Negative should represent 100% of selected responses. Empty subsets return zero counts; percentages remain blank when there are no responses.
- Added Calendar and Store tables and two many-to-one relationships to Feedback, with default single-direction filtering from dimensions to fact. Calendar covers the full calendar year containing the fixture. Month sorts by month number. The imported Feedback query remains the source of the fixture; dimension queries derive from it without a fact-to-dimension query dependency.
- Bound geographical visuals/slicers to Store and the year/trend fields to Calendar. Original fact columns remain for compatibility.
- Added week and county/council-area dropdown slicers, bringing the report to 34 native objects. The week convention is **Monday start, calendar year**, using `Date.WeekOfYear`; it is **not ISO week-year**. The location label accommodates Scotland, Wales and Northern Ireland rather than representing all subdivisions as English counties.
- Added ResponseID to the feedback table so equal displayed values do not collapse separate responses.
- Corrected the static sample-period label to the actual last fixture date, 29 September 2024. It describes the dataset coverage, not the current filter selection.
- Preserved sentiment faces and the existing HTML demo.

## Verification performed

`tools/validate_project.py` validates all 41 project/report JSON documents against the Microsoft schemas named in those files, resolves visual column/measure references against the TMDL source, and checks objects fit the 1440×810 canvas. All passed on 20 October 2026.

An independent Python reproduction of the existing generator yields:

| Metric | Expected unfiltered value |
| --- | ---: |
| Responses | 7,250 |
| Stores | 20 |
| Distinct response dates | 273 |
| Earliest response | 1 January 2024 |
| Latest response | 29 September 2024 |
| Positive responses | 5,167 |
| Neutral responses | 1,161 |
| Negative responses | 922 |
| Positive % | 71.3% |
| Neutral % | 16.0% |
| Negative % | 12.7% |

These are **fixture expectations, not query results from Power BI**. JSON schema validation does not execute TMDL, M or DAX and does not validate visual-specific formatting behavior.

Run static checks with Python 3.12+ and `jsonschema` 4.x:

```powershell
python tools/validate_project.py
```

The first run downloads official Microsoft schemas; subsequent runs use `.schema-cache`. The optional first argument chooses another cache directory.

## Open work before release

1. Open the PBIP in current Power BI Desktop, apply/refresh queries, and verify TMDL loading, relationships, totals and percentage calculations. No runtime success has been observed yet.
2. Test no selection, each sentiment, multiple sentiments, region/county/city combinations, year/week selections, empty weeks, and clearing selections. Check both cards and cross-visual interactions against the same filtered rows.
3. Verify the map renders in the intended tenant and in Publish to web. Map permissions/provider support are unverified. Check point grouping and colours rather than inferring correctness from coordinates alone.
4. Verify actual dropdown behavior and tab order in Power BI. Static canvas checks cannot establish readability or keyboard usability. Tune the restrained existing layout after viewing it in the renderer.
5. Add a supported comment-search experience. The current feedback table is **not yet a searchable table**.
6. Replace the response-volume bar chart with a clearly defined store-performance ranking (for example positive rate plus response count and minimum sample size). Response volume alone is not service performance.
7. Improve the synthetic fixture's realism if useful: its modular formulas produce repetitive comments and do not explicitly model seasonal/store-level sentiment patterns. Preserve determinism and update expected totals deliberately.
8. Review date semantics before extending to multiple years; adopt ISO year/week together if required. Mark/validate the date table in Desktop before adding time-intelligence measures. The fixture currently has one year only.
9. Publish only after Desktop checks pass, then repeat representative filter tests in the Service. Capture genuine report screenshots after verification.

## Access and deployment route

The Microsoft Power BI plugin was observed installed and enabled. It is a **local browser workflow**, not an authenticated deployment API. The available browser reached the Power BI work/school-email sign-in page; no workspace, account, tenant, or licence has been verified. No deployment was attempted and no subscription/trial was started.

The most direct route is current Power BI Desktop → open and validate this PBIP → publish to the owner's My workspace → verify in Power BI Service → create a Publish to web code if tenant policy allows → verify the anonymous report → embed it at the existing GitHub Pages URL. Keep `docs/index.html` intact until the actual report has passed those checks. Desktop publishing can publish a PBIP through a temporary PBIX; GitHub Pages cannot render project source.

Microsoft documents free licences for personal work in My workspace, and Publish to web from My workspace requires a Power BI licence; other workspaces require Pro/PPU. Public viewers need no licence. This is the first route to assess before buying capacity or Pro. Eligibility and tenant policy must be verified in the actual account.

A consumer Microsoft account alone is not the documented work/school signup route. Microsoft's signup guidance points people without a work/school address to a Microsoft 365 trial to establish an account. Do not start a trial or accept subscription terms automatically; first check whether the owner already has a suitable business tenant/account. Trial expiry and any ongoing tenant/account cost need review before selecting that route.

Fabric Git integration or `fabric-cicd` can be evaluated later when a suitable workspace and identity are available. The presence of item folders alone is not proof of sync/deployment readiness, and this repository has no `.platform` metadata. Do not buy Fabric capacity solely to render this small public portfolio report.

Official references checked 20 October 2026:

- [Power BI projects and publishing](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [Publish to web prerequisites and limitations](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-publish-to-web)
- [Individual signup](https://learn.microsoft.com/en-us/power-bi/fundamentals/service-self-service-signup-purchase-for-power-bi)
- [Free user capabilities](https://learn.microsoft.com/en-us/power-bi/fundamentals/end-user-features)

## Preservation

The baseline is retained on `main`; changes are isolated on `codex/powerbi-model-repairs`. A complete local Git bundle of baseline history was created and verified before editing. The website was not changed. Keep this branch in draft until actual Power BI runtime checks have passed.
