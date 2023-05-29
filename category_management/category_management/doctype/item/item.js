// Copyright (c) 2020, Gaisano and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item', {
	refresh: function(frm) {
        frm.add_custom_button("Sync to ERP", function(){
            frappe.show_progress(__('Syncing to ERP. Please wait.'), 99, 100);
            if(!frm.is_new()) {
                frappe.call({
                    method: "category_management.category_management.doctype.item.item.sync_item_to_erp",
                    args: {"item_code": frm.doc.item_code},
                    callback: function (r) {
                        setTimeout(function () {
                            location.reload();
                        }, 1500);
                    }
                })
            }
        }).addClass("btn-primary");
        if (frappe.session.user != "Administrator")
            frappe.model.get_value("User", {'name': frappe.session.user}, ['name','role_profile_name'], function(r){
                var hidden = r.role_profile_name == 'System Administrator' ? 0 : 1
                frm.set_df_property('item_prices_table', 'hidden', hidden)
            })
	},

    vat_nonvat: function(frm) {
        if (frm.doc.vat_nonvat == 'VAT - Exempt') {
            cur_frm.clear_table("taxes");
            var row = frappe.model.add_child(cur_frm.doc, "Item Tax", "taxes");
            row.item_tax_template = "VAT-Exempt";
        } else {
            cur_frm.clear_table("taxes");
        }
        cur_frm.refresh_field("taxes");
    }
});
