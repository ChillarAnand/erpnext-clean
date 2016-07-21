from __future__ import unicode_literals
import frappe
from erpnext.setup.setup_wizard import domainify

def execute():
	if 'schools' in frappe.get_installed_apps():
		frappe.get_doc('Portal Settings', 'Portal Settings').sync_menu()
		frappe.db.sql("""delete from `tabDesktop Icon`""")
		if not frappe.db.exists('Module Def', 'Schools'):
			frappe.get_doc({
				'doctype': 'Module Def',
				'module_name': 'Schools',
				'app_name': 'erpnext'
			}).insert()
		frappe.db.sql("""update `tabDocType` set module='Schools' where module='Academics'""")
		from frappe.installer import remove_from_installed_apps
		remove_from_installed_apps("schools")
		domainify.setup_domain('Education')
	else:
		frappe.reload_doc('schools', 'doctype', 'announcement')
		frappe.reload_doc('schools', 'doctype', 'course')
		frappe.reload_doc('schools', 'doctype', 'fees')
		frappe.reload_doc('schools', 'doctype', 'examination')
		frappe.get_doc('Portal Settings', 'Portal Settings').sync_menu()
		domainify.setup_sidebar_items(domainify.get_domain('Manufacturing'))
