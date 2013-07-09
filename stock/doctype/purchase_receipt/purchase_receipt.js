// ERPNext - web based ERP (http://erpnext.com)
// Copyright (C) 2012 Web Notes Technologies Pvt Ltd
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

cur_frm.cscript.tname = "Purchase Receipt Item";
cur_frm.cscript.fname = "purchase_receipt_details";
cur_frm.cscript.other_fname = "purchase_tax_details";

wn.require('app/accounts/doctype/purchase_taxes_and_charges_master/purchase_taxes_and_charges_master.js');
wn.require('app/utilities/doctype/sms_control/sms_control.js');
wn.require('app/buying/doctype/purchase_common/purchase_common.js');

wn.provide("erpnext.stock");
erpnext.stock.PurchaseReceiptController = erpnext.buying.BuyingController.extend({
	refresh: function() {
		this._super();
		
		if(this.frm.doc.docstatus == 1) {
			if(flt(this.frm.doc.per_billed, 2) < 100) {
				cur_frm.add_custom_button('Make Purchase Invoice', 
					this.make_purchase_invoice);
			}
			cur_frm.add_custom_button('Send SMS', cur_frm.cscript['Send SMS']);
		}

		cur_frm.add_custom_button(wn._('From Purchase Order'), 
			function() {
				wn.model.map_current_doc({
					method: "buying.doctype.purchase_order.purchase_order.make_purchase_receipt",
					source_doctype: "Purchase Order",
					get_query_filters: {
						supplier: cur_frm.doc.supplier || undefined,
						docstatus: 1,
						status: ["!=", "Stopped"],
						per_received: ["<", 99.99],
						company: cur_frm.doc.company
					}
				})
			});


		if(wn.boot.control_panel.country == 'India') {
			unhide_field(['challan_no', 'challan_date']);
		}
	},
	
	received_qty: function(doc, cdt, cdn) {
		var item = wn.model.get_doc(cdt, cdn);
		wn.model.round_floats_in(item, ["qty", "received_qty"]);

		item.qty = (item.qty < item.received_qty) ? item.qty : item.received_qty;
		this.qty(doc, cdt, cdn);
	},
	
	qty: function(doc, cdt, cdn) {
		var item = wn.model.get_doc(cdt, cdn);
		wn.model.round_floats_in(item, ["qty", "received_qty"]);
		
		if(item.qty > item.received_qty) {
			msgprint(wn._("Error") + ": " + wn._(wn.meta.get_label(item.doctype, "qty", item.name))
				+ " > " + wn._(wn.meta.get_label(item.doctype, "received_qty", item.name)));
			item.qty = item.rejected_qty = 0.0;
		} else {
			item.rejected_qty = flt(item.received_qty - item.qty, precision("rejected_qty", item));
		}
		
		this._super();
	},
	
	rejected_qty: function(doc, cdt, cdn) {
		var item = wn.model.get_doc(cdt, cdn);
		wn.model.round_floats_in(item, ["received_qty", "rejected_qty"]);
		
		if(item.rejected_qty > item.received_qty) {
			msgprint(wn._("Error") + ": " + 
				wn._(wn.meta.get_label(item.doctype, "rejected_qty", item.name))
				+ " > " + wn._(wn.meta.get_label(item.doctype, "received_qty", item.name)));
			item.qty = item.rejected_qty = 0.0;
		} else {
			item.qty = flt(item.received_qty - item.rejected_qty, precision("qty", item));
		}
		
		this.qty(doc, cdt, cdn);
	},
	
	make_purchase_invoice: function() {
		wn.model.open_mapped_doc({
			method: "stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice",
			source_name: cur_frm.doc.name
		})
	}, 

	tc_name: function() {
		this.get_terms();
	},
		
});

// for backward compatibility: combine new and previous states
$.extend(cur_frm.cscript, new erpnext.stock.PurchaseReceiptController({frm: cur_frm}));

cur_frm.cscript.supplier_address = cur_frm.cscript.contact_person = function(doc,dt,dn) {		
	if(doc.supplier) get_server_fields('get_supplier_address', JSON.stringify({supplier: doc.supplier, address: doc.supplier_address, contact: doc.contact_person}),'', doc, dt, dn, 1);
}

cur_frm.fields_dict['supplier_address'].get_query = function(doc, cdt, cdn) {
	return 'SELECT name,address_line1,city FROM tabAddress WHERE supplier = "'+ doc.supplier +'" AND docstatus != 2 AND name LIKE "%s" ORDER BY name ASC LIMIT 50';
}

cur_frm.fields_dict['contact_person'].get_query = function(doc, cdt, cdn) {
	return 'SELECT name,CONCAT(first_name," ",ifnull(last_name,"")) As FullName,department,designation FROM tabContact WHERE supplier = "'+ doc.supplier +'" AND docstatus != 2 AND name LIKE "%s" ORDER BY name ASC LIMIT 50';
}

cur_frm.cscript.new_contact = function(){
	tn = wn.model.make_new_doc_and_get_name('Contact');
	locals['Contact'][tn].is_supplier = 1;
	if(doc.supplier) locals['Contact'][tn].supplier = doc.supplier;
	loaddoc('Contact', tn);
}

cur_frm.fields_dict['purchase_receipt_details'].grid.get_field('project_name').get_query = function(doc, cdt, cdn) {
	return 'SELECT `tabProject`.name FROM `tabProject` \
		WHERE `tabProject`.status not in ("Completed", "Cancelled") \
		AND `tabProject`.name LIKE "%s" ORDER BY `tabProject`.name ASC LIMIT 50';
}

cur_frm.fields_dict['purchase_receipt_details'].grid.get_field('batch_no').get_query= function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	if(d.item_code){
		return "SELECT tabBatch.name, tabBatch.description FROM tabBatch WHERE tabBatch.docstatus != 2 AND tabBatch.item = '"+ d.item_code +"' AND `tabBatch`.`name` like '%s' ORDER BY `tabBatch`.`name` DESC LIMIT 50"
	}
	else{
		alert("Please enter Item Code.");
	}
}

cur_frm.cscript.select_print_heading = function(doc,cdt,cdn){
	if(doc.select_print_heading){
		// print heading
		cur_frm.pformat.print_heading = doc.select_print_heading;
	}
	else
		cur_frm.pformat.print_heading = "Purchase Receipt";
}

cur_frm.fields_dict['select_print_heading'].get_query = function(doc, cdt, cdn) {
	return 'SELECT `tabPrint Heading`.name FROM `tabPrint Heading` WHERE `tabPrint Heading`.docstatus !=2 AND `tabPrint Heading`.name LIKE "%s" ORDER BY `tabPrint Heading`.name ASC LIMIT 50';
}

cur_frm.fields_dict.purchase_receipt_details.grid.get_field("qa_no").get_query = function(doc) {
	return 'SELECT `tabQuality Inspection`.name FROM `tabQuality Inspection` WHERE `tabQuality Inspection`.docstatus = 1 AND `tabQuality Inspection`.%(key)s LIKE "%s"';
}

cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	if(cint(wn.boot.notification_settings.purchase_receipt)) {
		cur_frm.email_doc(wn.boot.notification_settings.purchase_receipt_message);
	}
}
