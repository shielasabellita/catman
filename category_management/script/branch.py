import frappe

@frappe.whitelist()
def read_all_branch():
    return frappe.get_list("Branch",{},['*'],order_by='name')
