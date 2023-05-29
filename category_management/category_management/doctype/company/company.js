// Copyright (c) 2020, Gaisano and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company', {
	// refresh: function(frm) {

	// }
    delete_company_transaction:function (frm,cdt,cdn) {
        frappe.verify_password(function() {
			var d = frappe.prompt({
				fieldtype:"Data",
				fieldname: "company_name",
				label: __("Please re-type company name to confirm"),
				reqd: 1,
				description: __("Please make sure you really want to delete all the transactions for this company. Your master data will remain as it is. This action cannot be undone.")
			},
			function(data) {
				if(data.company_name !== frm.doc.name) {
					frappe.msgprint(__("Company name not same"));
					return;
				}
				frappe.call({
					method: "category_management.category_management.doctype.company.delete_company_transactions.delete_company_transactions",
					args: {
						company_name: data.company_name
					},
					freeze: true,
					callback: function(r, rt) {
						if(!r.exc)
							frappe.msgprint(__("Successfully deleted all transactions related to this company!"));
					},
					onerror: function() {
						frappe.msgprint(__("Wrong Password"));
					}
				});
			},
			__("Delete all the Transactions for this Company"), __("Delete")
			);
			d.get_primary_btn().addClass("btn-danger");
		});
    },

});
