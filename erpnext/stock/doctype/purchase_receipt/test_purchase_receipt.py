# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from __future__ import unicode_literals
import unittest
import frappe
import frappe.defaults
from frappe.utils import cint

class TestPurchaseReceipt(unittest.TestCase):
	def test_make_purchase_invoice(self):
		self._clear_stock_account_balance()
		set_perpetual_inventory(0)
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice

		pr = frappe.copy_doc(test_records[0]).insert()
		
		self.assertRaises(frappe.ValidationError, make_purchase_invoice, 
			pr.name)

		pr = frappe.get_doc("Purchase Receipt", pr.name)
		pr.submit()
		pi = make_purchase_invoice(pr.name)
		
		self.assertEquals(pi[0]["doctype"], "Purchase Invoice")
		self.assertEquals(len(pi), len(pr.doclist))
		
		# modify rate
		pi[1]["rate"] = 200
		self.assertRaises(frappe.ValidationError, frappe.get_doc(pi).submit)
		
	def test_purchase_receipt_no_gl_entry(self):
		self._clear_stock_account_balance()
		set_perpetual_inventory(0)
		pr = frappe.copy_doc(test_records[0])
		pr.insert()
		pr.submit()
		
		stock_value, stock_value_difference = frappe.db.get_value("Stock Ledger Entry", 
			{"voucher_type": "Purchase Receipt", "voucher_no": pr.name, 
				"item_code": "_Test Item", "warehouse": "_Test Warehouse - _TC"}, 
			["stock_value", "stock_value_difference"])
		self.assertEqual(stock_value, 375)
		self.assertEqual(stock_value_difference, 375)
		
		bin_stock_value = frappe.db.get_value("Bin", {"item_code": "_Test Item", 
			"warehouse": "_Test Warehouse - _TC"}, "stock_value")
		self.assertEqual(bin_stock_value, 375)
		
		self.assertFalse(get_gl_entries("Purchase Receipt", pr.name))
		
	def test_purchase_receipt_gl_entry(self):
		self._clear_stock_account_balance()
		
		set_perpetual_inventory()
		self.assertEqual(cint(frappe.defaults.get_global_default("auto_accounting_for_stock")), 1)
		
		pr = frappe.copy_doc(test_records[0])
		pr.insert()
		pr.submit()
		
		gl_entries = get_gl_entries("Purchase Receipt", pr.name)
		
		self.assertTrue(gl_entries)
		
		stock_in_hand_account = frappe.db.get_value("Account", 
			{"master_name": pr.doclist[1].warehouse})		
		fixed_asset_account = frappe.db.get_value("Account", 
			{"master_name": pr.doclist[2].warehouse})
		
		expected_values = {
			stock_in_hand_account: [375.0, 0.0],
			fixed_asset_account: [375.0, 0.0],
			"Stock Received But Not Billed - _TC": [0.0, 750.0]
		}
		
		for gle in gl_entries:
			self.assertEquals(expected_values[gle.account][0], gle.debit)
			self.assertEquals(expected_values[gle.account][1], gle.credit)
			
		pr.cancel()
		self.assertFalse(get_gl_entries("Purchase Receipt", pr.name))
		
		set_perpetual_inventory(0)
		
	def _clear_stock_account_balance(self):
		frappe.db.sql("delete from `tabStock Ledger Entry`")
		frappe.db.sql("""delete from `tabBin`""")
		frappe.db.sql("""delete from `tabGL Entry`""")
		
	def test_subcontracting(self):
		pr = frappe.copy_doc(test_records[1])
		pr.run_method("calculate_taxes_and_totals")
		pr.insert()
		
		self.assertEquals(pr.doclist[1].rm_supp_cost, 70000.0)
		self.assertEquals(len(pr.get("pr_raw_material_details")), 2)
		
	def test_serial_no_supplier(self):
		pr = frappe.copy_doc(test_records[0])
		pr.doclist[1].item_code = "_Test Serialized Item With Series"
		pr.doclist[1].qty = 1
		pr.doclist[1].received_qty = 1
		pr.insert()
		pr.submit()
		
		self.assertEquals(frappe.db.get_value("Serial No", pr.doclist[1].serial_no, 
			"supplier"), pr.supplier)
			
		return pr
	
	def test_serial_no_cancel(self):
		pr = self.test_serial_no_supplier()
		pr.cancel()
		
		self.assertFalse(frappe.db.get_value("Serial No", pr.doclist[1].serial_no, 
			"warehouse"))
			
def get_gl_entries(voucher_type, voucher_no):
	return frappe.db.sql("""select account, debit, credit
		from `tabGL Entry` where voucher_type=%s and voucher_no=%s
		order by account desc""", (voucher_type, voucher_no), as_dict=1)
		
def set_perpetual_inventory(enable=1):
	accounts_settings = frappe.get_doc("Accounts Settings")
	accounts_settings.auto_accounting_for_stock = enable
	accounts_settings.save()
	
		
test_dependencies = ["BOM"]

test_records = frappe.get_test_records('Purchase Receipt')