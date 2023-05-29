from __future__ import unicode_literals
import frappe
import json

from gaisano_erpv12.api.item import add_update_item
from category_management.catman_web.response import webResponse

@frappe.whitelist()
def addUpdateItem():
	try:
		data = json.loads(frappe.request.data)
		return webResponse(200, data=add_update_item(data))
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Failed to add Item from Sync")
		return webResponse(
			500,
			error="error_response",
			data={'message': 'error_response', 'err': str(e)},
			endpoint="get_page"
		)