# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import cstr, flt, getdate, now, nowdate
from frappe import msgprint

from frappe.model.document import Document

class BankReconciliation(Document):

	def get_details(self):
		if not (self.doc.bank_account and self.doc.from_date and self.doc.to_date):
			msgprint("Bank Account, From Date and To Date are Mandatory")
			return
	
		dl = frappe.db.sql("select t1.name, t1.cheque_no, t1.cheque_date, t2.debit, t2.credit, t1.posting_date, t2.against_account from `tabJournal Voucher` t1, `tabJournal Voucher Detail` t2 where t2.parent = t1.name and t2.account = %s and (clearance_date is null or clearance_date = '0000-00-00' or clearance_date = '') and t1.posting_date >= %s and t1.posting_date <= %s and t1.docstatus=1", (self.doc.bank_account, self.doc.from_date, self.doc.to_date))
		
		self.set('entries', [])
		self.doc.total_amount = 0.0

		for d in dl:
			nl = self.doc.append('entries', {})
			nl.posting_date = cstr(d[5])
			nl.voucher_id = cstr(d[0])
			nl.cheque_number = cstr(d[1])
			nl.cheque_date = cstr(d[2])
			nl.debit = flt(d[3])
			nl.credit = flt(d[4])
			nl.against_account = cstr(d[6])
			self.doc.total_amount += flt(flt(d[4]) - flt(d[3]))

	def update_details(self):
		vouchers = []
		for d in self.get('entries'):
			if d.clearance_date:
				if d.cheque_date and getdate(d.clearance_date) < getdate(d.cheque_date):
					msgprint("Clearance Date can not be before Cheque Date (Row #%s)" % 
						d.idx, raise_exception=1)
					
				frappe.db.sql("""update `tabJournal Voucher` 
					set clearance_date = %s, modified = %s where name=%s""",
					(d.clearance_date, nowdate(), d.voucher_id))
				vouchers.append(d.voucher_id)

		if vouchers:
			msgprint("Clearance Date updated in %s" % ", ".join(vouchers))
		else:
			msgprint("Clearance Date not mentioned")