"""Mondaysys branding that survives app and site updates.

Everything is applied at runtime from this app's code (hooks, translations, wrappers) or
re-applied on every migrate, so upgrading ERPNext/Frappe/HRMS/CRM never undoes it.
Settings a customer changed themselves (e.g. their own logo) are left alone.
"""

import frappe

IMG = "/assets/mondaysys_branding/images"
ICON = f"{IMG}/mondaysys-icon.svg"
LOGO = f"{IMG}/mondaysys-logo.svg"
FAVICON = f"{IMG}/mondaysys-icon-32.png"
MONDAYPOS_ICON = f"{IMG}/mondaypos-icon.svg"

# app name -> (title, logo or None to keep the app's own icon)
APPS = {
	"frappe": ("Mondaysys Framework", ICON),
	"erpnext": ("MondayERP", ICON),
	"hrms": ("Monday HR", None),
	"crm": ("Monday CRM", None),
	"posawesome": ("MondayPOS", MONDAYPOS_ICON),
	"ury": ("MondayPOS Restaurant", None),
	"mondaypos_restaurant": ("MondayPOS Restaurant Custom", None),
}

# Values that are "ours" or upstream defaults, so they may be replaced on migrate.
REPLACEABLE_LOGOS = {
	None,
	"",
	ICON,
	LOGO,
	"/assets/erpnext/images/erpnext-logo.svg",
	"/assets/erpnext/images/erpnext-logo-blue.png",
	"/assets/frappe/images/frappe-framework-logo.svg",
	"/assets/frappe/images/frappe-favicon.svg",
	"/assets/hrms/images/frappe-hr-logo.svg",
}
REPLACEABLE_NAMES = {None, "", "Frappe", "ERPNext", "Frappe HR", "MondayERP", "Mondaysys", "Frappe Framework"}


def site_name() -> str:
	return "MondayERP" if "erpnext" in frappe.get_installed_apps() else "Mondaysys"


def _brand(app: str, title: str | None, logo: str | None) -> tuple[str | None, str | None]:
	if app in APPS:
		new_title, new_logo = APPS[app]
		return new_title, new_logo or logo
	return title, logo


# ---------------------------------------------------------------- runtime wrappers


def mondaypos_installed() -> bool:
	"""has_permission for the MondayPOS apps-screen tile (POS Awesome has no tile of its own)."""
	return "posawesome" in frappe.get_installed_apps()


def _rebind(original, wrapper):
	"""Point every already-imported module that holds `original` at `wrapper`
	(e.g. `from frappe.apps import get_apps` done before this app's hooks loaded)."""
	import sys

	for module in list(sys.modules.values()):
		name = getattr(module, "__name__", "") or ""
		if not name.startswith(("frappe", "erpnext", "hrms", "crm")):
			continue
		for attr in ("get_apps", "get_versions"):
			try:
				if getattr(module, attr, None) is original:
					setattr(module, attr, wrapper)
			except Exception:
				pass


def install_runtime_patches(*args, **kwargs):
	"""Idempotently wrap upstream functions that expose app titles/logos.
	Runs at hook import, before every request and at boot, so import order can't bypass it."""
	try:
		import frappe.apps as apps_module

		current = apps_module.get_apps
		if not getattr(current, "_mondaysys", False):

			def get_apps(*a, **kw):
				result = current(*a, **kw)
				for row in result or []:
					row["title"], row["logo"] = _brand(row.get("name"), row.get("title"), row.get("logo"))
				return result

			get_apps._mondaysys = True
			get_apps._original = current
			apps_module.get_apps = get_apps
		_rebind(getattr(apps_module.get_apps, "_original", None), apps_module.get_apps)
	except Exception:
		pass

	try:
		import frappe.utils.change_log as change_log

		current_versions = change_log.get_versions
		if not getattr(current_versions, "_mondaysys", False):

			def get_versions(*a, **kw):
				versions = current_versions(*a, **kw)
				for app, info in (versions or {}).items():
					if app in APPS and isinstance(info, dict):
						info["title"] = APPS[app][0]
				return versions

			get_versions._mondaysys = True
			get_versions._original = current_versions
			change_log.get_versions = get_versions
		_rebind(getattr(change_log.get_versions, "_original", None), change_log.get_versions)
	except Exception:
		pass


def boot_session(bootinfo):
	"""Brand the desk boot data (v15 and v16)."""
	install_runtime_patches()
	try:
		bootinfo.app_logo_url = ICON
		for row in bootinfo.get("app_data") or []:  # v16 app sidebar
			row["app_title"], row["app_logo_url"] = _brand(
				row.get("app_name"), row.get("app_title"), row.get("app_logo_url")
			)
		apps_data = bootinfo.get("apps_data")  # v15 apps screen
		if isinstance(apps_data, dict):
			for row in apps_data.get("apps") or []:
				row["title"], row["logo"] = _brand(row.get("name"), row.get("title"), row.get("logo"))
	except Exception:
		frappe.log_error("Mondaysys branding: boot_session failed")


# ---------------------------------------------------------------- settings (re-applied on migrate)


def _set_if_ours(doctype: str, field: str, value, replaceable: set):
	meta = frappe.get_meta(doctype)
	if not meta.get_field(field):
		return
	current = frappe.db.get_single_value(doctype, field)
	if current in replaceable and current != value:
		frappe.db.set_single_value(doctype, field, value)


def apply_site_branding():
	_set_if_ours("Website Settings", "app_name", site_name(), REPLACEABLE_NAMES)
	_set_if_ours("System Settings", "app_name", site_name(), REPLACEABLE_NAMES)
	_set_if_ours("Website Settings", "app_logo", ICON, REPLACEABLE_LOGOS)
	_set_if_ours("Website Settings", "splash_image", LOGO, REPLACEABLE_LOGOS)
	_set_if_ours("Website Settings", "favicon", FAVICON, REPLACEABLE_LOGOS | {FAVICON})
	_set_if_ours("Navbar Settings", "app_logo", ICON, REPLACEABLE_LOGOS)
	frappe.db.commit()
	frappe.clear_cache()
