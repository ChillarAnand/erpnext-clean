# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

# import frappe
import unittest
# test_dependencies = ['Item', 'Sales Invoice', 'Stock Entry', 'Batch']

class TestPickList(unittest.TestCase):
	def test_pick_list_picks_warehouse_for_each_item(self):
		pass
# 		pick_list = frappe.get_doc({
# 			'doctype': 'Pick List',
# 			'company': '_Test Company',
# 			'customer': '_Test Customer',
# 			'items_based_on': 'Sales Order',
# 			'items': [{
# 				'item_code': '_Test Item Home Desktop 100',
# 				'qty': 5,
# 				'stock_qty': 5,
# 				'conversion_factor': 1,
# 				'sales_order': '_T-Sales Order-1',
# 				'sales_item': '_T-Sales Order-1_item',
# 			}]
# 		})
# 		pick_list.set_item_locations()

# 		self.assertEqual(pick_list.locations[0].item_code, '_Test Item Home Desktop 100')
# 		self.assertEqual(pick_list.locations[0].warehouse, '_Test Warehouse - _TC')
# 		self.assertEqual(pick_list.locations[0].qty, 5)

	# def test_pick_list_skips_out_of_stock_item(self):
	# 	pick_list = frappe.get_doc({
	# 		'doctype': 'Pick List',
	# 		'company': '_Test Company',
	# 		'customer': '_Test Customer',
	# 		'items_based_on': 'Sales Order',
	# 		'items': [{
	# 			'item_code': '_Test Item Warehouse Group Wise Reorder',
	# 			'qty': 1000,
	# 			'stock_qty': 1000,
	# 			'conversion_factor': 1,
	# 			'sales_order': '_T-Sales Order-1',
	# 			'sales_item': '_T-Sales Order-1_item',
	# 		}]
	# 	})

	# 	pick_list.set_item_locations()

	# 	self.assertEqual(pick_list.locations[0].item_code, '_Test Item Warehouse Group Wise Reorder')
	# 	self.assertEqual(pick_list.locations[0].warehouse, '_Test Warehouse Group-C1 - _TC')
	# 	self.assertEqual(pick_list.locations[0].qty, 30)


	# def test_pick_list_skips_items_in_expired_batch(self):
	# 	pass

	# def test_pick_list_shows_serial_no_for_serialized_item(self):

	# 	stock_reconciliation = frappe.get_doc({
	# 		'doctype': 'Stock Reconciliation',
	# 		'company': '_Test Company',
	# 		'items': [{
	# 			'item_code': '_Test Serialized Item',
	# 			'warehouse': '_Test Warehouse - _TC',
	# 			'qty': 5,
	# 			'serial_no': '123450\n123451\n123452\n123453\n123454'
	# 		}]
	# 	})

	# 	stock_reconciliation.submit()

	# 	pick_list = frappe.get_doc({
	# 		'doctype': 'Pick List',
	# 		'company': '_Test Company',
	# 		'customer': '_Test Customer',
	# 		'items_based_on': 'Sales Order',
	# 		'items': [{
	# 			'item_code': '_Test Serialized Item',
	# 			'qty': 1000,
	# 			'stock_qty': 1000,
	# 			'conversion_factor': 1,
	# 			'sales_order': '_T-Sales Order-1',
	# 			'sales_item': '_T-Sales Order-1_item',
	# 		}]
	# 	})

	# 	pick_list.set_item_locations()
	# 	self.assertEqual(pick_list.locations[0].item_code, '_Test Serialized Item')
	# 	self.assertEqual(pick_list.locations[0].warehouse, '_Test Warehouse - _TC')
	# 	self.assertEqual(pick_list.locations[0].qty, 5)
	# 	self.assertEqual(pick_list.locations[0].serial_no, '123450\n123451\n123452\n123453\n123454')


	# def test_pick_list_for_multiple_reference_doctypes(self):
	# 	pass


## records required

'''
batch no
items
sales invoice
stock entries
	bin
	stock ledger entry
warehouses
'''