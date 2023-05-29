# -*- coding: utf-8 -*-
# Copyright (c) 2020, Gaisano and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import json
class Brand(Document):


	def validate(self):
		cur_user = frappe.session.user
		headers = {'content-type': 'application/json', 'Accept': 'application/json'}
		session = requests.Session()
		erp_info = frappe.get_single("ERP Information")
		data = {
			"brand":self.name,
			"description":self.brand,
			"ignore_permissions":True,
			"disabled": self.disabled
		}

		if self.is_new():
			r = session.post('{0}/api/resource/Brand'.format(erp_info.url), data=json.dumps(data), headers=headers)
			if r.status_code not in [200, 201]:
				frappe.log_error(r.text, "ERP Sync Error (Create)")
				frappe.throw(r.text)
		else:
			headers2 = {
				'content-type': 'application/json', 
				'Accept': 'application/json',
				'Authorization': "token {}:{}".format(erp_info.api_key, erp_info.get_password('api_secret'))
			}
			u = session.put('{0}/api/method/gaisano_erpv12.api.api.update_brand'.format(erp_info.url), data=json.dumps(data), headers=headers2)
			if u.status_code not in [200, 201]:
				frappe.log_error(u.text, "ERP Sync Error (Update)")
				frappe.throw(u.text)
		