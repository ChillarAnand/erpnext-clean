# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.reload_doc("accounts", "doctype", "account")
	frappe.db.sql("""update tabAccount set warehouse=master_name
		where ifnull(account_type, '') = 'Warehouse' and ifnull(master_name, '') != ''""")
