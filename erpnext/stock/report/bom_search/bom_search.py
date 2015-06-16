# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json

def execute(filters=None):
	data = []

	for doctype in ("Sales BOM Item",
		"BOM Explosion Item" if filters.search_sub_assemblies else "BOM Item"):
		all_boms = {}
		for d in frappe.get_all(doctype, fields=["parent", "item_code"]):
			all_boms.setdefault(d.parent, []).append(d.item_code)

		for parent, items in all_boms.iteritems():
			valid = True
			for key, item in filters.iteritems():
				if key != "search_sub_assemblies":
					if item and item not in items:
						valid = False

			if valid:
				data.append((parent, doctype[:-5]))

	return [{
		"fieldname": "parent",
		"label": "BOM",
		"width": 200,
		"fieldtype": "Dynamic Link",
		"options": "doctype"
	},
	{
		"fieldname": "doctype",
		"label": "Type",
		"width": 200,
		"fieldtype": "Data"
	}], data

	#print json.dumps(all_boms, indent=1)
	#columns, data = [], []
	#return columns, data
