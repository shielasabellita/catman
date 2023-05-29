# -*- coding: utf-8 -*-
# Copyright (c) 2020, Gaisano and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from category_management.category_management.doctype import price_list
import frappe
from frappe.model.document import Document
import random, string, json
from frappe import _
from category_management.category_management.doctype.item.item import sync_item_to_erp
from frappe.model.naming import make_autoname



class CategorizedItem(Document):
    def before_rename(self, *args, **kwargs):
        rename_data = []
        for i in args:
            rename_data.append(i)

        item_doc = frappe.get_doc("Item",{'barcode_retail':args[0]})
        frappe.db.set_value("Categorized Item", args[0],{'categorized_item_id':rename_data[1],'supplier_barcode':rename_data[1],'barcode_svg':rename_data[1],'barcode_retail':rename_data[1]},update_modified=False)
        item_doc.barcode_retail = args[1]
        row = item_doc.append("barcodes",{})
        row.barcode = args[1]
        
        item_doc.save()


        #To add stock number when barcode is changed
        stock_nos = self.stock_number.split(",")
        for st_no in stock_nos:
            
            if not frappe.db.exists("Stock Number V2","{0}:{1}".format(st_no, rename_data[1])) and self.from_x_trans == 0:
                print("CREATING STOCK NO FOR {0}".format(rename_data[1]))
                doc = frappe.new_doc("Stock Number V2")
                doc.stock_number = str(st_no).strip()
                doc.categorized_item_id = str(rename_data[1]).strip()
                doc.insert()


    def autoname(self):
        self.name = self.validate_name()

    
    def validate_name(self):
        if self.has_supplier_barcode: 
            if len(self.supplier_barcode) < 13:
                return str(self.supplier_barcode).zfill(13)

            elif len(self.supplier_barcode) == 13:
                return self.supplier_barcode

            elif len(self.supplier_barcode) > 13:
                frappe.throw(_("Supplier Barcode <strong>{}</strong> has more than 13 digits".format(self.supplier_barcode)))
        else:
            frappe_name = make_autoname("9898.########", "", self)

            return get_check_digit(frappe_name) #frappe_name+str(suffix_num)


    def validate(self):
        self.categorized_item_id = self.name
        self.barcode_svg = self.name
        self.barcode_retail = self.name
        self.date_created = self.creation


        #specified here cause multiple ternary operation can't be executed in CONCAT
        item_group = " {}".format(self.item_group) if self.item_group != "(BLANK)" else ""
        item_group_shortname = " {}".format(self.item_group_shortname) if self.item_group_shortname != "(BLANK)" else ""
        brand = " {}".format(self.brand) if self.brand != "(BLANK)" else ""
        # item_category = self.item_category if self.item_category != "(BLANK)" else ""
        item_form = " {}".format(self.item_form) if self.item_form != "(BLANK)" else ""
        item_form_shortname = " {}".format(self.item_form_shortname) if self.item_form_shortname != "(BLANK)" else ""

        item_subform = " {}".format(self.item_subform) if self.item_subform != "(BLANK)" else ""
        item_variant = " {}".format(self.item_variant) if self.item_variant != "(BLANK)" else ""
        item_size = " {}".format(self.item_size) if self.item_size != "(BLANK)" else ""
        item_size_shortname = " {}".format(self.item_size_shortname) if self.item_size_shortname != "(BLANK)" else ""
        item_color = " {}".format(self.item_color) if self.item_color != "(BLANK)" else ""
        item_color_shortname = " {}".format(self.item_color_shortname) if self.item_color_shortname != "(BLANK)" else ""



        #if data import dont concat new description, if new from system then concat new one
        #Note: used different variable for desc,name,shortname cause is still subject to change.
        if not self.item_description:
        
            self.item_description = item_group_shortname +  brand + item_form + item_subform + item_variant + item_size + item_color
            self.item_shortname = item_group_shortname +    brand + item_form_shortname + item_subform + item_variant + item_size_shortname + item_color_shortname
            self.item_name = item_group_shortname +  brand + item_form + item_subform + item_variant + item_size + item_color
        else:
            self.item_shortname = item_group_shortname +   brand + item_form_shortname + item_subform + item_variant + item_size_shortname + item_color_shortname
            self.item_name = item_group_shortname + brand + item_form + item_subform + item_variant + item_size + item_color
            # for description edit  
            if not self.is_new():
                self.item_description = item_group_shortname +  brand + item_form + item_subform + item_variant + item_size + item_color
            

        item_doc = self.sync_to_item()
        self.item_code = item_doc.item_code

        self.sync_to_erp()

    def before_insert(self):
        self.validate_duplicate()

    def validate_duplicate(self):
        filters = {
            "item_category_link":self.item_category_link,
            "brand_link":self.brand_link,
            "item_form_link":self.item_form_link,
            "item_subform_link":self.item_subform_link,
            "item_variant_link":self.item_variant_link,
            "item_size_link":self.item_size_link,
            "item_color_link":self.item_color_link,
        }

        item = frappe.get_value("Categorized Item", filters=filters)
        if item and self.is_new():
            reference_link = '<a href="/desk#Form/{0}/{1}">{1}</a>'.format("Categorized Item", item)
            frappe.throw(_("Item already exist. Please update the Item {} and add the stock number separated with comma.".format(reference_link)))


    def sync_to_item(self):
        item_code = frappe.get_value("Item", {"barcode_retail": self.name})
        if item_code or self.item_code:
            get_item_code = self.item_code if self.item_code else item_code
            item_doc = frappe.get_doc("Item", get_item_code)
            print("existing item", item_doc)
        else:
            item_doc = frappe.new_doc("Item")
            print("new_item", item_doc)
            

        price_lists = frappe.db.sql("""select name from `tabPrice List` where 
            name not like '%Grocery%' and name not like '%Standard Selling%' and name not in ('SRP', 'SRP CMGN', 'Standard Buying 2', 'Fresh Buying', 
            'Inventory Transfer - Fresh', 'Fresh Selling - InterCompany', 'Standard Selling') """, as_dict=1)
        
        price_list = []
        for p in price_lists:
            price_list.append(p['name'])


        if not self.item_shortname:
            self.item_shortname = ""
        
        uoms = []
        for uom in self.uoms:
            uoms.append({
                "uom": uom.uom,
                "conversion_factor": uom.conversion_factor
            })

        stock_nos = self.stock_number.split(",")
        stock_number = []
        for st_no in stock_nos:
            stock_number.append({
                "stock_no": st_no
            })

            if not frappe.db.exists("Stock Number V2","{0}:{1}".format(st_no, self.name)) and self.from_x_trans == 0:
                doc = frappe.new_doc("Stock Number V2")
                doc.stock_number = str(st_no).strip()
                doc.categorized_item_id = str(self.name).strip()
                doc.insert()


        item_prices = []
        for price in price_list:
            rate = self.price * uoms[0]['conversion_factor'] if price in ('Standard Buying', 'Inventory Transfer') else 0 # calculated price
            basic_rate = self.price * uoms[0]['conversion_factor'] if price in ('Standard Buying', 'Inventory Transfer') else 0
            if self.vat_nonvat == "VAT":
                if price == "Inventory Transfer":
                    rate = rate / 1.12 # calculated price

            item_prices.append({
                    "price_list":price,
                    "rate": basic_rate,
                    "price": rate, #calculated price
                    "uom": uoms[0]['uom'],
                    "synced": 1
                })

        item_doc.update({
            "disabled": self.disabled,
            "item_name": self.item_name,
            "item_short_name": self.item_shortname,
            "item_category":self.item_category,
            "brand": self.brand_link,
            "description": self.item_description,
            "parent_item_group": self.parent_group,
            "item_group": self.item_group,
            "default_unit_measure": uoms[0]['uom'],
            "vat_nonvat": self.vat_nonvat,
            "uoms": uoms,
            "barcode_retail": self.name,
            "discount": self.discount,
            "barcodes": [{
                "barcode": self.name
            }],
            "taxes": [{
                "item_tax_template": "Item Tax Template - 12%" if self.vat_nonvat == "VAT" else "VAT-Exempt"
            }],
            "supplier_items": [{
                "supplier": self.supplier
            }],
            "stock_number": stock_number,
            "item_prices_data": str(item_prices)
        })

        item_doc.save()

        return item_doc


    def sync_to_erp(self):
        if self.item_code and self.synced == 1:
            sync_item_to_erp(self.item_code, is_synced=True)

    def generate_code(self):

        item_group_code = frappe.get_value("Item Group",self.item_group,'item_group_code')
        item_category_code = None if not self.item_category else frappe.get_value("Item Category", self.item_group+"-"+self.item_category,'item_category_code')
        item_form_code = None if not self.item_form else frappe.get_value("Item Form", self.item_group+"-"+self.item_category+"-"+self.item_form,'item_form_code')
        item_subform_code = None if not self.item_subform else frappe.get_value("Item Subform", self.item_group+"-"+self.item_category+"-"+self.item_form+"-"+self.item_subform,'item_subform_code')
        item_size_code = None if not self.item_size else frappe.get_value("Item Size",self.item_size,'item_size_code')
        item_variant_code = None if not self.item_variant else frappe.get_value("Item Variant",self.item_group+"-"+self.item_category+"-"+self.item_form+"-"+self.item_subform+"-"+self.item_variant,'item_variant_code')
        item_color_code = None if not self.item_color else frappe.get_value("Item Color",self.item_color,'item_color_code')
        brand_code = None if not self.brand else frappe.get_value("Brand",self.brand,'brand_code')

        item_group_code = str(item_group_code) if item_group_code else "00"
        item_category_code = str(item_category_code) if item_category_code else "00"
        item_form_code = str(item_form_code) if item_form_code else "00"
        item_subform_code = str(item_subform_code) if item_subform_code else "00"
        item_size_code= str(item_size_code) if item_size_code else "00"
        item_variant_code = str(item_variant_code) if item_variant_code else "00"
        item_color_code = str(item_color_code) if item_color_code else "00"
        brand_code = str(brand_code) if brand_code else "00"

        sku = item_group_code+item_category_code+item_form_code+item_subform_code+item_size_code+item_variant_code+item_color_code+brand_code
        return {"sku": sku}



@frappe.whitelist()
def get_md_discount(supplier=''):
    dc = frappe.get_list("MD Discount", {"supplier_party": supplier})
    if len(dc) == 1:
        return dc[0]['name']
    else: 
        return False


def get_check_digit(number):
    from category_management.utils import roundup
    ctr = 0
    barcode12 = str(number)
    r_sum = 0
    for i in barcode12:
        if ctr % 2 == 0:
            temp = int(i) * 1
        else:
            temp = int(i) * 3
        r_sum += temp
        ctr += 1
    rounded = roundup(int(r_sum))
    check_digit = int(rounded) - int(r_sum)

    return barcode12 + str(check_digit)




