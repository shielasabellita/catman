# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Categories"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Parent Group",
					"onboard": 1
				},
                {
                    "type": "doctype",
                    "name": "Item Group",
                    "onboard": 1
                },
                {
                    "type": "doctype",
                    "name": "Item Category",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Brand",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Item Form",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Item Subform",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Item Variant",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Item Size",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Item Color",
                    "onboard": 1,
                },
			]
		},
        {
            "label": _("Item"),
            "icon": "fa fa-star",
            "items": [
                {
                    "type": "doctype",
                    "name": "Categorized Item",
                    "onboard": 1
                }
            ]
        },
       {
           "label": _("Buying"),
           "icon": "fa fa-star",
           "items": [
                {
                   "type": "doctype",
                   "name": "X Transaction Settings",
                   "onboard": 1
               },
               {
                   "type": "doctype",
                   "name": "X Transaction",
                   "onboard": 1
               },{
                   "type": "doctype",
                   "name": "Supplier",
                   "onboard": 1
               }
           ]
       },
       {
           "label": _("Stock"),
           "icon": "fa fa-star",
           "items": [
               {
                   "type": "doctype",
                   "name": "Item",
                   "onboard": 1
               },
               {
                   "type": "doctype",
                   "name": "Item Price",
                   "onboard": 1
               },
               {
                   "type": "doctype",
                   "name": "Item Tax Template",
                   "onboard": 1
               },
               {
                   "type": "doctype",
                   "name": "UOM",
                   "onboard": 1
               }
           ]
       }

	]
