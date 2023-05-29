# -*- coding: utf-8 -*-
# Copyright (c) 2020, Gaisano and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from category_management.category_management.doctype import price_list
import frappe
import json, requests
from category_management.utils import get_erp_info
from frappe.model.document import Document
from frappe import _


erp_info = get_erp_info()

class Item(Document):

    def validate(self):
        self.item_code = self.name
        self.generate_item_prices()


    def generate_item_prices(self):
        for prices in eval(self.item_prices_data):
            item_price = frappe.get_value("Item Price", {
                            "price_list": prices['price_list'], 
                            "uom": prices['uom'], 
                            "item_code": self.item_code
                        })  

            if item_price:
                frappe.db.set_value("Item Price", item_price, {
                    "price_list": prices['price_list'], 
                    "uom": prices['uom'], 
                    "rate": prices['price'],
                    "item_code": self.item_code,
                    "item_name": self.item_name
                })
            else:
                item_price_doc = frappe.new_doc("Item Price")
                item_price_doc.price_list = prices['price_list']
                item_price_doc.uom = prices['uom']
                item_price_doc.rate = prices['price']
                item_price_doc.item_code = self.item_code
                item_price_doc.item_name = self.item_name
                item_price_doc.insert()


    def generate_stock_numberv2(self):
        for st_no in self.stock_number:
            if not frappe.db.exists("Stock Number V2","{0}:{1}".format(st_no, self.barcode_retail)) and self.from_x_trans == 0:
                doc = frappe.new_doc("Stock Number V2")
                doc.stock_number = str(st_no).strip()
                doc.categorized_item_id = str(self.name).strip()
                doc.insert()



    def on_trash(self):
        self.delete_item_prices()
		# self.sync_delete()


    def delete_item_prices(self):
        prices = frappe.get_list("Item Price", {"item_code": self.name})
        for p in prices:
            item_price = frappe.get_doc("Item Price", p['name'])
            item_price.delete()

        settings = frappe.get_single("Stock Settings")
        if settings.delete_category_item:
            if frappe.get_value("Categorized Item", {"item_code": self.name}):
                categorized_item = frappe.get_doc("Categorized Item", {"item_code": self.name})
                categorized_item.delete()


    def sync_delete(self):
        cur_user = frappe.session.user
        session = requests.Session()
        erp_info = frappe.get_single("ERP Information")

        headers = {
            'content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': "token {}:{}".format(erp_info.api_key, erp_info.get_password('api_secret'))
        }

        data = {
            "brand":self.name,
            "description":self.brand,
            "ignore_permissions":True
        }

        r = session.delete('{0}/api/resource/Item/'.format(erp_info.url), headers=headers)
        if r.status_code not in [200, 201]:
            frappe.log_error(r.text, "ERP Sync Error")
            frappe.throw(r.text)

    def set_vat_nonvat(self):
        template = "Item Tax Template - 12%" if self.vat_nonvat == "VAT" else "VAT-Exempt"

        self.taxes = []
        self.append("taxes", {
            "item_tax_template": template
        })


@frappe.whitelist()
def sync_item_to_erp(item_code, is_synced=False):
    if not erp_info.url:
        frappe.msgprint("Please add ERP url on ERP Information")

    data = get_data(item_code)

    url = erp_info.url + "/api/method/gaisano_erpv12.api.endpoints.item.addUpdateItem"
    headers = {
        'content-type': 'application/json',
        'Accept': 'application/json',
        'Authorization': "token {}:{}".format(erp_info.api_key, erp_info.get_password('api_secret'))
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code in [200, 201]:
            if not is_synced:
                frappe.db.sql("UPDATE tabItem set synced=1 WHERE name='{}'".format(item_code), as_dict=1)
                frappe.db.sql("UPDATE `tabCategorized Item` set synced=1 WHERE item_code='{}'".format(item_code), as_dict=1)
                frappe.db.commit()
        else:
            frappe.log_error(response.text, "Failed to Sync Item")

        return response.json()

    except:
        frappe.log_error(frappe.get_traceback(), "Failed to sync Item to ERP")
        frappe.msgprint(_("Failed to sync Item to ERP. Please see Error Log"))


def get_data(item_code):
    self = frappe.get_doc("Item", item_code)

    data = {}

    new_item = {
        "doctype": "Item",
        "catman_item_code": self.item_code,
        "naming_series": self.naming_series,
        "disabled": self.disabled,
        "item_name": self.item_name,
        "item_short_name": self.item_short_name,
        "description": self.description,
        "parent_item_group": self.parent_item_group,
        "item_group": self.item_group,
        "stock_uom": self.default_unit_measure,
        "vat_nonvat": self.vat_nonvat,
        "item_category": self.item_category,
        "brand": self.brand,
        "barcodes_retail": self.barcode_retail,
        "discount": self.discount,
        "barcodes": [],
        "stock_number": [],
        "taxes": [],
        "supplier_items": [],
        "uoms": [],
        "item_prices_table": self.item_prices_data,
        "owner": frappe.session.user,
        "modified_by": frappe.session.user
    }

    for i in self.uoms:
        new_item["uoms"].append({
            "uom": i.uom,
            "conversion_factor": i.conversion_factor
        })
    for i in self.barcodes:
        new_item["barcodes"].append({
            "barcode": i.barcode,
        })

    for i in self.stock_number:
        new_item["stock_number"].append({
        "stock_no": i.stock_no
        })

    for i in self.taxes:
        new_item["taxes"].append({
            "item_tax_template": i.item_tax_template
        })

    for i in self.supplier_items:
        new_item["supplier_items"].append({
            "supplier": i.supplier,
            "supplier_short_name": i.supplier_name,
        })

    data = new_item

    return data


@frappe.whitelist()
def get_srp(item_code=None,uom=None,branch=None,get_all=False):
    if not get_all:
        rate = frappe.get_list("Item Price",{"price_list":"SRP - {0} - Dept Store".format(branch),"item_code":item_code,"uom":uom},["rate"])
        print(item_code)
        print(branch)
        print(uom)
        print(rate)
        if rate:
            return rate[0].rate
        else:
            return 0
@frappe.whitelist()
def update_stock_uom_rate(item_code,stock_uom,uom,rate=0.00,total_discount=0.00,selling_conversion_factor=1):
    print(uom)
    response = {
        'stock_uom_rate': float(rate),
        'discounted_rate': float(rate) - (float(rate) * (float(total_discount)/100)),
       
    }
    if stock_uom != uom:
        conversion_factor = frappe.db.sql("SELECT conversion_factor FROM `tabUOM Conversion Detail` WHERE uom = '{0}' AND parent = '{1}'".format(uom,item_code),as_dict=1)
        stock_uom_rate = float(rate) / (conversion_factor[0].conversion_factor if conversion_factor else 1)
        response['discounted_rate'] = float(rate) - (float(rate) * (float(total_discount)/100))
        response['stock_uom_rate'] = stock_uom_rate
    response['buying_rate_base_on_selling_uom'] = float(selling_conversion_factor) * float(response['stock_uom_rate'] )
    return response


@frappe.whitelist()
def get_items(barcodes):
    barcodes = json.loads(barcodes)

    msg = []
    for bd in barcodes:
        item = frappe.get_value("Categorized Item", bd, ['synced', 'item_code'], as_dict=1)
        msg.append(sync_item_to_erp(item['item_code']))

    return msg