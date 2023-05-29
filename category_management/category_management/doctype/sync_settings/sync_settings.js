// Copyright (c) 2021, Gaisano and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sync Settings', {
    refresh: function(frm) {
        cur_frm.set_query("warehouse", "warehouse", function(doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                        ['Warehouse', 'branch', '=', d.branch],

                    ]
            }
        });
    },
    force__eod_available_stock_syncing:function (frm,cdt,cdn) {
        frappe.msgprint("Executing Available Stock Syncing in Que");
        frappe.call({
            method:'force__eod_available_stock_syncing',
            doc:frm.doc,
            callback:function (r) {

            }
        });

    }
});
