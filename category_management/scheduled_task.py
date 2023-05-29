import frappe
from category_management.category_management.doctype.x_transaction.x_transaction import get_available_stock
from category_management.api import erp_login

@frappe.whitelist()
def update_available_stock(item_code,warehouse):
    try:
        qty = get_available_stock(item_code = item_code, warehouse = warehouse,session=erp_login())['data'][0]['actual_qty']
    except:
        #If tabBin doesn't have actual_qty of an item, JSON response will not return array data so set instantly to 0
        qty = 0


    available_stock_entry = frappe.get_list('Available Stock',filters={'item_code':item_code,'warehouse':warehouse},fields=['qty'])

    if not available_stock_entry:
        doc = frappe.new_doc('Available Stock')
        doc.item_code = item_code
        doc.warehouse = warehouse
        doc.uom = 'Unit'
        doc.qty = qty
        doc.insert()
    else:
        doc = frappe.get_doc('Available Stock',"{0}-{1}".format(item_code,warehouse))
        doc.qty = qty
        doc.save()

#Function executed daily(12:00 AM) if EOD_ITEM_SYNCING is enabled
@frappe.whitelist()
def available_stock_sync():
    sync_settings = frappe.get_single("Sync Settings")

    if sync_settings.eod_item_syncing:
        items = frappe.get_all("Item",  filters={'disabled': 0},fields=['name'])
        warehouses = frappe.get_all("Warehouse", filters={'is_group': 0, 'disabled': 0}, fields=['name'])
        for warehouse in sync_settings.warehouse:
            print(warehouse.warehouse)
            for item in items:
                print(item.name)
                try:
                    frappe.enqueue('category_management.scheduled_task.update_available_stock',item_code=item.name,warehouse=warehouse.warehouse)
                except:
                    frappe.log_error(frappe.get_traceback(), 'failed daily available stock sync')
#Function for Force EOD Available Stock Sync in Sync Settings
@frappe.whitelist()
def enqueue_available_stock_sync():
    frappe.enqueue(available_stock_sync())