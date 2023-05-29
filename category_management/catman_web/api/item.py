import frappe
from frappe import _
from random import randint, randrange


def update_item(data):
    if data:
        frappe.db.set_value('Item', data['catman_item_code'], data['item'])

        template = "Item Tax Template - 12%" if data['item']['vat_nonvat'] == "VAT" else "VAT-Exempt"

        frappe.db.set_value("Item Tax", {"parent": data['item']['item_code']}, "item_tax_template", template)

        frappe.db.set_value("Item Supplier", {"parent": data['item']['item_code']}, {
            "supplier": data['supplier']['supplier'],
            "supplier_name": data['supplier']['supplier_name']
        })
        frappe.db.set_value("Categorized Item", {"item_code": data['item']['item_code']}, {
            "supplier": data['supplier']['supplier'],
            "vat_nonvat": data['item']['vat_nonvat'],
            "discount": data['item']['discount'],
        })
        insert_uom(data)
    else:
        frappe.throw(_("Please enter a valid data"))


def insert_uom(data):
    for d in data['uoms']:
        if not frappe.db.exists("UOM Conversion Detail", {"parent": data['item']['item_code'], "uom": d['uom']}):
            parent = [
                {
                    "parent": data['item']['item_code'],
                    "field": "uoms",
                    "parenttype": "Item"
                },
                {
                    "parent": data['barcode_retail'],
                    "field": "uoms",
                    "parenttype": "Categorized Item"
                }
            ]
            
            for p in parent:
                query = """
                INSERT INTO `tabUOM Conversion Detail` 
                (`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`,
                `parent`, `parentfield`, `parenttype`, `idx`, `conversion_factor`, `uom`) 
                VALUES 
                ("{name}", "{creation}", "{modified}", "{modified_by}", "{owner}", "{docstatus}",
                "{parent}", "{parentfield}", "{parenttype}", "{idx}", "{conversion_factor}", "{uom}")
                """.format(
                    name= randrange(1000000, 10000000) ,
                    creation= frappe.utils.now(),
                    modified= frappe.utils.now(),
                    modified_by= "Administrator",
                    owner= "Administrator",
                    docstatus= 0,
                    parent= p['parent'],
                    parentfield= p['field'],
                    parenttype= p['parenttype'],
                    idx= 1,
                    conversion_factor= d['conversion_factor'],
                    uom= d['uom'],
                )
                frappe.db.sql(query, as_dict=1)
                frappe.db.commit()
