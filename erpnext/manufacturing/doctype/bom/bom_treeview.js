frappe.treeview_settings["BOM"] = {
	get_tree_nodes: 'erpnext.manufacturing.page.bom_browser.bom_browser.get_children',
	filters: [
		{
			fieldname: "bom",
			fieldtype:"Link",
			options: "BOM",
			label: __("BOM")
		}
	],
	breadcrumb: "Manufacturing",
	disable_add_node: true,
	label: "bom", // should be fieldname from filters
	get_label: function(node) {
		if(node.data.qty) {
			return node.data.qty + " x " + node.data.item_code;
		} else {
			return node.data.item_code || node.data.value;
		}
	},
	toolbar: [
		{toggle_btn: true},
		{
			label:__("Edit"),
			condition: function(node) {
				return node.expandable;
			},
			click: function(node) {
				
				frappe.set_route("Form", "BOM", node.data.value);
			}
		}
	],
}