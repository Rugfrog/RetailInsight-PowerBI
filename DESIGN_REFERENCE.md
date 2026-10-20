# Reference-led Power BI redesign

The owner's supplied screenshot defines the design: a 230px dark slate rail,
pale blue-grey canvas, five compact KPI panels with restrained coloured top
rules, a large sentiment line chart, UK store map, and aligned feedback/store
tables. The report canvas is 1600 × 1104 to match those proportions.

Implemented in the actual PBIR report, retaining the existing semantic model:

- Customer feedback overview with native KPI cards, line chart, map, response
  table, store summary table and a text input slicer bound to customer comments.
- Separate Store performance page with a detailed comparison table and positive
  sentiment bar chart. Native page-navigation buttons connect the two pages.
- Seven native dropdown slicers: year, week, sentiment, region, county/council
  area, city and channel. Their sync groups carry selections across both pages.
- Native Clear All Slicers action, rather than an inert illustrated button.
- Green, amber and red faces retained in the KPI rail and sidebar. Sidebar
  sentiment percentages are data-bound cards.
- Fixed 0–100% data-bar scales in the store tables, alternating table rows,
  explicit column widths, consistent Segoe UI typography and no shadows.
- Explicit registered custom theme plus reusable source generator at
  `tools/restyle_report.py` (requires Pillow).

The two registered PNGs contain **only decorative panels, rules and icons**.
They contain no metric values, charts, map, table records or filter values.
Those are all native Power BI visuals. Static labels are native textboxes.

Adaptations from the browser reference:

- The trend remains daily. No inactive Daily/Weekly/Monthly tabs were added.
- Use the native response table's ellipsis menu to export records; no false CSV
  action was drawn onto the report. Export availability depends on the host.
- Native tables scroll rather than imitating the HTML table's pagination.
- The UK map uses actual coordinates and tooltip measures. Map rendering is
  still subject to Power BI Desktop/tenant map permissions and provider support.
- County/council area remains available in addition to the reference's filters.
- Response ID remains in the detail table to preserve individual row identity.

Validation: 115 project/report JSON documents pass Microsoft's declared schemas;
field bindings, canvas bounds, registered-image references and page destinations
resolve. Microsoft's TMDL parser still loads three tables and two relationships.
No semantic-model or HTML-demo files changed in this redesign.

**Desktop render check pending.** Schema checks cannot prove typography,
formatting defaults, slicer/search interactions or map rendering. Close the
already-loaded report without saving over these external source edits, reopen
`RetailInsight.pbip`, refresh/apply the model if necessary, and inspect both pages.
In Desktop authoring mode, Ctrl+click activates navigation/action buttons.
The screenshots supplied by the owner are design references, not proof of the
new native report rendering.
