import frappe

@frappe.whitelist()
def get_supplier_detail(supplier):
    return frappe.get_list("Supplier",{"name":supplier},['*'])