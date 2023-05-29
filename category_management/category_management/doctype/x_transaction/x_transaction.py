
from __future__ import unicode_literals
from category_management.category_management.doctype.item.item import get_srp
import frappe
from frappe import _
from frappe.model.document import Document
import json
import requests
from category_management.api import erp_login
from category_management.utils import compute_discounted_rate,compute_margin,compute_srp,computed_mark_up_rate

from frappe.desk.reportview import get_match_cond, get_filters_cond
class XTransaction(Document):
    def autoname(self):

        if self.x_transaction_type == "X Purchase Order":
            self.naming_series = "XPO-."+self.posting_date.replace("-","") + ".####."

    def validate(self):
        total = 0
        total_qty = 0
        branches = frappe.get_list("Branch",{},["centralize_po_code"])
        for item in self.items:
            total += item.total_amount
            total_qty += item.total_qty
        if total_qty == 0:
            frappe.throw("X Transaction Items table should not be empty.")
        self.total_amount = total

        #Depreciated Code, used before when there is only 1 uniform for item per branch
        #self.update_items()
    def get_total_amount_per_po(self,generated_po, items):
        data = {}
        uom = []
        
        for item in items:  
            # Loop through all items and insert uoms used in document
            uom.append(item.uom)
            
        # Inititalize uom list
        uom = list(set(uom))

        for po in generated_po:
            # Get all branches in X-PO
            po_branch = frappe.db.get_value("Purchase Order", po.po_code, "branch")

            # Fetch gross amount and net amount of each PO
            po_total_amount = frappe.db.get_value("Purchase Order", po.po_code, "total")
            po_net_amount = frappe.db.get_value("Purchase Order", po.po_code, "net_total")

            # Fetch branch centralize po code
            branch_detail = frappe.db.get_value("Branch", po_branch, "centralize_po_code")

            # Initialize dictionary
            data[branch_detail] = {'gross_amount': 0, 'net_amount': 0, 'uom': dict.fromkeys(uom, 0)}
            data['total_uom'] = dict.fromkeys(uom, 0)

            # insert gross amount and net amount
            data[branch_detail]['gross_amount'] = po_total_amount
            data[branch_detail]['net_amount'] = po_net_amount

        for item in items:
            # Loop over all branches
            for branch in data:
                if branch != 'total_uom':
                    # then increment item qty per branch
                    data[branch]['uom'][item.uom] += item.get(branch)
                    data['total_uom'][item.uom] += item.get(branch)
        return data
    def get_item_srp(self,items):
        
        branch_fields =  ["cty","mll","osm","jrb","mlby","val","crm","btu","ilgmain","ilgmall","bml","suki","cmgn","pml","tbd","vmt","val2"]
        item_list = []
        result = {}

        for item in items:
            # item_list.append(item.specific_stock_no_v2)
            result[item.specific_stock_no_v2] = {'srp': 0, 'margin': 0, 'markup': 0}

        # items = list(set(items))
        # result = dict.fromkeys(item_list, {'srp': 0, 'margin': 0, 'markup': 0})
        print(result)
        for item in items:
            for branch_field in branch_fields:
                if item.get(branch_field + "_srp") != 0.00:
                    result[item.specific_stock_no_v2]['srp'] = item.get(branch_field + "_srp")
                    result[item.specific_stock_no_v2]['margin'] = item.get(branch_field + "_margin")
                    result[item.specific_stock_no_v2]['markup'] = item.get(branch_field + "_mark_up_rate")
                
                    break
                print("current item " + item.specific_stock_no_v2+branch_field)
    
        return result

    #Depreciated Code
    # def update_items(self):
    #     idx = 1
    #     for item in self.get('items'):
    #         item.discounted_rate = compute_discounted_rate(item.rate,self.cascading_total)
    #         item.auto_computed_srp = compute_srp(item.discounted_rate,item.mark_up)
    #         item.margin = compute_margin(item.final_srp,item.buying_rate_base_on_selling_uom)
    #         item.mark_up_rate = computed_mark_up_rate(item.final_srp,item.buying_rate_base_on_selling_uom)
    #         item.total_amount = item.rate * item.total_qty
    #         idx = idx + 1
          









@frappe.whitelist()
def read_item_info(price_list,x_transaction_type,branch_details,item_code=None,uom=None,cascading_total=0.00,mark_up=0.00,rate=0.00,conversion_factor = 1.00):
    cur_user = frappe.session.user
    if item_code:
        
        stock_uom,selling_uom= frappe.get_value("Item",item_code,['default_unit_measure','default_sales_unit_of_measure'])

        if not selling_uom:
            selling_uom = stock_uom

        if not uom:
 
            result = frappe.db.sql("SELECT * FROM `tabItem` LEFT JOIN `tabItem Price` on `tabItem`.item_code = `tabItem Price`.item_code where `tabItem`.name = %s AND price_list = %s AND uom = %s",(item_code, price_list, stock_uom), as_dict=1)
          
            
            result[0]['conversion_factor'] = get_conversion_factor(item_code,stock_uom)
            
        else:
            result = frappe.db.sql("SELECT * FROM `tabItem` LEFT JOIN `tabItem Price` on `tabItem`.item_code = `tabItem Price`.item_code where `tabItem`.name = %s AND price_list = %s AND uom = %s",( item_code,price_list,stock_uom), as_dict=1)
           
           
            result[0]['conversion_factor'] =  get_conversion_factor(item_code,uom)
            if  float(result[0]['conversion_factor']) < float(conversion_factor):
                
                result[0]['rate'] = float(rate) / float(conversion_factor)
            elif float(result[0]['conversion_factor']) > float(conversion_factor):
                result[0]['rate'] = float(rate) * result[0]['conversion_factor']
            
          
        if not result:
            frappe.log_error(_("Item %s doesn't have item".format()),"Read Item Info Error" )
            frappe.throw(_("On Item {0}, there is no item price set for the UOM {1}".format(item_code,uom if uom else stock_uom)))
        

        result[0]['discounted_rate'] = compute_discounted_rate(buying_rate= result[0].rate,cascading_total=cascading_total)
        result[0]['auto_computed_srp'] = compute_srp(discounted_rate=result[0]['discounted_rate'],mark_up=mark_up)
        result[0]['stock_uom_rate'] = float(result[0].rate) / float(result[0]['conversion_factor'])
        result[0]['stock_uom'] = stock_uom

        #FOR DIFFERENT SELLING UOM HANDLING 
        result[0]['selling_uom'] = selling_uom
        result[0]['selling_conversion_factor'] =  get_conversion_factor(item_code,selling_uom)
        result[0]['buying_rate_base_on_selling_uom'] =  result[0]['stock_uom_rate'] *  result[0]['selling_conversion_factor'] 
        


        result[0]['branch_srp'] = get_branch_srp(item_code=item_code,uom=stock_uom,branch_details=json.loads(branch_details),buying_rate=result[0]['buying_rate_base_on_selling_uom'])
        user_sync_preference = frappe.get_value("User Sync Preference",cur_user,"real_time_item_api")

       


        if user_sync_preference is None:
            print("In None")
            user_sync_preference = frappe.db.get_single_value('Sync Settings','real_time_item_api')

        if user_sync_preference == 1:
            print("User Wants to Sync")
            for branch_detail in json.loads(branch_details):
                if 'set_warehouse' in branch_detail:
                    actual_qty = get_available_stock(item_code,branch_detail['set_warehouse'])['data']
                    if not actual_qty:
                        actual_qty = [{"actual_qty":0}]
                    result[0][branch_detail['centralize_po_code']] = actual_qty
        elif frappe.db.get_single_value('Sync Settings','eod_item_syncing'):
            print("enabled EOD")
            for branch_detail in json.loads(branch_details):
                if 'set_warehouse' in branch_detail:
                    qty = frappe.get_value("Available Stock",{'item_code': item_code,'warehouse': branch_detail['set_warehouse']},"qty")
                    actual_qty = [{"actual_qty": qty if qty else 0}]
                    result[0][branch_detail['centralize_po_code']] = actual_qty


        return result
    else:
        frappe.throw("Stock number doesn't have linked Item Code")


@frappe.whitelist()
def set_selling_uom(item_code,selling_uom,stock_uom_rate):

    result = [{}]
    result[0]['selling_conversion_factor'] = get_conversion_factor(item_code,selling_uom)
    result[0]['buying_rate_base_on_selling_uom'] = float(stock_uom_rate) * float(result[0]['selling_conversion_factor'])
    return result


#Will return the warehouse for PO found in X Transaction Settings
@frappe.whitelist()
def get_default_warehouse_po(branch):
    return frappe.get_value("PO Default Warehouse", {"branch": branch,"parent":"X Transaction Settings"}, ["warehouse"])



@frappe.whitelist()
def execute_rpc(self,password):
    cur_user = frappe.session.user
    param = json.loads(self)
   
    data = {
        "doctype":"X Transaction",
        "name":param.get('name'),
        "naming_series":param.get('name'),
        "x_transaction_type":param.get("x_transaction_type"),
        "posting_date": param.get("posting_date"),
        "supplier": param.get("supplier"),
        "reqd_by_date": param.get("reqd_by_date"),
        "company": param.get("company"),
        "strictly_ship_via": param.get("strictly_ship_via") if "strictly_ship_via" in param else "",
        "md_discount": param.get("md_discount"),
        "cascading_total":param.get('cascading_total'),
        "total_discount":param.get('total_discount'),
        "mark_up": param.get('mark_up'),
        "price_list": param.get("price_list"),
        "items": param.get("items"),
        "taxes_and_charges":param.get("taxes_and_charges"),
        "branch_detail": param.get("branch_detail"),
        "docstatus":1,
        "catman_name":param.get('name'),
        "payment_term":param.get('payment_term'),
        "remarks":param.get('remarks'),
        "owner":cur_user
      
    }

    headers = {'content-type':'application/json','Accept':'application/json'}
    session = requests.Session()
    erp_info = frappe.get_single("ERP Information")

    session.post('{0}/api/method/login'.format(erp_info.url),data = json.dumps({"usr":cur_user,"pwd":password}),headers=headers)

    r = session.post('{0}/api/resource/X Transaction'.format(erp_info.url),data=json.dumps(data),headers=headers)
    if r.status_code not in [200,201]:
        frappe.log_error(r.text,"ERP Sync Error")
        
        
        frappe.throw(json.loads(json.loads(json.loads(r.text).get('_server_messages'))[0]).get('message'))
    else:
        doc = frappe.get_doc("X Transaction",param['name'])
        doc.sync_status = 1
        doc.save()



@frappe.whitelist()
def get_available_stock(item_code,warehouse,session=None):
    erp_info = frappe.get_single("ERP Information")
    if session is None:
        session = erp_login()

    response = session.get('{0}/api/resource/Bin?fields=["actual_qty"]&filters=[["item_code", "=", "{1}"],["warehouse","=","{2}"]]'.format(erp_info.url,item_code,warehouse))

    print(response.text)
    if response.status_code not in [200]:
        frappe.log_error(response.text,"Error: Can't get Available Stock")

    return response.json()
@frappe.whitelist()
def get_stock_no(parent=None):
    if parent:
        stock_nos =  frappe.db.sql("""SELECT stock_no FROM `tabStock Number` WHERE parent = %s""",
                             (parent),as_dict=1)
        stock_list = []
        for stock_no in stock_nos:
            print(stock_no)
            stock_list.append(stock_no.stock_no)
        print(stock_list)
        data = "\n"
        return data.join(stock_list)


@frappe.whitelist()
def get_branch_srp(item_code=None,uom=None,branch_details=None,buying_rate=0.00):
    from category_management.category_management.doctype.item.item import get_srp
    result = [{},{},{}]
    for branch_detail in branch_details:
        if 'branch' in branch_detail:
            srp = get_srp(item_code=item_code,uom=uom, branch=branch_detail['branch'][5:])
            if not srp:
                srp = 0.00
            result[0][branch_detail['centralize_po_code']+"_srp"] =  srp
            result[0][branch_detail['centralize_po_code']+"_margin"] = compute_margin(srp=srp,buying_rate=buying_rate)
            result[0][branch_detail['centralize_po_code']+"_mark_up_rate"] = computed_mark_up_rate(srp=srp,buying_rate=buying_rate)
    return result

#For Different Selling UOM handling (margin/markup)
def get_conversion_factor(item_code,uom):
    conversion_factor = 1.0
    conversion_factor_details = frappe.get_doc("Item",item_code).get("uoms")
    for conversion_factor_detail in conversion_factor_details:
        if conversion_factor_detail.uom == uom:
            conversion_factor = conversion_factor_detail.conversion_factor
    return conversion_factor