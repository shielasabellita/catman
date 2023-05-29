// Copyright (c) 2020, GAMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('X Transaction Settings', {
	refresh: function(frm) {
        cur_frm.set_query("warehouse", "purchase_order_warehouse", function(doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                        ['Warehouse', 'branch', '=', d.branch],

                    ]
            }
        });
    }
});
