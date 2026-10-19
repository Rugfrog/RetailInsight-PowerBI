# GitHub setup and browser preview

Create a new **public** GitHub repository called `RetailInsight-PowerBI`. Use public because GitHub Pages on free plans generally publishes from public repositories. There is no employer data here; all data is fictional.

Upload the *contents* of this project into the repository root; it includes:

- `RetailInsight.pbip` and its Report/SemanticModel folders (editable Power BI project; not yet verified in Desktop)
- `/docs/index.html`, `/docs/app.js`, `/docs/style.css`, `/docs/data.js`, `/docs/assets/uk-map.svg` (interactive web preview)

Then in repository **Settings → Pages → Build and deployment → Deploy from a branch**, choose branch **main**, directory **/docs**, and Save. Once deployment succeeds, the expected link will have the form:

`https://rugfrog.github.io/RetailInsight-PowerBI/`

Check that the page loads before sharing it. GitHub Pages may be disabled initially.

If you instead want the *actual* Power BI report interactive in a browser, you must first verify it in Power BI Desktop and publish to Power BI Service, then use the Power BI **Publish to web (public)** feature if your license and tenant administrator permit. Public publishing exposes the report data to anyone.
