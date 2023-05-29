
import frappe
def get_14_digit_barcode():
    import json
    import pandas as pd
    from openpyxl import load_workbook
    affected_barcodes = frappe.db.get_list('Categorized Item', filters=[
        [
        'modified', 'between', ['2022-01-13', '2022-01-13']
        ]
        
        
    ],fields=['*']
    )
    barcode_array = []
  
    for barcode in affected_barcodes:
  
        if len(barcode['name']) == 14:
            barcode_array.append({'current_barcode':barcode['name'],'correct_barcode':barcode['name'][1:],'item_code':barcode['item_code']})
    


    current_barcode = []
    correct_barcode = []
    item_code = []

    for barcode in barcode_array:
        current_barcode.append(barcode['current_barcode'])
        correct_barcode.append(barcode['correct_barcode'])
        item_code.append(barcode['item_code'])
    # dataframe Name and Age columns
    df = pd.DataFrame({'currentBarcode':current_barcode,
                    'correctBarcode': correct_barcode,
                    'itemCode':item_code
                    
                    })

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    path_to_xlsxs = "/home/justine/Gaisano/14_digit_barcode.xlsx"

    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(path_to_xlsxs, sheet_name='Sheet1', index=False)



#will base on latest stock uom rate in item price list
def update_categorized_item_price():
    import os
    items = frappe.get_all("Item",['*'])
    item_len = len(items)
    idx = 1
    for item in items:
        os.system("clear")
    
        progress(idx,item_len,"UPDATE CATEGORIZED ITEM PRICE")
        stock_uom = item['default_unit_measure']
        rate = frappe.db.get_value("Item Price",{'item_code':item['name'],'price_list':"Standard Buying",'uom':stock_uom},"rate")
        frappe.db.set_value("Categorized Item",item['barcode_retail'],"price",rate,update_modified=False)
        idx += 1

def progress(count, total,title ):
    import sys
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    suffix =  str(count)+"/"+str(total)+" items updated"
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write(title)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix, ))
    sys.stdout.flush() 