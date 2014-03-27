# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, flt
from frappe import _
from erpnext.controllers.accounts_controller import AccountsController

class PeriodClosingVoucher(AccountsController):
		self.year_start_date = ''

	def validate(self):
		self.validate_account_head()
		self.validate_posting_date()

	def on_submit(self):
		self.make_gl_entries()

	def on_cancel(self):
		frappe.db.sql("""delete from `tabGL Entry` 
			where voucher_type = 'Period Closing Voucher' and voucher_no=%s""", self.doc.name)

	def validate_account_head(self):
		if frappe.db.get_value("Account", self.doc.closing_account_head, "report_type") \
				!= "Balance Sheet":
			frappe.throw(_("Account") + ": " + self.doc.closing_account_head + 
				_("must be a Liability account"))

	def validate_posting_date(self):
		from erpnext.accounts.utils import get_fiscal_year
		self.year_start_date = get_fiscal_year(self.doc.posting_date, self.doc.fiscal_year)[1]

		pce = frappe.db.sql("""select name from `tabPeriod Closing Voucher`
			where posting_date > %s and fiscal_year = %s and docstatus = 1""", 
			(self.doc.posting_date, self.doc.fiscal_year))
		if pce and pce[0][0]:
			frappe.throw(_("Another Period Closing Entry") + ": " + cstr(pce[0][0]) + 
				  _("has been made after posting date") + ": " + self.doc.posting_date)
		
	def get_pl_balances(self):
		"""Get balance for pl accounts"""
		return frappe.db.sql("""
			select t1.account, sum(ifnull(t1.debit,0))-sum(ifnull(t1.credit,0)) as balance
			from `tabGL Entry` t1, `tabAccount` t2 
			where t1.account = t2.name and ifnull(t2.report_type, '') = 'Profit and Loss'
			and t2.docstatus < 2 and t2.company = %s 
			and t1.posting_date between %s and %s 
			group by t1.account
		""", (self.doc.company, self.year_start_date, self.doc.posting_date), as_dict=1)
	 
	def make_gl_entries(self):
		gl_entries = []
		net_pl_balance = 0
		pl_accounts = self.get_pl_balances()
		for acc in pl_accounts:
			if flt(acc.balance):
				gl_entries.append(self.get_gl_dict({
					"account": acc.account,
					"debit": abs(flt(acc.balance)) if flt(acc.balance) < 0 else 0,
					"credit": abs(flt(acc.balance)) if flt(acc.balance) > 0 else 0,
				}))
			
				net_pl_balance += flt(acc.balance)

		if net_pl_balance:
			gl_entries.append(self.get_gl_dict({
				"account": self.doc.closing_account_head,
				"debit": abs(net_pl_balance) if net_pl_balance > 0 else 0,
				"credit": abs(net_pl_balance) if net_pl_balance < 0 else 0
			}))
			
		from erpnext.accounts.general_ledger import make_gl_entries
		make_gl_entries(gl_entries)
