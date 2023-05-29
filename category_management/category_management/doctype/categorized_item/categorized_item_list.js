frappe.listview_settings['Categorized Item'] = {
    add_fields: ["item_code", "synced"],
    get_indicator: function(doc) {
        if (doc.synced == 1 ){
            return [__("Synced"), "green"];
        }else{
            return [__("Not Synced"), "orange"];
        }
    },
    onload(listview){
        listview.page.add_action_item('Bulk Sync to ERP', (event) => {
            let selected = []
            for (let check of event.view.cur_list.$checks) {
                selected.push(check.dataset.name);
            }

            frappe.call({
                method: "category_management.category_management.doctype.item.item.get_items",
                args: {barcodes: selected},
                callback: function(r){
                    if (r){
                        $.map(r.message, function(val, idx){
                            if (val.status_message == "Success"){
                                frappe.msgprint({
                                    title: __("Sync Success"),
                                    indicator: 'green',
                                    message: __(val.data)
                                });
                            }else{
                                frappe.msgprint({
                                    title: __("Syncing Failed on ERP"),
                                    indicator: 'red',
                                    message: __(val.data.err)
                                });
                            }
                        })
                        window.location.reload()
                    }
                }
            })
        });
    }
};