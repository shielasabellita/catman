# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
        {
            "label": _("X Transaction"),
            "icon": "fa fa-star",
            "items": [
                {
                    "type": "doctype",
                    "name": "X Purchase Order",
                    "onboard": 1
                }
            ]
        }

	]
