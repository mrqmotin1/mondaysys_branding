# Mondaysys Branding

Frappe app that brands **MondayERP** sites (Frappe/ERPNext v15 and v16) with the Mondaysys identity.
Install it last on every site. MondayPOS Cloud adds it to every bench group and to every new site automatically.

| What | How (survives updates) |
|---|---|
| App names: ERPNext → **MondayERP**, Frappe HR → **Monday HR**, Frappe CRM → **Monday CRM**, Frappe → **Mondaysys** | `translations/en.csv` + wrappers on `frappe.apps.get_apps` / `change_log.get_versions` + `boot_session` |
| Logos, favicon, splash | `app_logo_url` / `website_context` hooks; assets in `public/images` |
| Login page and browser title | Website/System Settings `app_name`, re-applied on every `migrate` |
| "Powered by" credits | `public/css/mondaysys_branding.css` |

The app never overwrites a logo or site name that a customer set themselves.
Frappe and ERPNext are GPL-3.0; their licence and copyright notices remain in their code.
