# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from frappe.utils import flt, time_diff_in_hours, get_datetime, getdate, cint, get_datetime_str
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.manufacturing.doctype.manufacturing_settings.manufacturing_settings import get_mins_between_operations

class OverlapError(frappe.ValidationError): pass
class OverProductionLoggedError(frappe.ValidationError): pass

class TimeSheet(Document):

	def validate(self):
		self.set_status()
		self.total_hours = 0.0
		self.total_billing_amount = 0.0
		self.validate_dates()
		self.validate_time_logs()
		self.update_cost()
		for d in self.get("time_logs"):
			self.total_hours += flt(d.hours)
			if d.billable: self.total_billing_amount += flt(d.billing_amount)

	def set_status(self):
		self.status = {
			"0": "Draft",
			"1": "Submitted",
			"2": "Cancelled"
		}[str(self.docstatus or 0)]

		if self.sales_invoice:
			self.status = "Billed"

		if self.salary_slip:
			self.status = "Payslip"

		if self.sales_invoice and self.salary_slip:
			self.status = "Completed"

	def set_dates(self):
		if self.docstatus < 2:
			start_date = min([d.from_time for d in self.time_logs])
			end_date = max([d.to_time for d in self.time_logs])

			if start_date and end_date:
				self.start_date = getdate(start_date)
				self.end_date = getdate(end_date)

	def before_submit(self):
		self.set_dates()

	def before_cancel(self):
		self.set_status()

	def on_cancel(self):
		self.update_production_order(None)
		self.update_task_and_project()

	def on_submit(self):
		self.validate_mandatory_fields()
		self.update_production_order(self.name)
		self.update_task_and_project()

	def validate_mandatory_fields(self):
		if self.production_order:
			production_order = frappe.get_doc("Production Order", self.production_order)
			pending_qty = flt(production_order.qty) - flt(production_order.produced_qty)

		for data in self.time_logs:
			if not data.from_time and not data.to_time:
				frappe.throw(_("Row {0}: From Time and To Time is mandatory.").format(data.idx))

			if not data.activity_type and self.employee:
				frappe.throw(_("Row {0}: Activity Type is mandatory.").format(data.idx))

			if flt(data.hours) == 0.0:
				frappe.throw(_("Row {0}: Hours value must be greater than zero.").format(data.idx))

			if self.production_order and flt(data.completed_qty) == 0:
				frappe.throw(_("Row {0}: Completed Qty must be greater than zero.").format(data.idx))

			if self.production_order and flt(pending_qty) < flt(data.completed_qty):
				frappe.throw(_("Row {0}: Completed Qty cannot be more than {0} for operation {1}").format(data.idx, pending_qty, self.operation),
					OverProductionLoggedError)
					
			if data.billable and flt(data.billing_rate) == 0.0:
				frappe.throw(_("Row {0}: Billing Rate must be greater than zero.").format(data.idx))

	def update_production_order(self, time_sheet):
		if self.production_order:
			pro = frappe.get_doc('Production Order', self.production_order)

			for timesheet in self.time_logs:
				for data in pro.operations:
					if data.name == timesheet.operation_id:
						summary = self.get_actual_timesheet_summary(timesheet.operation_id)
						data.time_sheet = time_sheet
						data.completed_qty = summary.completed_qty 
						data.actual_operation_time = summary.mins
						data.actual_start_time = summary.from_time
						data.actual_end_time = summary.to_time

			pro.flags.ignore_validate_update_after_submit = True
			pro.update_operation_status()
			pro.calculate_operating_cost()
			pro.set_actual_dates()
			pro.save()

	def get_actual_timesheet_summary(self, operation_id):
		"""Returns 'Actual Operating Time'. """
		return frappe.db.sql("""select
			sum(tsd.hours*60) as mins, sum(tsd.completed_qty) as completed_qty, min(tsd.from_time) as from_time,
			max(tsd.to_time) as to_time from `tabTime Sheet Detail` as tsd, `tabTime Sheet` as ts where 
			ts.production_order = %s and tsd.operation_id = %s and ts.docstatus=1 and ts.name = tsd.parent""",
			(self.production_order, operation_id), as_dict=1)[0]

	def update_task_and_project(self):
		for data in self.time_logs:
			if data.task:
				task = frappe.get_doc("Task", data.task)
				task.update_time_and_costing()
				task.save()

			elif data.project:
				frappe.get_doc("Project", data.project).update_project()

	def validate_dates(self):
		for data in self.time_logs:
			if time_diff_in_hours(data.to_time, data.from_time) < 0:
				frappe.throw(_("To date cannot be before from date"))

	def validate_time_logs(self):
		for data in self.get('time_logs'):
			self.validate_overlap(data)
			self.check_workstation_timings(data)

	def validate_overlap(self, data):
		if self.production_order:
			self.validate_overlap_for("workstation", data)
		else:
			self.validate_overlap_for("user", data)
			self.validate_overlap_for("employee", data)

	def validate_overlap_for(self, fieldname, args):
		existing = self.get_overlap_for(fieldname, args)
		if existing:
			frappe.throw(_("Row {0}: From Time and To Time overlap with existing from and to time").format(args.idx),
				OverlapError)

	def get_overlap_for(self, fieldname, args):
		if not args.get(fieldname):
			return

		existing = frappe.db.sql("""select ts.name as name, tsd.from_time as from_time, tsd.to_time as to_time from 
			`tabTime Sheet Detail` tsd, `tabTime Sheet` ts where tsd.`{0}`=%(val)s and tsd.parent = ts.name and
			(
				(%(from_time)s > tsd.from_time and %(from_time)s < tsd.to_time) or
				(%(to_time)s > tsd.from_time and %(to_time)s < tsd.to_time) or
				(%(from_time)s <= tsd.from_time and %(to_time)s >= tsd.to_time))
			and tsd.name!=%(name)s
			and ts.docstatus < 2""".format(fieldname),
			{
				"val": args.get(fieldname),
				"from_time": args.from_time,
				"to_time": args.to_time,
				"name": args.name or "No Name"
			}, as_dict=True)

		return existing[0] if existing else None

	def check_workstation_timings(self, args):
		"""Checks if **Time Log** is between operating hours of the **Workstation**."""
		if args.workstation and args.from_time and args.to_time:
			from erpnext.manufacturing.doctype.workstation.workstation import check_if_within_operating_hours
			check_if_within_operating_hours(args.workstation, args.operation, args.from_time, args.to_time)

	def move_to_next_non_overlapping_slot(self, index):
		from datetime import timedelta
		if self.time_logs:
			for data in self.time_logs:
				if data.idx == index:
					overlapping = self.get_overlap_for("workstation", data)
					if not overlapping:
						frappe.throw(_("Logical error: Must find overlapping"))
					
					if overlapping:
						time_sheet = self.get_last_working_slot(overlapping.name, data.workstation)
						data.from_time = get_datetime(time_sheet.to_time) + get_mins_between_operations()
						data.to_time = get_datetime(data.from_time) + timedelta(hours=data.hours)
					break

	def get_last_working_slot(self, time_sheet, workstation):
		return frappe.db.sql(""" select max(from_time) as from_time, max(to_time) as to_time 
			from `tabTime Sheet Detail` where workstation = %(workstation)s""",
			{'workstation': workstation}, as_dict=True)[0]

	def update_cost(self):
		for data in self.time_logs:
			if data.activity_type and not data.billing_amount:
				rate = get_activity_cost(self.employee, data.activity_type)
				hours =  data.hours or 0
				if rate:
					data.billing_rate = flt(rate.get('billing_rate'))
					data.costing_rate = flt(rate.get('costing_rate'))
					data.billing_amount = data.billing_rate * hours
					data.costing_amount = data.costing_rate * hours

@frappe.whitelist()
def make_sales_invoice(source_name, target=None):
	target = frappe.new_doc("Sales Invoice")

	target.append("timesheets", get_mapped_doc("Time Sheet", source_name, {
		"Time Sheet": {
			"doctype": "Sales Invoice Timesheet",
			"field_map": {
				"total_billing_amount": "billing_amount",
				"name": "time_sheet"
			},
		}
	}))
	
	target.run_method("calculate_billing_amount_from_timesheet")

	return target

@frappe.whitelist()
def make_salary_slip(source_name, target_doc=None):
	target = frappe.new_doc("Salary Slip")
	set_missing_values(source_name, target)
	
	target.append("timesheets", get_mapped_doc("Time Sheet", source_name, {
		"Time Sheet": {
			"doctype": "Salary Slip Timesheet",
			"field_map": {
				"total_hours": "working_hours",
				"name": "time_sheet"
			},
		}
	}))
	
	target.run_method("get_emp_and_leave_details")

	return target

def set_missing_values(time_sheet, target):
	doc = frappe.get_doc('Time Sheet', time_sheet)
	target.employee = doc.employee
	target.employee_name = doc.employee_name
	target.salary_slip_based_on_timesheet = 1
	target.start_date = doc.start_date
	target.end_date = doc.end_date

@frappe.whitelist()
def get_activity_cost(employee=None, activity_type=None):
	rate = frappe.db.get_values("Activity Cost", {"employee": employee,
		"activity_type": activity_type}, ["costing_rate", "billing_rate"], as_dict=True)
	if not rate:
		rate = frappe.db.get_values("Activity Type", {"activity_type": activity_type},
			["costing_rate", "billing_rate"], as_dict=True)

	return rate[0] if rate else {}

@frappe.whitelist()
def get_employee_list(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select distinct(employee) as employee
		from `tabSalary Structure` where salary_slip_based_on_timesheet=1
		and employee like %(txt)s limit %(start)s, %(page_len)s""", 
		{'txt': "%%%s%%"%(txt), 'start': start, 'page_len': page_len})
