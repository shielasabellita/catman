# -*- coding: utf-8 -*-
# Copyright (c) 2021, Gaisano and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from category_management.scheduled_task import enqueue_available_stock_sync
class SyncSettings(Document):
	def force__eod_available_stock_syncing(self):
		enqueue_available_stock_sync()


