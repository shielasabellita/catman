# -*- coding: utf-8 -*-
# Copyright (c) 2020, Gaisano and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Supplier(Document):
	pass
	# def validate(self):
	# 	self.supplier = self.name

@frappe.whitelist()
def getSupplier(supplier =  None):
	return frappe.db.sql(""" SELECT * from `tabSupplier` WHERE name = %s""", supplier, as_dict=1)