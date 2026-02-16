# Data Dictionary — `data/data.csv`

Unified dataset combining mortgage partner information from four Azerbaijani banks.
136 rows total. One row = one residential complex or partner project.

---

## Column Reference

| Column | Type | Description | Banks with data |
|--------|------|-------------|-----------------|
| `source` | string | Bank that lists this partner. One of: `PASHA Bank`, `ABB Home`, `Xalq Bank`, `BirBank` | All |
| `name` | string | Name of the residential complex or project. For BirBank, this is the complex name; falls back to developer name if complex name is absent. | All |
| `partner_name` | string | Developer or construction company responsible for the project. | BirBank only |
| `region` | string | City or region. Populated directly from source data where available. | BirBank, Xalq Bank |
| `address` | string | Full street address of the complex. | All (varies in completeness) |
| `phone` | string | Primary contact phone number. Format varies by source (some include short codes). | All |
| `email` | string | Contact email address. | BirBank only |
| `website` | string | Developer or project website URL. | All (varies in coverage) |
| `facebook` | string | Facebook page URL. | BirBank only |
| `instagram` | string | Instagram profile URL. | BirBank only |
| `logo_url` | string | URL of the complex or partner logo image. | All |
| `down_payment` | numeric (%) | Minimum required initial payment as a percentage of the property price. | PASHA Bank, BirBank |
| `annual_rate` | numeric (%) | Annual mortgage interest rate offered for this complex. | PASHA Bank, ABB Home, BirBank |
| `term` | numeric (years) | Maximum mortgage loan term in years. | PASHA Bank, ABB Home, BirBank |
| `min_loan_amount` | numeric (AZN) | Minimum mortgage loan amount. | BirBank only |
| `max_loan_amount` | numeric (AZN) | Maximum mortgage loan amount. | ABB Home, BirBank |
| `latitude` | float | Latitude coordinate of the complex location. | BirBank only |
| `longitude` | float | Longitude coordinate of the complex location. | BirBank only |

---

## Source-Specific Notes

### PASHA Bank (14 rows)
- Mortgage terms (`down_payment`, `annual_rate`, `term`) are listed per complex and may vary by project.
- No developer (`partner_name`) is listed — only the complex name.
- Address and phone sourced from the partner card on the bank's portal.

### ABB Home (8 rows)
- `annual_rate`, `down_payment`, and `term` reflect **product-level** terms, not project-level. All 8 rows share the same mortgage conditions because ABBHome publishes one mortgage product applying to all partner developers.
- No `region`, `email`, `facebook`, or `instagram` fields captured.
- `max_loan_amount` is populated (product-level cap).

### Xalq Bank (14 rows)
- No mortgage term fields are available (`down_payment`, `annual_rate`, `term` all empty). Xalq Bank's portal only lists partner contact information, not loan parameters.
- `region` is explicitly labelled per card (e.g. "Bakı", "Sumqayıt").
- `website` links may point to Instagram or other social profiles where no dedicated website exists.

### BirBank (100 rows)
- Most complete source. One row per residential complex; a single developer may appear across multiple rows.
- `down_payment` values observed: `15`, `20`, `30` (percent).
- `annual_rate` values observed: `5.0` (subsidised/social programme), `16.5` (standard commercial).
- `max_loan_amount` is almost universally `500000` AZN.
- `latitude`/`longitude` are the only geo-coordinates in the dataset and allow map-based analysis.
- `email`, `facebook`, `instagram` are populated only where the developer has provided them.

---

## Coverage Matrix

| Field | PASHA Bank | ABB Home | Xalq Bank | BirBank |
|-------|:---:|:---:|:---:|:---:|
| name | Yes | Yes | Yes | Yes |
| partner_name | — | — | — | Yes |
| region | — | — | Yes | Yes |
| address | Yes | Yes | Yes | Yes |
| phone | Yes | Yes | Yes | Yes |
| email | — | — | — | Partial |
| website | Partial | — | Yes | Partial |
| facebook | — | — | — | Partial |
| instagram | — | — | — | Partial |
| down_payment | Yes | Yes* | — | Yes |
| annual_rate | Yes | Yes* | — | Yes |
| term | Yes | Yes* | — | Yes |
| min_loan_amount | — | — | — | Yes |
| max_loan_amount | — | Yes | — | Yes |
| latitude / longitude | — | — | — | Yes |

*Product-level (same value for all ABB Home rows)
