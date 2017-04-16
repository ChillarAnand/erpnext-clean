# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt,cstr
from erpnext.accounts.report.financial_statements import get_period_list

def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	data=get_lead_data(filters)
	return columns, data
	
def get_columns():
	columns = [_("Lead Owner") + ":data:130", _("Lead Count") + ":Int:80",
				_("Opp Count") + ":Int:80",
				_("Quot Count") + ":Int:80", _("Order Count") + ":Int:100",
				_("Order Value") + ":Float:100",_("Opp/Lead %") + ":Float:100",
				_("Quot/Lead %") + ":Float:100",_("Order/Quot %") + ":Float:100"
	]
	return columns

def get_lead_data(filters):
	conditions=""
	if filters.from_date:
		conditions += " and date(creation) >= %(from_date)s"
	if filters.to_date:
		conditions += " and date(creation) <= %(to_date)s"
	data = frappe.db.sql("""select lead_owner as "Lead Owner", count(name) as "Lead Count" from `tabLead` where 1 = 1 %s group by lead_owner""" % (conditions,),filters, as_dict=1)
	dl=list(data)
	for row in dl:
		is_quot_count_zero = False
		row["Quot Count"]= get_lead_quotation_count(row["Lead Owner"])
		row["Opp Count"] = get_lead_opp_count(row["Lead Owner"])
		row["Order Count"] = get_quotation_ordered_count(row["Lead Owner"])
		row["Order Value"] = get_order_amount(row["Lead Owner"])
		row["Opp/Lead %"] = row["Opp Count"] / row["Lead Count"] * 100
		row["Quot/Lead %"] = row["Quot Count"] / row["Lead Count"] * 100
		#Handle div by zero and reset count to zero
		if row["Quot Count"] == 0:
			row["Quot Count"] = 1
			is_quot_count_zero = True
		row["Order/Quot %"] = row["Order Count"] / row["Quot Count"] * 100
		if is_quot_count_zero ==  True:
			row["Quot Count"] = 0
	return dl
	
def get_lead_quotation_count(leadowner):
	quotation_count = frappe.db.sql("""select count(name) from `tabQuotation` 
										where lead in (select name from `tabLead` where lead_owner = %s)""",leadowner)
	return flt(quotation_count[0][0]) if quotation_count else 0
	
def get_lead_opp_count(leadowner):
	opportunity_count = frappe.db.sql("""select count(name) from `tabOpportunity` 
										where lead in (select name from `tabLead` where lead_owner = %s)""",leadowner)
	return flt(opportunity_count[0][0]) if opportunity_count else 0
	
def get_quotation_ordered_count(leadowner):
	quotation_ordered_count = frappe.db.sql("""select count(name) from `tabQuotation` 
												where status = 'Ordered' and lead in (select name from `tabLead` where lead_owner = %s)""",leadowner)
	return flt(quotation_ordered_count[0][0]) if quotation_ordered_count else 0
	
def get_order_amount(leadowner):
	ordered_count_amount = frappe.db.sql("""select sum(base_net_amount) from `tabSales Order Item` 
											where prevdoc_docname in (select name from `tabQuotation` 
											where status = 'Ordered' and lead in (select name from `tabLead` where lead_owner = %s))""",leadowner)
	return flt(ordered_count_amount[0][0]) if ordered_count_amount else 0