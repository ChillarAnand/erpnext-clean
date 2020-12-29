# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

class ProductFiltersBuilder:
	def __init__(self, item_group=None):
		if not item_group or item_group == "Products Settings":
			self.doc = frappe.get_doc("Products Settings")
		else:
			self.doc = frappe.get_doc("Item Group", item_group)

		self.item_group = item_group

	def get_field_filters(self):
		filter_fields = [row.fieldname for row in self.doc.filter_fields]

		meta = frappe.get_meta('Item')
		fields = [df for df in meta.fields if df.fieldname in filter_fields]

		filter_data = []
		for df in fields:
			filters = {}
			if df.fieldtype == "Link":
				if self.item_group:
					filters['item_group'] = self.item_group

				values =  frappe.get_all("Item", fields=[df.fieldname], filters=filters, distinct="True", pluck=df.fieldname)
			else:
				doctype = df.get_link_doctype()

				# apply enable/disable/show_in_website filter
				meta = frappe.get_meta(doctype)

				if meta.has_field('enabled'):
					filters['enabled'] = 1
				if meta.has_field('disabled'):
					filters['disabled'] = 0
				if meta.has_field('show_in_website'):
					filters['show_in_website'] = 1

				values = [d.name for d in frappe.get_all(doctype, filters)]

			# Remove None
			values = values.remove(None) if None in values else values
			if values:
				filter_data.append([df, values])

		return filter_data

	def get_attribute_fitlers(self):
		attributes = [row.attribute for row in self.doc.filter_attributes]
		attribute_docs = [
			frappe.get_doc('Item Attribute', attribute) for attribute in attributes
		]

		print(attribute_docs)

		# # mark attribute values as checked if they are present in the request url
		# if frappe.form_dict:
		# 	for attr in attribute_docs:
		# 		if attr.name in frappe.form_dict:
		# 			value = frappe.form_dict[attr.name]
		# 			if value:
		# 				enabled_values = value.split(',')
		# 			else:
		# 				enabled_values = []

		# 			for v in enabled_values:
		# 				for item_attribute_row in attr.item_attribute_values:
		# 					if v == item_attribute_row.attribute_value:
		# 						item_attribute_row.checked = True

		return attribute_docs
