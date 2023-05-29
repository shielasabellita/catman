import frappe
from frappe import _

def add_update_item_price(data):
    if not frappe.db.exists("Item Price", {"item_code": data['item_code'], "price_list": data['price_list'], "uom":data['uom']}):
        add_item_price(data)
        return "Item Code {} Price list {} successfully created on Catman".format(data['item_code'], data['price_list'])
    else:
        update_item_price(data)
        return "Item Price {} successfully updated on CatMan".format(data['item_code'])

def add_item_price(data):
    doc = frappe.new_doc("Item Price")
    doc.item_code = data['item_code']
    doc.price_list = data['price_list']
    doc.uom  = data['uom']
    doc.rate = data['price_list_rate']
    doc.save()

def update_item_price(data):
    if data['stock_uom'] == data['uom'] and data['price_list'] == "Standard Buying":
        frappe.db.set_value("Categorized Item",data['barcode'],"price",data['price_list_rate'],update_modified=False) 

    item_price = frappe.db.sql("""SELECT name FROM `tabItem Price` 
                     where item_code = %s and price_list =%s and uom =%s""",
                     (data['item_code'],data['price_list'], data['uom']), as_dict=1)
    doc = frappe.get_doc("Item Price",item_price[0].name)
    doc.rate = data['price_list_rate']
    doc.save()
    