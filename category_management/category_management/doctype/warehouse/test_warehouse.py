# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
# from __future__ import unicode_literals
# from frappe.model.rename_doc import rename_doc
# from erpnext.stock.doctype.stock_entry.stock_entry_utils import make_stock_entry
# from frappe.utils import cint
# from erpnext import set_perpetual_inventory
# from frappe.test_runner import make_test_records
# from erpnext.accounts.doctype.account.test_account import get_inventory_account, create_account
#
# import erpnext
# import frappe
import unittest
# test_records = frappe.get_test_records('Warehouse')

class TestWarehouse(unittest.TestCase):
	pass
# 	def setUp(self):
# 		if not frappe.get_value('Item', '_Test Item'):
# 			make_test_records('Item')
#
# 	def test_parent_warehouse(self):
# 		parent_warehouse = frappe.get_doc("Warehouse", "_Test Warehouse Group - _TC")
# 		self.assertEqual(parent_warehouse.is_group, 1)
#
# 	def test_warehouse_hierarchy(self):
# 		p_warehouse = frappe.get_doc("Warehouse", "_Test Warehouse Group - _TC")
#
# 		child_warehouses =  frappe.db.sql("""select name, is_group, parent_warehouse from `tabWarehouse` wh
# 			where wh.lft > %s and wh.rgt < %s""", (p_warehouse.lft, p_warehouse.rgt), as_dict=1)
#
# 		for child_warehouse in child_warehouses:
# 			self.assertEqual(p_warehouse.name, child_warehouse.parent_warehouse)
# 			self.assertEqual(child_warehouse.is_group, 0)
#
# 	def test_warehouse_renaming(self):
# 		set_perpetual_inventory(1)
# 		create_warehouse("Test Warehouse for Renaming 1")
# 		account = get_inventory_account("_Test Company", "Test Warehouse for Renaming 1 - _TC")
# 		self.assertTrue(frappe.db.get_value("Warehouse", filters={"account": account}))
#
# 		# Rename with abbr
# 		if frappe.db.exists("Warehouse", "Test Warehouse for Renaming 2 - _TC"):
# 			frappe.delete_doc("Warehouse", "Test Warehouse for Renaming 2 - _TC")
# 		rename_doc("Warehouse", "Test Warehouse for Renaming 1 - _TC", "Test Warehouse for Renaming 2 - _TC")
#
# 		self.assertTrue(frappe.db.get_value("Warehouse",
# 			filters={"account": "Test Warehouse for Renaming 1 - _TC"}))
#
# 		# Rename without abbr
# 		if frappe.db.exists("Warehouse", "Test Warehouse for Renaming 3 - _TC"):
# 			frappe.delete_doc("Warehouse", "Test Warehouse for Renaming 3 - _TC")
#
# 		rename_doc("Warehouse", "Test Warehouse for Renaming 2 - _TC", "Test Warehouse for Renaming 3")
#
# 		self.assertTrue(frappe.db.get_value("Warehouse",
# 			filters={"account": "Test Warehouse for Renaming 1 - _TC"}))
#
# 		# Another rename with multiple dashes
# 		if frappe.db.exists("Warehouse", "Test - Warehouse - Company - _TC"):
# 			frappe.delete_doc("Warehouse", "Test - Warehouse - Company - _TC")
# 		rename_doc("Warehouse", "Test Warehouse for Renaming 3 - _TC", "Test - Warehouse - Company")
#
# 	def test_warehouse_merging(self):
# 		set_perpetual_inventory(1)
#
# 		create_warehouse("Test Warehouse for Merging 1")
# 		create_warehouse("Test Warehouse for Merging 2")
#
# 		make_stock_entry(item_code="_Test Item", target="Test Warehouse for Merging 1 - _TC",
# 			qty=1, rate=100)
# 		make_stock_entry(item_code="_Test Item", target="Test Warehouse for Merging 2 - _TC",
# 			qty=1, rate=100)
#
# 		existing_bin_qty = (
# 			cint(frappe.db.get_value("Bin",
# 				{"item_code": "_Test Item", "warehouse": "Test Warehouse for Merging 1 - _TC"}, "actual_qty"))
# 			+ cint(frappe.db.get_value("Bin",
# 				{"item_code": "_Test Item", "warehouse": "Test Warehouse for Merging 2 - _TC"}, "actual_qty"))
# 		)
#
# 		rename_doc("Warehouse", "Test Warehouse for Merging 1 - _TC",
# 			"Test Warehouse for Merging 2 - _TC", merge=True)
#
# 		self.assertFalse(frappe.db.exists("Warehouse", "Test Warehouse for Merging 1 - _TC"))
#
# 		bin_qty = frappe.db.get_value("Bin",
# 			{"item_code": "_Test Item", "warehouse": "Test Warehouse for Merging 2 - _TC"}, "actual_qty")
#
# 		self.assertEqual(bin_qty, existing_bin_qty)
#
# 		self.assertTrue(frappe.db.get_value("Warehouse",
# 			filters={"account": "Test Warehouse for Merging 2 - _TC"}))
#
# def create_warehouse(warehouse_name, properties=None, company=None):
# 	if not company:
# 		company = "_Test Company"
#
# 	warehouse_id = erpnext.encode_company_abbr(warehouse_name, company)
# 	if not frappe.db.exists("Warehouse", warehouse_id):
# 		w = frappe.new_doc("Warehouse")
# 		w.warehouse_name = warehouse_name
# 		w.parent_warehouse = "_Test Warehouse Group - _TC"
# 		w.company = company
# 		make_account_for_warehouse(warehouse_name, w)
# 		w.account = warehouse_id
# 		if properties:
# 			w.update(properties)
# 		w.save()
# 		return w.name
# 	else:
# 		return warehouse_id
#
# def make_account_for_warehouse(warehouse_name, warehouse_obj):
# 	if not frappe.db.exists("Account", warehouse_name + " - _TC"):
# 		parent_account = frappe.db.get_value('Account',
# 			{'company': warehouse_obj.company, 'is_group':1, 'account_type': 'Stock'},'name')
# 		account = create_account(account_name=warehouse_name, \
# 				account_type="Stock", parent_account= parent_account, company=warehouse_obj.company)