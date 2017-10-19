QUnit.test("test: operation", function (assert) {
	assert.expect(2);
	let done = assert.async();
	frappe.run_serially([
		// test operation creation
		() => frappe.set_route("List", "Operation"),

		// Create a Keyboard operation
		() => {
			frappe.tests.make(
				"Operation", [
					{__newname: "Assemble Keyboard"},
					{workstation: "Keyboard assembly workstation"}
				]
			);
		},
		() => frappe.timeout(1),
		() => {
			assert.ok(cur_frm.docname.includes('Assemble Keyboard'),
				'Assemble Keyboard created successfully');
			assert.ok(cur_frm.doc.workstation.includes('Keyboard assembly workstation'),
				'Keyboard assembly workstation was linked successfully');
		},

		// Create a Screen operation
		() => {
			frappe.tests.make(
				"Operation", [
					{__newname: 'Assemble Screen'},
					{workstation: "Screen assembly workstation"}
				]
			);
		},
		() => frappe.timeout(1),

		// Create a CPU operation
		() => {
			frappe.tests.make(
				"Operation", [
					{__newname: 'Assemble CPU'},
					{workstation: "CPU assembly workstation"}
				]
			);
		},
		() => frappe.timeout(1),

		() => done()
	]);
});
