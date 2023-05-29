import frappe


@frappe.whitelist()
def md_item_under_discount_get_all(discount_id):
	return frappe.db.sql(""" SELECT DISTINCT * FROM `tabMD Item Under Discount` WHERE parent =%s""", discount_id, as_dict=1)

@frappe.whitelist()
def item_by_supplier(supplier = None):
	return frappe.db.sql("""Select parent from `tabItem Supplier` where supplier= %s""", supplier, as_dict = 1)