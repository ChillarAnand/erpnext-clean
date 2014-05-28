# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	update_hr_permissions()
	update_permissions()
	remove_duplicate_user_permissions()
	frappe.clear_cache()

def update_hr_permissions():
	from frappe.core.page.user_permissions import user_permissions

	# add set user permissions rights to HR Manager
	frappe.db.sql("""update `tabDocPerm` set `set_user_permissions`=1 where parent in ('Employee', 'Leave Application')
		and role='HR Manager' and permlevel=0 and `read`=1""")

	# apply user permissions on Employee and Leave Application
	frappe.db.sql("""update `tabDocPerm` set `apply_user_permissions`=1 where parent in ('Employee', 'Leave Application')
		and role in ('Employee', 'Leave Approver') and permlevel=0 and `read`=1""")

	frappe.clear_cache()

	# save employees to run on_update events
	for employee in frappe.db.sql_list("""select name from `tabEmployee`"""):
		frappe.get_doc("Employee", employee).save()

def update_permissions():
	# clear match conditions other than owner
	frappe.db.sql("""update tabDocPerm set `match`=''
		where ifnull(`match`,'') not in ('', 'owner')""")

def remove_duplicate_user_permissions():
	# remove duplicate user_permissions (if they exist)
	for d in frappe.db.sql("""select parent, defkey, defvalue,
		count(*) as cnt from tabDefaultValue
		where parent not in ('__global', '__default')
		group by parent, defkey, defvalue""", as_dict=1):
		if d.cnt > 1:
			# order by parenttype so that user permission does not get removed!
			frappe.db.sql("""delete from tabDefaultValue where `parent`=%s and `defkey`=%s and
				`defvalue`=%s order by parenttype limit %s""", (d.parent, d.defkey, d.defvalue, d.cnt-1))

