# ERPNext: Copyright 2013 Web Notes Technologies Pvt Ltd
# GNU General Public Licnese. See "license.txt"

from __future__ import unicode_literals
import webnotes

for_doctype = {
	"Support Ticket": {"status":"Open"},
	"Customer Issue": {"status":"Open"},
	"Task": {"status":"Open"},
	"Lead": {"status":"Open"},
	"Contact": {"status":"Open"},
	"Opportunity": {"docstatus":0},
	"Quotation": {"docstatus":0},
	"Sales Order": {"docstatus":0},
	"Journal Voucher": {"docstatus":0},
	"Sales Invoice": {"docstatus":0},
	"Purchase Invoice": {"docstatus":0},
	"Leave Application": {"status":"Open"},
	"Expense Claim": {"approval_status":"Draft"},
	"Job Applicant": {"status":"Open"},
	"Purchase Receipt": {"docstatus":0},
	"Delivery Note": {"docstatus":0},
	"Stock Entry": {"docstatus":0},
	"Material Request": {"docstatus":0},
	"Purchase Order": {"docstatus":0},
	"Production Order": {"docstatus":0},
	"BOM": {"docstatus":0},
	"Timesheet": {"docstatus":0},
	"Time Log": {"status":"Draft"},
	"Time Log Batch": {"status":"Draft"},
}

def get_things_todo():
	"""Returns a count of incomplete todos"""
	incomplete_todos = webnotes.conn.sql("""\
		SELECT COUNT(*) FROM `tabToDo`
		WHERE IFNULL(checked, 0) = 0
		AND (owner = %s or assigned_by=%s)""", (webnotes.session.user, webnotes.session.user))
	return incomplete_todos[0][0]

def get_todays_events():
	"""Returns a count of todays events in calendar"""
	from webnotes.utils import nowdate
	todays_events = webnotes.conn.sql("""\
		SELECT COUNT(*) FROM `tabEvent`
		WHERE owner = %s
		AND event_type != 'Cancel'
		AND %s between date(starts_on) and date(ends_on)""", (
		webnotes.session.user, nowdate()))
	return todays_events[0][0]

def get_unread_messages():
	"returns unread (docstatus-0 messages for a user)"
	return webnotes.conn.sql("""\
		SELECT count(*)
		FROM `tabComment`
		WHERE comment_doctype IN ('My Company', 'Message')
		AND comment_docname = %s
		AND ifnull(docstatus,0)=0
		""", webnotes.user.name)[0][0]

for_module = {
	"To Do": get_things_todo,
	"Calendar": get_todays_events,
	"Messages": get_unread_messages
}
