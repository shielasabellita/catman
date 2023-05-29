# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
# import erpnext
from frappe.utils import cint, nowdate
from frappe import throw, _
from frappe.utils.nestedset import NestedSet
# from erpnext.stock import get_warehouse_account
from frappe.contacts.address_and_contact import load_address_and_contact

class Warehouse(NestedSet):
	nsm_parent_field = 'parent_warehouse'

	def autoname(self):
		if self.company:
			suffix = " - G"  
			if not self.warehouse_name.endswith(suffix):
				self.name = self.warehouse_name + suffix
		else:
			self.name = self.warehouse_name

	