frappe.listview_settings['Sales Order'] = {
	add_fields: ["base_grand_total", "customer_name", "currency", "delivery_date", "per_delivered", "per_billed",
		"status", "order_type", "per_ordered", "drop_ship"],
	get_indicator: function(doc) {
        if(doc.status==="Stopped") {
			return [__("Stopped"), "darkgrey", "status,=,Stopped"];

        } else if (doc.order_type !== "Maintenance" && doc.drop_ship !=1 
			&& flt(doc.per_delivered, 2) < 100 && frappe.datetime.get_diff(doc.delivery_date) < 0) {
			// to bill & overdue
			return [__("Overdue"), "red", "per_delivered,<,100|delivery_date,<,Today|status,!=,Stopped"];

		} else if (doc.order_type !== "Maintenance" && doc.drop_ship !=1 
			&& flt(doc.per_delivered, 2) < 100 && doc.status!=="Stopped") {
			// not delivered

			if(flt(doc.per_billed, 2) < 100) {
				// not delivered & not billed

				return [__("To Deliver and Bill"), "orange",
					"per_delivered,<,100|per_billed,<,100|status,!=,Stopped"];
			} else {
				// not delivered

				return [__("To Deliver"), "orange",
					"per_delivered,<,100|per_billed,=,100|status,!=,Stopped"];
			}

		} else if ((doc.order_type === "Maintenance" || flt(doc.per_delivered, 2) == 100 || 
			(doc.drop_ship == 1 && flt(doc.per_ordered, 2) == 100  ) ) && flt(doc.per_billed, 2) < 100 
			&& doc.status!=="Stopped") {

			// to bill
			return [__("To Bill"), "orange", "per_delivered,=,100|per_billed,<,100|status,!=,Stopped|per_ordered,<,100"];

		} else if((doc.order_type === "Maintenance" || flt(doc.per_delivered, 2) == 100)
			&& flt(doc.per_billed, 2) == 100 && doc.status!=="Stopped") {

			return [__("Completed"), "green", "per_delivered,=,100|per_billed,=,100|status,!=,Stopped"];
		} else if ( doc.drop_ship == 1 && flt(doc.per_delivered, 2) < 100 
			&& frappe.datetime.get_diff(doc.delivery_date) < 0) {
			// to bill & overdue
			return [__("Overdue"), "red", "per_ordered,<,100|delivery_date,<,Today|status,!=,Stopped"];

		} else if ( doc.drop_ship == 1 && flt(doc.per_ordered, 2) < 100 && doc.status!=="Stopped") {
			// not ordered
			
			if(flt(doc.per_billed, 2) < 100) {
				// not delivered & not billed

				return [__("To Order and Bill"), "orange",
					"per_ordered,<,100|per_billed,<,100|status,!=,Stopped"];
			} else {
				// not ordered

				return [__("To Order"), "orange",
					"per_ordered,<,100|per_billed,=,100|status,!=,Stopped"];
			}

		}
	},
	onload: function(listview) {
		var method = "erpnext.selling.doctype.sales_order.sales_order.stop_or_unstop_sales_orders";

		listview.page.add_menu_item(__("Set as Stopped"), function() {
			listview.call_for_selected_items(method, {"status": "Stop"});
		});

		listview.page.add_menu_item(__("Set as Unstopped"), function() {
			listview.call_for_selected_items(method, {"status": "Unstop"});
		});

	}
};
