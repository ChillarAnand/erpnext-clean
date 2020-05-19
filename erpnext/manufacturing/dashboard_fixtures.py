# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe, erpnext, json
from frappe import _
from frappe.utils import nowdate, get_date_str
from erpnext.accounts.utils import get_fiscal_year

def get_data():
	return frappe._dict({
		"dashboards": get_dashboards(),
		"charts": get_charts(),
		"number_cards": get_number_cards(),
	})

def get_dashboards():
	return [{
		"name": "Manufacturing Dashboard",
		"dashboard_name": "Manufacturing Dashboard",
		"charts": [
			{ "chart": "Produced Quantity", "width": "Half" },
			{ "chart": "Completed Operation", "width": "Half" },
			{ "chart": "Work Order Analysis", "width": "Half" },
			{ "chart": "Quality Inspection Analysis", "width": "Half" },
			{ "chart": "Pending Work Order", "width": "Half" },
			{ "chart": "Last Month Downtime Analysis", "width": "Half" },
			{ "chart": "Work Order Qty Analysis", "width": "Full" },
			{ "chart": "Job Card Analysis", "width": "Full" }
		],
		"cards": [
			{ "card": "Total Work Order" },
			{ "card": "Completed Work Order" },
			{ "card": "Ongoing Job Card" },
			{ "card": "Total Quality Inspection"}
		]
	}]

def get_charts():
	company = erpnext.get_default_company()

	if not company:
		company = frappe.db.get_value("Company", {"is_group": 0}, "name")

	return [{
		"doctype": "Dashboard Chart",
		"based_on": "modified",
		"time_interval": "Yearly",
		"chart_type": "Sum",
		"chart_name": _("Produced Quantity"),
		"name": "Produced Quantity",
		"document_type": "Work Order",
		"filters_json": json.dumps([['Work Order', 'docstatus', '=', 1, False]]),
		"group_by_type": "Count",
		"time_interval": "Monthly",
		"timespan": "Last Year",
		"owner": "Administrator",
		"type": "Line",
		"value_based_on": "produced_qty",
		"is_public": 1,
		"timeseries": 1
	}, {
		"doctype": "Dashboard Chart",
		"based_on": "creation",
		"time_interval": "Yearly",
		"chart_type": "Sum",
		"chart_name": _("Completed Operation"),
		"name": "Completed Operation",
		"document_type": "Work Order Operation",
		"filters_json": json.dumps([['Work Order Operation', 'docstatus', '=', 1, False]]),
		"group_by_type": "Count",
		"time_interval": "Quarterly",
		"timespan": "Last Year",
		"owner": "Administrator",
		"type": "Line",
		"value_based_on": "completed_qty",
		"is_public": 1,
		"timeseries": 1
	}, {
		"doctype": "Dashboard Chart",
		"time_interval": "Yearly",
		"chart_type": "Report",
		"chart_name": _("Work Order Analysis"),
		"name": "Work Order Analysis",
		"timespan": "Last Year",
		"report_name": "Work Order Summary",
		"owner": "Administrator",
		"filters_json": json.dumps({"company": company, "charts_based_on": "Status"}),
		"type": "Donut",
		"is_public": 1,
		"is_custom": 1,
		"custom_options": json.dumps({
			"axisOptions": {
				"shortenYAxisNumbers": 1
			},
			"height": 300
		}),
	}, {
		"doctype": "Dashboard Chart",
		"time_interval": "Yearly",
		"chart_type": "Report",
		"chart_name": _("Quality Inspection Analysis"),
		"name": "Quality Inspection Analysis",
		"timespan": "Last Year",
		"report_name": "Quality Inspection Summary",
		"owner": "Administrator",
		"filters_json": json.dumps({}),
		"type": "Donut",
		"is_public": 1,
		"is_custom": 1,
		"custom_options": json.dumps({
			"axisOptions": {
				"shortenYAxisNumbers": 1
			},
			"height": 300
		}),
	}, {
		"doctype": "Dashboard Chart",
		"time_interval": "Yearly",
		"chart_type": "Report",
		"chart_name": _("Pending Work Order"),
		"name": "Pending Work Order",
		"timespan": "Last Year",
		"report_name": "Work Order Summary",
		"filters_json": json.dumps({"company": company, "charts_based_on": "Age"}),
		"owner": "Administrator",
		"type": "Donut",
		"is_public": 1,
		"is_custom": 1,
		"custom_options": json.dumps({
			"axisOptions": {
				"shortenYAxisNumbers": 1
			},
			"height": 300
		}),
	}, {
		"doctype": "Dashboard Chart",
		"time_interval": "Yearly",
		"chart_type": "Report",
		"chart_name": _("Last Month Downtime Analysis"),
		"name": "Last Month Downtime Analysis",
		"timespan": "Last Year",
		"filters_json": json.dumps({}),
		"report_name": "Downtime Analysis",
		"owner": "Administrator",
		"is_public": 1,
		"is_custom": 1,
		"type": "Bar"
	}, {
		"doctype": "Dashboard Chart",
		"time_interval": "Yearly",
		"chart_type": "Report",
		"chart_name": _("Work Order Qty Analysis"),
		"name": "Work Order Qty Analysis",
		"timespan": "Last Year",
		"report_name": "Work Order Summary",
		"filters_json": json.dumps({"company": company, "charts_based_on": "Quantity"}),
		"owner": "Administrator",
		"type": "Bar",
		"is_public": 1,
		"is_custom": 1,
		"custom_options": json.dumps({
			"barOptions": { "stacked": 1 }
		}),
	}, {
		"doctype": "Dashboard Chart",
		"time_interval": "Yearly",
		"chart_type": "Report",
		"chart_name": _("Job Card Analysis"),
		"name": "Job Card Analysis",
		"timespan": "Last Year",
		"report_name": "Job Card Summary",
		"owner": "Administrator",
		"is_public": 1,
		"is_custom": 1,
		"filters_json": json.dumps({"company": company, "docstatus": 1, "range":"Monthly"}),
		"custom_options": json.dumps({
			"barOptions": { "stacked": 1 }
		}),
		"type": "Bar"
	}]

def get_number_cards():
	fiscal_year = get_fiscal_year(date=nowdate())
	year_start_date = get_date_str(fiscal_year[1])
	year_end_date = get_date_str(fiscal_year[2])

	return [{
		"doctype": "Number Card",
		"document_type": "Work Order",
		"name": "Total Work Order",
		"filters_json": json.dumps([
			['Work Order', 'docstatus', '=', 1],
			['Work Order', 'creation', 'between', [year_start_date, year_end_date]]
		]),
		"function": "Count",
		"is_public": 1,
		"label": _("Total Work Order"),
		"show_percentage_stats": 1,
		"stats_time_interval": "Monthly"
	},
	{
		"doctype": "Number Card",
		"document_type": "Work Order",
		"name": "Completed Work Order",
		"filters_json": json.dumps([
			['Work Order', 'status', '=', 'Completed'],
			['Work Order', 'docstatus', '=', 1],
			['Work Order', 'creation', 'between', [year_start_date, year_end_date]]
		]),
		"function": "Count",
		"is_public": 1,
		"label": _("Completed Work Order"),
		"show_percentage_stats": 1,
		"stats_time_interval": "Monthly"
	},
	{
		"doctype": "Number Card",
		"document_type": "Job Card",
		"name": "Ongoing Job Card",
		"filters_json": json.dumps([
			['Job Card', 'status','!=','Completed'],
			['Job Card', 'docstatus', '=', 1]
		]),
		"function": "Count",
		"is_public": 1,
		"label": _("Ongoing Job Card"),
		"show_percentage_stats": 1,
		"stats_time_interval": "Monthly"
	},
	{
		"doctype": "Number Card",
		"document_type": "Quality Inspection",
		"name": "Total Quality Inspection",
		"filters_json": json.dumps([['Quality Inspection', 'docstatus', '=', 1]]),
		"function": "Count",
		"is_public": 1,
		"label": _("Total Quality Inspection"),
		"show_percentage_stats": 1,
		"stats_time_interval": "Monthly"
	}]