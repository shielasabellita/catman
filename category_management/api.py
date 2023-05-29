from __future__ import unicode_literals
import frappe, json
import requests

##### for Item Syncing
@frappe.whitelist(allow_guest=True)
def get_categorized_item(param):
	print(param)
	if param:
		query = "SELECT * FROM `tabCategorized Item` WHERE stock_number = '{0}'"
		result = frappe.db.sql(query.format(param),as_dict=True)
		return result
	else:
		query = "SELECT * FROM `tabCategorized Item`"
		result = frappe.db.sql(query,as_dict=True)
		return result



@frappe.whitelist(allow_guest=True)
def update_item():
	try:
		data = json.loads(frappe.request.data)
	except:
		data = None

	print(data)
	if data:
		item_data = data['item']
		item = frappe.get_doc("Item", {"item_code": item_data['item_code']})
		# stock_no = []
		# for nos in frappe.get_list("Stock Number", {"parent": item_data['item_code']}, "stock_no"):
		# 	stock_no.append(nos.stock_no)
		
		# for nos in data['stock_numbers']:
		# 	if nos not in stock_no:
		# 		item.append("stock_number", {
		# 			"stock_no": nos
		# 		})

		item_price = frappe.db.sql("select rate, item_code, price_list, uom from `tabItem Price` where item_code='{}'".format(item_data['item_code']), as_dict=1)

		try:
			# Update Item
			frappe.db.set_value('Item', item_data['item_code'], item_data)

			if item.taxes:
				template = "Item Tax Template - 12%" if item_data['vat_nonvat'] == "VAT" else "VAT-Exempt"
				frappe.db.set_value("Item Tax", {"parent": item_data['item_code']}, "item_tax_template", template)
				frappe.db.set_value("Item Supplier", {"parent": item_data['item_code']}, {
					"supplier": data['supplier']['supplier'],
					"supplier_name": data['supplier']['supplier_name']
				})
				frappe.db.set_value("Categorized Item", {"item_code": item_data['item_code']}, {
					"supplier": data['supplier']['supplier'],
					"vat_nonvat": item_data['vat_nonvat'],
					"discount": item_data['discount'],
				})


            # Update Item Price
			for data_price in data['price_list_rate']:
				for price in item_price:
					if data_price['price_list'] == price['price_list']  and data_price['uom'] == price['uom']: # and data_price['price_list'] == price['price_list']:
						if data_price['price_list_rate'] != price['rate']:
							item_price_doc = frappe.get_doc("Item Price", {"item_code": data_price['item_code'], "price_list": data_price['price_list'], "uom": data_price['uom']})
							item_price_doc.rate = data_price['price_list_rate']
							item_price_doc.save(ignore_permissions=True)
					else:
						if not frappe.db.exists("Item Price", {"price_list": data_price['price_list'], "uom": data_price['uom'], 'item_code': data_price['item_code']}):
							new_item_price = frappe.get_doc({
								"doctype": "Item Price",
								"item_code": data_price['item_code'],
								"uom": data_price['uom'],
								"item_name": data_price['item_name'],
								"item_description": data_price['item_description'],
								"min_qty": 1,
								"price_list": data_price['price_list'],
								"rate": data_price['price_list_rate']
							})

							new_item_price.insert(ignore_permissions=True)

			return "Item successfuly updated from CATMAN"

		except:
			frappe.log_error("Failed to update Item and Item Price", frappe.get_traceback())


@frappe.whitelist(allow_guest=True)
def sync_supplier():
	try:
		data = json.loads(frappe.request.data)
	except:
		data = None

	print(data)
	if data:
		if not frappe.db.exists("Supplier", data['name']):
			supplier = frappe.new_doc("Supplier")
		else:
			supplier = frappe.get_doc("Supplier", {"name": data['name']})

		try:
			supplier.erp_supplier_code = data['name']
			supplier.update(data)
			supplier.save(ignore_permissions=True)

			return supplier.name

		except:
			frappe.log_error("Failed to add/update Supplier", frappe.get_traceback())

@frappe.whitelist(allow_guest=True)
def sync_discount():
	try:
		data = json.loads(frappe.request.data)
	except:
		data = None

	print(data)
	if data:
		if not frappe.db.exists("MD Discount", data['discount']): 
			disc = frappe.new_doc("MD Discount")
		else:
			disc = frappe.get_doc("MD Discount", {"name": data['discount']})

		try:
			disc.update(data)
			disc.save(ignore_permissions=True)
			return 1

		except:
			frappe.log_error("Failed to add/update Supplier", frappe.get_traceback())

@frappe.whitelist(allow_guest=True)
def sync_user():
	try:
		data = json.loads(frappe.request.data)
	except:
		data = None

	if data:
		try:
			print(frappe.db.exists("User", data['name']))
			if not frappe.db.exists("User", data['name']): 
				user = frappe.new_doc("User")
				print("create")
				user.update(data)
				user.save(ignore_permissions=True)
				return "Successfuly addded! If you wish to update user, please update the user manually to CATMAN ERP"

			else:
				return "User already exist. If you wish to update user, please update the user manually to CATMAN ERP"

		except:
			frappe.log_error("Failed to add/update User", frappe.get_traceback())

@frappe.whitelist()
def erp_login():

	headers = {'content-type': 'application/json', 'Accept': 'application/json'}
	session = requests.Session()
	erp_info = frappe.get_single("ERP Information")
	session.post('{0}/api/method/login'.format(erp_info.url),
				 data=json.dumps({"usr": erp_info.username, "pwd": erp_info.get_password('password')}), headers=headers)

	return session


#DELETE request method
@frappe.whitelist()
def delete_item(barcode):
	if frappe.local.request.method=="DELETE":
		items = frappe.get_list("Item", {"barcode_retail": barcode})
		try:
			if items:
				item_codes = ""
				for i in items:
					item_codes += i['name']+", "
					frappe.delete_doc("Item", i['name'], ignore_missing=False)
					frappe.db.commit()

				frappe.local.response.http_status_code = 202
				frappe.local.response.message = "Successfuly deleted Items: {}".format(item_codes)
		except Exception as e:
			frappe.throw(_(str(e)))
	else:
		frappe.throw(_("Method error"))

#SYNC Stock V2 Data to ERP
@frappe.whitelist()
def add_stock_v2(doc=None):

	try:
		erp_info = frappe.get_single("ERP Information")
		headers = {
			'content-type': 'application/json',
			'Accept': 'application/json',
			'Authorization': "token {}:{}".format(erp_info.api_key, erp_info.get_password('api_secret'))
		}
		if not None:
			data = {
				"stock_number":doc.stock_number.strip(),
				"categorized_item_id":doc.categorized_item_id,
				"created_from":"Synced",
				"owner":frappe.session.user
			}

			response = requests.post('{0}/api/resource/Stock Number V2'.format(erp_info.url),data=json.dumps(data), headers=headers)
			if response.status_code not in [200,201]:
				frappe.log_error(response.text,"Stock Number V2 {0} of {1} not synced".format(doc.stock_number,doc.categorized_item_id))
	except Exception as e:
		frappe.msgprint("Failed to sync Stock Number")
		frappe.log_error(frappe.get_traceback(), "Failed to sync Stock Number V2")
			