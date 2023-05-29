// Copyright (c) 2020, GAMS and contributors
// For license information, please see license.txt



var branch_fields = ["cty","mll","osm","jrb","mlby","val","crm","btu","ilgmain","ilgmall","bml","suki","cmgn","pml","tbd","vmt","val2"];
frappe.ui.form.on('X Transaction', {
    onload_post_render:function (frm,cdt,cdn) {
        cur_frm.fields_dict['items'].grid.add_custom_button('Refresh Rate', () => {

            if(cur_frm.doc.x_transaction_type == "X Transaction")
            {
                _price_list_rate(frm,cdt,cdn);
            }
        });

        var stock_no = frm.get_docfield("items","stock_no");
        stock_no.get_route_options_for_new_doc = function (field) {
			return {

				"supplier": frm.doc.supplier,
                "discount":frm.doc.md_discount
			};
		};

        var specific_stock_no_v2 = frm.get_docfield("items","specific_stock_no_v2");
        specific_stock_no_v2.get_route_options_for_new_doc = function (field) {
            var d = locals[field.doctype][field.docname];
			return {

				"categorized_item_id": d.stock_no,
                "created_from": "X Transaction"
			};
		};
        cur_frm.set_query("specific_stock_no_v2", "items", function(doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                        ['Stock Number V2', 'categorized_item_id', '=', d.stock_no],

                    ]
            }
        });
    },
    supplier:function (frm,cdt,cdn) {
        if (cur_frm.doc.supplier) {
       
            var values = locals[cdt][cdn];

            frappe.call({
                method:"category_management.category_management.doctype.supplier.supplier.getSupplier",
                args:{"supplier":values.supplier},
                callback:function(response)
                {
                    var m=response.message[0];

                    if(m.vat_nonvat == "VAT")
                    {
                        cur_frm.set_value("taxes_and_charges","Value Added Tax 12% - G");
                    }else{
                        cur_frm.set_value("taxes_and_charges","");

                    }
                }
            });
        }
        frm.set_query("stock_no", "items", function(doc, cdt, cdn){
            var df = locals[cdt][cdn]
            return {
                filters: [
                    ['Categorized Item', 'supplier', '=', doc.supplier]
                ]
            }
        })
    },
    md_discount: function(frm,cdt,cdn){
        if(frm.doc.md_discount == undefined){
            frm.set_value("cascading_total",0);
            frm.set_value("total_discount",0);
            frm.set_value("md_discount_title","");
        }
    },
	refresh: function(frm,cdt,cdn) {
        if(!frm.is_new()){
            lock_fields(frm);
        }
        
  		cur_frm.set_value("price_list","Standard Buying");
        if(cur_frm.doc.__unsaved == 1 ) {
            cur_frm.doc.sync_status = 0;

            if (!cur_frm.doc.branch_detail){

                frappe.call({
                    method: "category_management.script.branch.read_all_branch",
                    callback: function (r) {
                         frappe.run_serially([
                             ()=>{
                                for (var i = 0; i < r.message.length-5; i++) {
                                    var new_row = frm.add_child("branch_detail");
                                    new_row.branch = r.message[i].name;
                                    new_row.business_unit = r.message[i].chain;
                                    new_row.centralize_po_code = r.message[i].centralize_po_code;
                                }
                                cur_frm.refresh_fields("branch_detail");
                             },
                             ()=>{
                             }
                         ]);


                    }
                });
            }
            cur_frm.clear_table("generated_purchase_order");
            cur_frm.refresh_fields("generated_purchase_order");
            cur_frm.clear_table("generated_delivery_note");
            cur_frm.refresh_fields("generated_delivery_note");
            cur_frm.clear_table("generated_stock_entry");
            cur_frm.refresh_fields("generated_stock_entry");
            cur_frm.refresh_field("sync_status");
            set_branch_detail(frm,cdt,cdn);
        }

        $("[data-fieldname='branch_detail']").find(".grid-add-row").hide();
        $("[data-fieldname='branch_detail']").find(".grid-remove-rows").hide();


	},
    mark_up:function(frm){
        $.each(frm.doc.items,function(idx,item){
            frm.doc.items[idx].mark_up = frm.doc.mark_up;
        });
        frm.refresh_field("items");
    },
    validate:function (frm,cdt,cdn) {
       if(frm.doc.reqd_by_date === frm.doc.posting_date){
            frappe.msgprint("Required by date should not be the same with posting date");
            frm.set_value("reqd_by_date", "");
        }

        frm.doc.items.forEach(function(item,idx){
        
            branch_fields.forEach(function(branch){
                console.log(item[branch] );
                if(item[branch] != 0.00 && item[branch+"_srp"] == 0.00){
                    frappe.throw(branch.toUpperCase()+" SRP For Item In Row #"+(idx+1)+" Is Zero");
                }
            });
        });
        

    },
    sync_to_erp:function(frm,cdt,cdn){
        if(cur_frm.doc.__unsaved == 1 ){
            frappe.throw("XPO Not Saved: Please save your XPO before syncing.")
        }
        let d = new frappe.ui.Dialog({
            title: 'Verify Password',
            fields: [
                {
                    label: 'Username',
                    fieldname: 'username',
                    fieldtype: 'Read Only',
                    default: frappe.session.user
                },
                {
                    label: 'Password',
                    fieldname: 'password',
                    fieldtype: 'Password'
                }
            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                frappe.show_progress(__('Syncing to ERP. Please wait.'),99,100);
                 frappe.call({
                    method:'category_management.category_management.doctype.x_transaction.x_transaction.execute_rpc',
                    args:{
                        'self':frm.doc,
                        'password':values.password
                    },
                    callback:function(response){

                        frappe.hide_progress();
                        frappe.msgprint("Synced to ERP");
                        cur_frm.reload_doc();

                    }
                });
                d.hide();
            }
        });
        d.show();


    },
    reqd_by_date: function (frm) {
        if(frm.doc.reqd_by_date === frm.doc.posting_date){
            frappe.msgprint("Required by date should not be the same with posting date");
            frm.set_value("reqd_by_date", "");
        }
    }
});


cur_frm.set_query("set_warehouse", "branch_detail", function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
	    filters: [
                ['Warehouse', 'branch', '=', d.branch],

            ]
	}
});

cur_frm.set_query("md_discount", function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
	    filters: [
                ['MD Discount', 'supplier_party', '=', cur_frm.doc.supplier ],

            ]
	}
});



// insert all items on item child table based on discount type, whether By product or By supplier
function _get_all_items(doc ,cdt, cdn) {

  //cur_frm.refresh();
  cur_frm.clear_table("items");
  cur_frm.refresh_field("items");
  var values = locals[cdt][cdn];
  var row = locals[cdt][cdn];
  var test=[];
  frappe.show_progress("Getting Item from the Server.",0, 100,"In Progress").hide();
    // get all item_code basd on discount id
    frappe.call({
        method:"gaisano_erpv12.script.purchase_order.md_item_under_discount_get_all",
        args:{"discount_id":cur_frm.doc.md_discount},
        callback:function(r){
            for(var i=0; i < r.message.length; i++)
            {


                    // Get details on specific item_code
                    frappe.call({
                            method: "frappe.client.get",
                            args: {
                            doctype: "Item",
                            filters: {
                                "item_code": r.message[i].item_code,
                            }
                        },
                        callback: function (data) {
                            var childTable = cur_frm.add_child("items");
                                    childTable.item_shortname = data.message.item_short_name;
                                    childTable.item_name = data.message.item_name;
                                    childTable.item_code = data.message.item_code;
                                    childTable.description = data.message.description;
                                    childTable.conversion_factor = 1;
                                    childTable.uom = data.message.purchase_uom;
                                    childTable.stock_uom = data.message.stock_uom;
                                    childTable.qty = 0;
                                    childTable.item_tax_template = data.message.vat_nonvat == "VAT" ? "" :"VAT-Exempt";
                                    childTable.schedule_date = cur_frm.doc.schedule_date;
                                    childTable.expected_delivery_date = cur_frm.doc.schedule_date;
                                    childTable.description = data.message.description;
                                    childTable.rate = data.message.price_list_rate;
                                    childTable.price_list_rate = data.message.price_list_rate;
                                    childTable.last_purchase_rate = data.message.last_purchase_rate;
                                    cur_frm.refresh_fields("items");

                        }

                }).done(function(i)
                {
                    test.push(i.message.item_code);
                    var message ="Please Wait ";
                    if(test.length == r.message.length)
                    {p
                        $(".progress-bar").css("background-color","#6ef32a");
                        message ="Done";

                    }else{

                    }
                    frappe.show_progress("Getting Item from the Server",test.length, (r.message.length), message+" "+test.length +" |"+(r.message.length));

                })


            }
        }
    })
}

cur_frm.set_query("parent_pr", function(doc, cdt, cdn) {

    if (cur_frm.doc.x_transaction_type == "X Return - Fresh"){
        return {
            filters:[
                ['Purchase Receipt','document_type',"=","Fresh Goods" ],

            ]
        }
    }else{
         return {
            filters:[
                ['Purchase Receipt','document_type',"=","Fresh Goods" ],
                ['Purchase Receipt','status',"=","To Bill" ],

            ]
        }
    }

});


frappe.ui.form.on("X Transaction Item",{
    items_add:function (frm,cdt,cdn) {
        var d = locals[cdt][cdn];
        d.mark_up = frm.doc.mark_up;
        frm.refresh_field("items");
    },
    specific_stock_no_v2: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        frm.doc.items.forEach(function(item,idx){
            if(item.stock_no == d.stock_no && item.stock_no != "" && d.idx != item.idx && d.specific_stock_no_v2 == item.specific_stock_no_v2){
                d.stock_no = "";
                d.item_code = "";
                d.specific_stock_no_v2 = "";
                d.description = "";
                d.uom = "";
                d.total_amount = 0.00;
                d.rate = 0.00;
                frappe.msgprint("Barcode and Stock Number already ordered in row "+item.idx)
            }

        });
        frm.refresh_field("items")
    },
    item_code:function (frm,cdt,cdn) {

        var d = locals[cdt][cdn];
 
    

       return frappe.call({
          method: "category_management.category_management.doctype.x_transaction.x_transaction.read_item_info",
          args: {
                item_code: d.item_code,
                price_list:cur_frm.doc.price_list,
                x_transaction_type:cur_frm.doc.x_transaction_type,
                uom:d.uom,
                branch_details:cur_frm.doc.branch_detail,
                mark_up: d.mark_up,
                cascading_total : frm.doc.cascading_total

          },
          callback: function(r){
              if(!r._server_messages){
                 if(r.message.length > 0) {
                    console.log(r.message);
                    var result = r.message[0];
                    d['description'] = result.item_name;
                    d['rate'] =result.rate;
                    d['uom'] =result.uom;
                    d['unit_cost'] =result.unit_cost;
                    d['item_tax_template']= result.vat_nonvat  == "VAT" ? "Item Tax Template - 12%" :"VAT-Exempt";
                    d['auto_computed_srp'] = result.auto_computed_srp;
                    d['discounted_rate']  = result.discounted_rate;
                    d['stock_uom'] = result.stock_uom;
                    d['stock_uom_rate'] = result.stock_uom_rate;
                    d['conversion_factor'] = result.conversion_factor;
                    


                    //FOR DIFFERENT SELLING UOM HANDLING
                    d['selling_uom'] = result.selling_uom;
                    d['selling_conversion_factor'] = result.selling_conversion_factor;
                    d['buying_rate_base_on_selling_uom'] = result.buying_rate_base_on_selling_uom;

                    var branch_srp =  result['branch_srp'][0];
                     for( var branch_srp_field in branch_srp){
                         d[branch_srp_field] = branch_srp[branch_srp_field];
                     }
                     try {

                        //Note: To change( spaghetti code)
                         d['available_stock_cty']=r.message[0]['cty'][0].actual_qty;
                         d['available_stock_mll']=r.message[0]['mll'][0].actual_qty;
                         d['available_stock_osm']=r.message[0]['osm'][0].actual_qty;
                         d['available_stock_jrb']=r.message[0]['jrb'][0].actual_qty;
                         d['available_stock_mlby']=r.message[0]['mlby'][0].actual_qty;
                         d['available_stock_val']=r.message[0]['val'][0].actual_qty;
                         d['available_stock_crm']=r.message[0]['crm'][0].actual_qty;
                         d['available_stock_btu']=r.message[0]['btu'][0].actual_qty;
                         d['available_stock_ilgmain']=r.message[0]['ilgmain'][0].actual_qty;
                         d['available_stock_ilgmall']=r.message[0]['ilgmall'][0].actual_qty;
                         d['available_stock_bml']=r.message[0]['bml'][0].actual_qty;
                         d['available_stock_suki']=r.message[0]['suki'][0].actual_qty;
                         d['available_stock_cmgn']=r.message[0]['cmgn'][0].actual_qty;
                         d['available_stock_pml']=r.message[0]['pml'][0].actual_qty;
                         d['available_stock_tbd']=r.message[0]['tbd'][0].actual_qty;
                         d['available_stock_vmt']=r.message[0]['vmt'][0].actual_qty;
                         d['available_stock_val2']=r.message[0]['val2'][0].actual_qty;
                     }catch(err){
                         console.log("Sync Settings not set");
                     }


                 }else{
                     d['description'] ="";
                     d['rate'] = 0;
                     d['uom'] = "";
                     d['item_tax_template'] = "";
                     d['qty']= "";
                 }
                 frm.refresh_fields()
              }

          }
       });
    },
    uom:function (frm,cdt,cdn) {
        var d = locals[cdt][cdn];
        frappe.call({
            method: "category_management.category_management.doctype.x_transaction.x_transaction.read_item_info",
                args: {
                    item_code: d.item_code,
                    price_list:cur_frm.doc.price_list,
                    x_transaction_type:cur_frm.doc.x_transaction_type,
                    uom:d.uom,
                    branch_details:cur_frm.doc.branch_detail,
                    mark_up: d.mark_up,
                    cascading_total : frm.doc.cascading_total,
                    conversion_factor: d.conversion_factor,
                    rate: d.rate
                },
                callback: function(r){
                    if(r.message.length > 0) {
                        var result = r.message[0]
                        d['description'] =result.item_name;
                        d['rate'] =result.rate;
                        // d['uom'] =result.uom;
                        d['total_amount'] = d['rate'] * d['total_qty'];
                        d['item_tax_template']= result.vat_nonvat  == "VAT" ? "Item Tax Template - 12%" :"VAT-Exempt";
                        d['auto_computed_srp'] = result.auto_computed_srp;
                        d['discounted_rate']  = result.discounted_rate;
                        d['stock_uom'] = result.stock_uom;
                        d['stock_uom_rate'] = result.stock_uom_rate;
                        d['conversion_factor'] = result.conversion_factor;

                    }else{
                        d['description'] ="";
                        d['rate'] = 0;
                        d['uom'] = "";
                        d['item_tax_template'] = "";
                    }
                    cur_frm.refresh_field("items");
              }
        });

        cur_frm.refresh_field("items");
    },
    selling_uom:function (frm,cdt,cdn) {
        var d = locals[cdt][cdn];
        frappe.call({
            method: "category_management.category_management.doctype.x_transaction.x_transaction.set_selling_uom",
                args: {
                    item_code: d.item_code,
                   stock_uom_rate: d.stock_uom_rate,
                   selling_uom: d.selling_uom
                },
                callback: function(r){
                    console.log(r);
                    if(r.message.length > 0) {
                        var result = r.message[0]
                        //FOR DIFFERENT SELLING UOM HANDLING
                        
                        d['selling_conversion_factor'] = result.selling_conversion_factor;
                        d['buying_rate_base_on_selling_uom'] = result.buying_rate_base_on_selling_uom;
                        if (d.item_code != ""){
                            d.auto_computed_srp = d.discounted_rate + d.discounted_rate * ((d.mark_up)/100.00)
                            branch_fields.forEach(function(branch,idx){
                                let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
                                let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
                                set_selling_details(d,branch,margin,mark_up_rate,false);
                                
                            });
                        }

                    }else{
                        //FOR DIFFERENT SELLING UOM HANDLING
                        d['selling_uom'] = "";
                        d['selling_conversion_factor'] = "";
                        d['buying_rate_base_on_selling_uom'] = "";

                    }
                    cur_frm.refresh_field("items");
              }
        });

        cur_frm.refresh_field("items");
    },
    cty:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"cty");
    },
    jrb:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"jrb");
    },
    mll:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"mll");
    },
    osm:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"osm");
    },
    mlby:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"mlby");
    },
    val:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"val");
    },
    crm:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"crm");
    },
    btu:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"btu");
    },
    ilgmain:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"ilgmain");
    },
    ilgmall:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"ilgmall");
    },
    bml:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"bml");
    },
    suki:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"suki");
    },
    cmgn:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"cmgn");
    },
    pml:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"pml");
    },
    tbd:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"tbd");
    },
    vmt:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"vmt");
    },
    val2:function (frm,cdt,cdn) {
        set_total_qty_amount(frm,cdt,cdn);
        // set_branch_detail(frm,cdt,cdn);
        set_uom(frm,cdt,cdn,"val2");
    },
    cty_srp:function (frm,cdt,cdn) {
       
        let branch = "cty";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
       
    },
    jrb_srp:function (frm,cdt,cdn) {
        let branch = "jrb";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    mll_srp:function (frm,cdt,cdn) {
        let branch = "mll";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    osm_srp:function (frm,cdt,cdn) {
        let branch = "osm";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    mlby_srp:function (frm,cdt,cdn) {
        let branch = "mlby";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    val_srp:function (frm,cdt,cdn) {
        let branch = "val";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    crm_srp:function (frm,cdt,cdn) {
        let branch = "crm";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    btu_srp:function (frm,cdt,cdn) {
        let branch = "btu";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    ilgmain_srp:function (frm,cdt,cdn) {
        let branch = "ilgmain";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    ilgmall_srp:function (frm,cdt,cdn) {
        let branch = "ilgmall";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    bml_srp:function (frm,cdt,cdn) {
        let branch = "bml";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    suki_srp:function (frm,cdt,cdn) {
        let branch = "suki";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    cmgn_srp:function (frm,cdt,cdn) {
        let branch = "cmgn";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    pml_srp:function (frm,cdt,cdn) {
        let branch = "pml";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    tbd_srp:function (frm,cdt,cdn) {
        let branch = "tbd";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    vmt_srp:function (frm,cdt,cdn) {
        let branch = "vmt";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    val2_srp:function (frm,cdt,cdn) {
        let branch = "val2";
        let d = locals[cdt][cdn];
        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
        set_selling_details(d,branch,margin,mark_up_rate);
    },
    base_srp: function(frm,cdt,cdn){
        var d = locals[cdt][cdn]
        branch_fields.forEach(function(branch,idx){
            d[branch+"_srp"] = d["base_srp"];
            let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
            let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
            set_selling_details(d,branch,margin,mark_up_rate,false);
            
        });
        cur_frm.refresh_fields("items");
  
    },
    base_order: function(frm,cdt,cdn){
        var d = locals[cdt][cdn]
        branch_fields.forEach(function(branch,idx){
            d[branch] = d["base_order"];
            d[branch+"_uom"] = d["uom"];

        });
        cur_frm.refresh_fields("items");
    },
    mark_up: function(frm,cdt,cdn){
        var d = locals[cdt][cdn];
        if (d.item_code != ""){
            d.auto_computed_srp = d.discounted_rate + d.discounted_rate * ((d.mark_up)/100.00)
            cur_frm.refresh_fields("items");
        }
        
    },
    rate: function(frm,cdt,cdn){
        var d = locals[cdt][cdn];
        
        frappe.call({
            method:'category_management.category_management.doctype.item.item.update_stock_uom_rate',
            args:{
                item_code:d.item_code,
                stock_uom:d.stock_uom,
                uom:d.uom,
                rate:d.rate,
                total_discount: frm.doc.total_discount,
                selling_conversion_factor:d.selling_conversion_factor
                
                
            },
            callback: function(r){
                var response = r.message;
                console.log("UPDATE STOCK UOM RATE");
                console.log(response);
                d.stock_uom_rate = response.stock_uom_rate;
                d.discounted_rate = response.discounted_rate;
                d.buying_rate_base_on_selling_uom = response.buying_rate_base_on_selling_uom
                if (d.item_code != ""){
                    d.auto_computed_srp = d.discounted_rate + d.discounted_rate * ((d.mark_up)/100.00)
                    branch_fields.forEach(function(branch,idx){
                        let margin = compute_margin(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
                        let mark_up_rate = compute_mark_up_rate(d[branch+"_srp"],d.buying_rate_base_on_selling_uom);
                        set_selling_details(d,branch,margin,mark_up_rate,false);
                        
                    });
                }
                cur_frm.refresh_fields("items");
            }
        });
    }

   
});

function set_total_qty_amount(frm,cdt,cdn) {

    var d = locals[cdt][cdn];
    d.total_qty = d.cty + d.mll + d.osm + d.jrb + d.mlby + d.val + d.crm + d.btu + d.ilgmain + d.ilgmall + d.bml + d.suki + d.cmgn + d.pml + d.tbd + d.vmt + d.val2;
    d.total_amount = d.rate * d.total_qty;
    cur_frm.refresh_fields("items");
    //CHANGE TO CUR_FRM becuase items table is unknown when using just frm

}


function set_branch_detail(frm,cdt,cdn,event) {
    var d = locals[cdt][cdn];
   
    branch_fields.forEach(function (branch_field,index,array) {
        frappe.model.get_value("Branch", {"centralize_po_code": branch_field}, "name", function(d){
            frappe.call({
                method:"category_management.category_management.doctype.x_transaction.x_transaction.get_default_warehouse_po",
                args:{"branch":d.name},
                callback: function (r) {
                    cur_frm.doc.branch_detail.forEach(function (cur_branch,index) {
                        if(cur_branch.branch == d.name){
                            cur_branch.set_warehouse = r.message;
                            cur_frm.refresh_fields("branch_detail");

                        }
                    });
                }
            });
        });
    });


}


function _price_list_rate(doc, cdt, cdn)
{

    var values = locals[cdt][cdn];
    var num_total = 0;
    var total =0;
    var loading_state =[];
    frappe.show_progress("Getting Updated Rate.",0,100, "In Progress").hide();
    $.each(cur_frm.doc.items || [], function(i, item) {

            frappe.call({
                    method:"gaisano_erpv12.script.item.item_price",
                    args:{"item_code":item.item_code, "price_list": cur_frm.doc.price_list, "uom":item.uom},
                    callback: function(r){
                    if(r.message === undefined || r.message.length ==0)
                    {
                        var rate = r.message[0];
                        item.amount= 0;
                        item.rate = 0;

                        refresh_field("items");

                        num_total = item.amount;
                        total = total + item.amount;
                        // cur_frm.set_value("total",total);
                        // refresh_field("total");

                      }else{
                        var rate = r.message[0];
                        item.amount= rate.price_list_rate * item.qty;
                        item.rate = rate.price_list_rate;

                        refresh_field("items");

                        // num_total = item.amount;
                        // total = total + item.amount;

                    }
                },

            }).done(function(i)
            {
                loading_state.push("loading");
                var message = "Please Wait ...";
                if(loading_state.length == cur_frm.doc.items.length)
                {
                    $(".progress-bar").css("background-color","#6ef32a");
                    message ="Done";
                }
                frappe.show_progress("Getting Updated Rate",loading_state.length, cur_frm.doc.items.length, message+" "+loading_state.length+" | " + cur_frm.doc.items.length)
            });


    });
}

//SET UOM_PER_BRANCH IF THE UOM FIELD HAS VALUE AND ORDER PER BRANCH > 0
function set_uom(frm,cdt,cdn,branch){
    var d = locals[cdt][cdn]
    if (d.uom != null && d[branch] > 0) {
        d[branch+"_uom"] = d.uom;
        frm.refresh_field("items");
    }else{
        d[branch+"_uom"] = "";

    }
}

function lock_fields(frm){
    const lock_fields = [
        "supplier",
        "posting_date",
        "reqd_by_date",
        "strictly_ship_via",
        "taxes_and_charges",
        "md_discount",
        "mark_up",
        "items",
        "branch_detail",
        "remarks"
    ]
    if (frm.doc.sync_status == 1){
        lock_fields.forEach(function(field){
            frm.set_df_property(field,"read_only",1);
            frm.refresh_field(field);
        });
        
    }
}



function compute_margin(srp=0.00,buying_rate=0.00){
  
    
    let margin = 0.00;
    if(srp != 0.00){
        margin = ((srp - buying_rate) / srp)*100.00;
    }
    return margin;
    
}
function compute_mark_up_rate(srp=0.00,buying_rate=0.00){
    let mark_up_rate = 0.00;
    if(srp != 0.00){
        mark_up_rate = ((srp - buying_rate) / buying_rate)*100.00;
    }
   return mark_up_rate;
}


function set_selling_details(row=null,branch=null,margin=0.00,mark_up_rate=0.00,refresh=true){
    row[branch+"_margin"] = margin;
    row[branch+"_mark_up_rate"] = mark_up_rate;
    if(refresh){
        cur_frm.refresh_fields("items");
    }
   
}