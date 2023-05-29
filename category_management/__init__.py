# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '0.0.1'


import requests, frappe, json
from category_management.executables import *
def update_items_synced(limit):
    from category_management.utils import get_erp_info
    settings = get_erp_info()

    items = frappe.db.sql("select barcode_retail, name from tabItem where synced=0 limit {}".format(limit), as_dict=1)
    for i in items:
        url = settings.url + "/api/method/gaisano_erpv12.api.api"
        erp_item = requests.post(url+".get_item", data=json.dumps({"barcode_retail": i['barcode_retail']}))
        if erp_item.status_code in (200,201):
            frappe.db.set_value("Item", i['name'], "synced", 1, update_modified=False)
            frappe.db.set_value("Categorized Item", {"item_code": i['name']}, "synced", 1, update_modified=False)


