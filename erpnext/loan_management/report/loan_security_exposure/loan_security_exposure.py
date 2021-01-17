# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe import _
from frappe.utils import get_datetime, flt
from six import iteritems
from erpnext.loan_management.report.applicant_wise_loan_security_exposure.applicant_wise_loan_security_exposure \
	 import get_loan_security_details, get_applicant_wise_total_loan_security_qty

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{"label": _("Loan Security"), "fieldname": "loan_security", "fieldtype": "Link", "options": "Loan Security", "width": 160},
		{"label": _("Loan Security Code"), "fieldname": "loan_security_code", "fieldtype": "Data", "width": 100},
		{"label": _("Loan Security Name"), "fieldname": "loan_security_name", "fieldtype": "Data", "width": 150},
		{"label": _("Haircut"), "fieldname": "haircut", "fieldtype": "Percent", "width": 100},
		{"label": _("Loan Security Type"), "fieldname": "loan_security_type", "fieldtype": "Link", "options": "Loan Security Type", "width": 120},
		{"label": _("Disabled"), "fieldname": "disabled", "fieldtype": "Check", "width": 80},
		{"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
		{"label": _("Latest Price"), "fieldname": "latest_price", "fieldtype": "Currency", "options": "currency", "width": 100},
		{"label": _("Current Value"), "fieldname": "current_value", "fieldtype": "Currency", "options": "currency", "width": 100},
		{"label": _("% Of Total Portfolio"), "fieldname": "portfolio_percent", "fieldtype": "Percentage", "width": 100},
		{"label": _("Pledged Applicant Count"), "fieldname": "pledged_applicant_count", "fieldtype": "Percentage", "width": 100},
		{"label": _("Currency"), "fieldname": "currency", "fieldtype": "Currency", "options": "Currency", "hidden": 1, "width": 100},
	]

	return columns

def get_data(filters):
	data = []
	loan_security_details = get_loan_security_details(filters)
	current_pledges, total_portfolio_value = get_company_wise_loan_security_details(filters, loan_security_details)
	currency = erpnext.get_company_currency(filters.get('company'))

	for security, value in iteritems(current_pledges):
		row = {}
		current_value = flt(value['qty'] * loan_security_details.get(security)['latest_price'])
		row.update(loan_security_details.get(security))
		row.update({
			'total_qty': value['qty'],
			'current_value': current_value,
			'portfolio_percent': flt(current_value * 100 / total_portfolio_value, 2),
			'pledged_applicant_count': value['applicant_count'],
			'currency': currency
		})

		data.append(row)

	return data



def get_company_wise_loan_security_details(filters, loan_security_details):
	pledge_values, total_value_map, applicant_type_map = get_applicant_wise_total_loan_security_qty(filters,
		loan_security_details)

	total_portfolio_value = 0
	security_wise_map = {}
	for key, qty in iteritems(pledge_values):
		security_wise_map.setdefault(key[1], {
			'qty': 0.0,
			'applicant_count': 0.0
		})

		security_wise_map[key[1]]['qty'] += qty
		if qty:
			security_wise_map[key[1]]['applicant_count'] += 1

		total_portfolio_value += flt(qty * loan_security_details.get(key[1])['latest_price'])

	return security_wise_map, total_portfolio_value



