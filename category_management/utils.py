import frappe
import json
import os
import math

@frappe.whitelist()
def get_reg_prov_city_brgy(region):
    # data = frappe.form_dict

    file = "/assets/category_management/files/region_province_city_brngy.json"
    path = os.getcwd() + file
    with open(path) as myjsonfile:
        places = json.load(myjsonfile)
        return places[region]


def get_erp_info():
    return frappe.get_single("ERP Information")

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10

def compute_margin(srp=0.00,buying_rate=0.00):
    if srp != 0.00:
        margin = ((float(srp) - float(buying_rate)) / float(srp))*100.00
    else:
        margin = 0.00
    return margin

def computed_mark_up_rate(srp=0.00,buying_rate=0.00):
    if srp != 0.00:
        mark_up_rate = ((float(srp) - float(buying_rate)) / float(buying_rate))*100.00
    else:
        mark_up_rate = 0.00
    return mark_up_rate

def compute_srp(discounted_rate=0.00,mark_up=0.00):
    srp = float(discounted_rate) + (float(discounted_rate) * (float(mark_up)/100.00))
    return srp

#Note: Depreciated code
def compute_srp_cmgn(discounted_rate=0.00):
    srp_cmgn = float(discounted_rate) + (float(discounted_rate) * float(0.5))
    return srp_cmgn

def compute_discounted_rate(buying_rate=0.00,cascading_total=0.00):
    discounted_rate = float(buying_rate) - (float(buying_rate) * (float(cascading_total)/100.00))
    return discounted_rate