// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.require("assets/erpnext/js/financial_statements.js");

frappe.query_reports["Profit and Loss Statement"] = $.extend({}, erpnext.financial_statements);

frappe.query_reports["Profit and Loss Statement"]["filters"].push({
	"fieldname": "accumulated_values",
	"label": __("Accumulated Values"),
	"fieldtype": "Check"
});

console.log(frappe.query_reports["Profit and Loss Statement"]);

