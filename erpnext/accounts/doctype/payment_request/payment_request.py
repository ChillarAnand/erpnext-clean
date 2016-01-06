# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate, get_url, cstr
from frappe import _
from erpnext.accounts.doctype.journal_entry.journal_entry import (get_payment_entry_against_invoice, 
get_payment_entry_against_order)
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import get_account_currency, get_balance_on
from itertools import chain

class PaymentRequest(Document):		
	def validate(self):
		self.validate_payment_gateway_account()
		self.validate_payment_request()
		self.validate_currency()

	def validate_payment_request(self):
		if frappe.db.get_value("Payment Request", {"reference_name": self.reference_name, 
			"name": ("!=", self.name), "status": ("not in", ["Initiated", "Paid"]), "docstatus": 1}, "name"):
			frappe.throw(_("Payment Request already exist"))
	
	def validate_currency(self):
		ref_doc = frappe.get_doc(self.reference_doctype, self.reference_name)
		if ref_doc.currency != frappe.db.get_value("Account", self.payment_account, "account_currency"):
			frappe.throw(_("Transaction currency is not similar to Gateway Currency"))
			
	def validate_payment_gateway_account(self):
		if not self.payment_gateway:
			frappe.throw(_("Payment Gateway Account is not configured"))
			
	def validate_payment_gateway(self):
		if self.gateway == "PayPal":
			if not frappe.db.get_value("PayPal Settings", None, "api_username"):
				if not frappe.conf.paypal_username:
					frappe.throw(_("PayPal Settings missing"))
			
		
	def on_submit(self):
		if not self.mute_email:
			self.send_payment_request()
			self.send_email()

		self.make_communication_entry()
	
	def on_cancel(self):
		self.set_cancelled()
		
	def on_update_after_submit(self):
		pass
	
	def set_status(self):
		pass
	
	def make_invoice(self):
		if self.make_sales_invoice:
			from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
			si = make_sales_invoice(self.reference_name, ignore_permissions=True)
			si = si.insert(ignore_permissions=True)
			si.submit()
	
	def send_payment_request(self):
		self.payment_url = get_url("/api/method/erpnext.accounts.doctype.payment_request.payment_request.generate_payment_request?name={0}".format(self.name))
		if self.payment_url:
			frappe.db.set_value(self.doctype, self.name, "status", "Initiated")
			
	def set_paid(self):
		if frappe.session.user == "Guest":
			frappe.set_user("Administrator")
			
		jv = self.create_journal_entry()
		self.make_invoice()
		
		return jv
		
	def create_journal_entry(self):
		"""create entry"""
		payment_details = {
			"amount": self.amount,
			"return_obj": True,
			"bank_account": self.payment_account
		}
		
		frappe.flags.ignore_account_permission = True
				
		if self.reference_doctype == "Sales Order":
			jv = get_payment_entry_against_order(self.reference_doctype, self.reference_name, payment_details)
			
		if self.reference_doctype == "Sales Invoice":
			jv = get_payment_entry_against_invoice(self.reference_doctype, self.reference_name, payment_details)
			
		jv.update({
			"voucher_type": "Journal Entry",
			"posting_date": nowdate()
		})		
		jv.insert(ignore_permissions=True)
		jv.submit()
		
		#set status as paid for Payment Request
		frappe.db.set_value(self.doctype, self.name, "status", "Paid")
		
		return jv
		
	def send_email(self):
		"""send email with payment link"""
		frappe.sendmail(recipients=self.email_to, sender=None, subject=self.subject,
			message=self.get_message(), attachments=[frappe.attach_print(self.reference_doctype, 
			self.reference_name, file_name=self.reference_name, print_format=self.print_format)])
						
	def get_message(self):
		"""return message with payment gateway link"""
		return  self.message + """ <a href="%s"> Click here to pay </a>"""%self.payment_url
		
	def set_failed(self):
		pass
	
	def set_cancelled(self):
		frappe.db.set_value(self.doctype, self.name, "status", "Cancelled")
	
	def make_communication_entry(self):
		"""Make communication entry"""
		comm = frappe.get_doc({
			"doctype":"Communication",
			"subject": self.subject,
			"content": self.get_message(),
			"sent_or_received": "Sent",
			"reference_doctype": self.reference_doctype,
			"reference_name": self.reference_name
		})
		comm.insert(ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def make_payment_request(**args):
	"""Make payment request"""
	
	args = frappe._dict(args)
	ref_doc = get_reference_doc_details(args.dt, args.dn)
	gateway_account = get_gateway_details(args)
	
	pr = frappe.new_doc("Payment Request")
	pr.update({
		"payment_gateway": gateway_account.name,
		"gateway": gateway_account.gateway,
		"payment_account": gateway_account.payment_account,
		"currency": ref_doc.currency,
		"make_sales_invoice": args.cart or 0,
		"amount": get_amount(ref_doc, args.dt),
		"mute_email": args.mute_email or 0,
		"email_to": args.recipient_id or "",
		"subject": "Payment Request for %s"%args.dn,
		"message": gateway_account.message,
		"reference_doctype": args.dt,
		"reference_name": args.dn
	})
	
	if args.return_doc:
		return pr
		
	if args.submit_doc:
		pr.insert(ignore_permissions=True)
		pr.submit()
		
		if args.cart:
			generate_payment_request(pr.name)
			frappe.db.commit()
		
		if not args.cart:	
			return pr
			
	return pr.as_dict()

def get_reference_doc_details(dt, dn):
	""" return reference doc Sales Order/Sales Invoice"""
	return frappe.get_doc(dt, dn)

def get_amount(ref_doc, dt):
	"""get amount based on doctype"""
	if dt == "Sales Order":
		amount = flt(ref_doc.base_grand_total) - flt(ref_doc.advance_paid)

	if dt == "Sales Invoice":
		amount = abs(ref_doc.outstanding_amount)
	
	if amount > 0:
		return amount
	else:
		frappe.throw(_("Payment Entry is already created"))
		
def get_gateway_details(args):
	"""return gateway and payment account of default payment gateway"""
	if args.payemnt_gateway:
		gateway_account = frappe.db.get_value("Payment Gateway Account", args.payemnt_gateway, 
			["name", "gateway", "payment_account", "message"], as_dict=1)
	
	gateway_account = frappe.db.get_value("Payment Gateway Account", {"is_default": 1}, 
		["name", "gateway", "payment_account", "message"], as_dict=1)
	
	if not gateway_account:
		frappe.throw(_("Payment Gateway Account is not configured"))
	
	return gateway_account

@frappe.whitelist()
def get_print_format_list(ref_doctype):
	print_format_list = ["Standard"]
	
	print_format_list.extend(list(chain.from_iterable(frappe.db.sql("""select name from `tabPrint Format` 
		where doc_type=%s""", ref_doctype, as_list=1))))
	
	return {
		"print_format": print_format_list
	}
	
@frappe.whitelist(allow_guest=True)
def generate_payment_request(name):
	doc = frappe.get_doc("Payment Request", name)
	if doc.docstatus not in [0, 2]:
		if doc.gateway == "PayPal":
			from paypal_integration.express_checkout import set_express_checkout
			payment_url = set_express_checkout(doc.amount, doc.currency, {"doctype": doc.doctype,
				"docname": doc.name})
	
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = payment_url
	else:
		frappe.respond_as_web_page(_("Invalid Payment Request"), 
			_("Payment Request has been canceled by vendor"), success=False, 
			http_status_code=frappe.ValidationError.http_status_code)
			
@frappe.whitelist(allow_guest=True)
def resend_payment_email(docname):
	return frappe.get_doc("Payment Request", docname).send_email()
		