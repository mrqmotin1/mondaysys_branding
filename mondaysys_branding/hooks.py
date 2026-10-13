app_name = "mondaysys_branding"
app_title = "Mondaysys Branding"
app_publisher = "MondaySys"
app_description = "Mondaysys branding for MondayERP sites"
app_email = "ops@mondaysys.com"
app_license = "mit"

IMG = "/assets/mondaysys_branding/images"

# Navbar / desk logo; this app is installed last, so its entry wins.
app_logo_url = f"{IMG}/mondaysys-icon.svg"

website_context = {
	"favicon": f"{IMG}/mondaysys-icon-32.png",
	"splash_image": f"{IMG}/mondaysys-logo.svg",
}

app_include_css = ["/assets/mondaysys_branding/css/mondaysys_branding.css"]
web_include_css = ["/assets/mondaysys_branding/css/mondaysys_branding.css"]

# Rename/re-logo apps in the desk boot data (v16 app sidebar, logo).
boot_session = "mondaysys_branding.branding.boot_session"

# Re-apply the runtime wrappers before every request (cheap, idempotent).
before_request = ["mondaysys_branding.branding.install_runtime_patches"]

# MondayPOS tile in the apps screen / switcher (POS Awesome doesn't ship one).
add_to_apps_screen = [
	{
		"name": "posawesome",
		"logo": f"{IMG}/mondaypos-icon.svg",
		"title": "MondayPOS",
		"route": "/app/posapp",
		"has_permission": "mondaysys_branding.branding.mondaypos_installed",
	}
]

# Re-assert DB-stored branding after install and every migrate (i.e. every site update).
after_install = "mondaysys_branding.branding.apply_site_branding"
after_migrate = "mondaysys_branding.branding.apply_site_branding"

# Wrap frappe.apps.get_apps / change_log.get_versions so app titles and logos are branded.
from mondaysys_branding.branding import install_runtime_patches  # noqa: E402

install_runtime_patches()
