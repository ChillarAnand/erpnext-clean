# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
import frappe.defaults
from erpnext.shopping_cart.doctype.shopping_cart_settings.shopping_cart_settings import is_cart_enabled

def show_cart_count():
	if (is_cart_enabled() and
		frappe.db.get_value("User", frappe.session.user, "user_type") == "Website User"):
		return True

	return False

def set_cart_count(login_manager):
	role, parties = check_customer_or_supplier()
	if role == 'Supplier': return
	if show_cart_count():
		from erpnext.shopping_cart.cart import set_cart_count
		set_cart_count()

def clear_cart_count(login_manager):
	if show_cart_count():
		frappe.local.cookie_manager.delete_cookie("cart_count")

def update_website_context(context):
	cart_enabled = is_cart_enabled()
	context["shopping_cart_enabled"] = cart_enabled

def update_my_account_context(context):
	check_user_role, parties = check_customer_or_supplier()

	if check_user_role == 'Supplier':
		get_supplier_context(context)
	else:
		get_customer_context(context)

def get_supplier_context(context):
	context["my_account_list"].extend([
		{"label": _("Request for Quotations"), "url": "rfq"},
	])

def get_customer_context(context):
	context["my_account_list"].extend([
		{"label": _("Projects"), "url": "project"},
		{"label": _("Orders"), "url": "orders"},
		{"label": _("Invoices"), "url": "invoices"},
		{"label": _("Shipments"), "url": "shipments"},
		{"label": _("Issues"), "url": "issues"},
		{"label": _("Addresses"), "url": "addresses"}
	])

def check_customer_or_supplier():
	if frappe.session.user:
		contacts = frappe.get_all("Contact", fields=["customer", "supplier", "email_id"],
			filters={"email_id": frappe.session.user})

		customer = [d.customer for d in contacts if d.customer] or None
		supplier = [d.supplier for d in contacts if d.supplier] or None

		if customer: return 'Customer', customer
		if supplier : return 'Supplier', supplier
		return 'Customer', None