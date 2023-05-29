# -*- coding: utf-8 -*-
# Copyright (c) 2021, Gaisano and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from category_management.api import add_stock_v2
class StockNumberV2(Document):
	def validate(self):
		if self.created_from == "X Transaction":
			doc = frappe.get_doc("Categorized Item", self.categorized_item_id)
			doc.stock_number = "{0},{1}".format(doc.stock_number.strip(), self.stock_number.strip())
			doc.from_x_trans = 1
			doc.save()
		add_stock_v2(self)

		

