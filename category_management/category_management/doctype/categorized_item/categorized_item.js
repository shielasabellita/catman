// Copyright (c) 2020, Gaisano and contributors
// For license information, please see license.txt

var itemDescription = [];
frappe.ui.form.on('Categorized Item', {
	onload:function (frm,cdt,cdn) {
		frm.set_query('brand_link', function(doc){
			return {
				filters: {
					"disabled": 0
				}
			}
		})

		var item_category_link = frm.get_docfield("item_category_link");
		var item_form_link = frm.get_docfield("item_form_link");
		var item_subform_link = frm.get_docfield("item_subform_link");
		var item_variant_link = frm.get_docfield("item_variant_link");
		var item_size_link = frm.get_docfield("item_size_link");
		var item_color_link = frm.get_docfield("item_color_link");


		item_category_link.get_route_options_for_new_doc = function (field) {
			return {
				"item_group": frm.doc.item_group,
			};
		};
		item_form_link.get_route_options_for_new_doc = function (field) {
			return {
				"item_category":frm.doc.item_category_link
			};
		};

		item_subform_link.get_route_options_for_new_doc = function (field) {
			return {
				"item_form": frm.doc.item_form_link
			};
		};
		item_variant_link.get_route_options_for_new_doc = function (field) {
			return {
				"item_subform": frm.doc.item_subform_link
			};
		};

		item_color_link.get_route_options_for_new_doc = function (field) {
			return {
				"item_group": frm.doc.item_group
			};
		};
		item_size_link.get_route_options_for_new_doc = function (field) {
			return {
				"item_group": frm.doc.item_group
			};
		};

		if(typeof(frappe._from_link) != "undefined" ) {

			if(frappe._from_link.doctype == "X Transaction Item"){

				window.x_trans_link = frappe._from_link;

			}

        }

    },
	refresh: function(frm) {

		if (frm.is_new()){
			frm.set_value("categorized_item_id", "")
			frm.set_value("item_code", "")
			frm.set_value("barcode_retail", "")
			cur_frm.set_value("barcode_svg", "")
			cur_frm.set_value("synced", 0)

		}
		else{

			if (frm.doc.synced == 0 || !frm.doc.synced){
				frm.add_custom_button("Sync to ERP", function (doc) {
					if (!frm.doc.__unsaved) {
						frappe.confirm('After you confirm this, the <strong>item will be synced</strong> to ERP. Do you wish to continue?',
							// yes
							() => {
								frappe.call({
									method: "category_management.category_management.doctype.item.item.sync_item_to_erp",
									args: {"item_code": frm.doc.item_code},
									callback: function (r) {
										console.log(r)
										if (r.message.status_message == "Success"){
											frappe.msgprint({
												title: __("Sync Success"),
												indicator: 'green',
												message: __(r.message.data)
											});
											setTimeout(function () {
												location.reload();
											}, 1500);
										}else{
											frappe.msgprint({
												title: __("Syncing Failed on ERP"),
												indicator: 'red',
												message: __(r.message.data.err)
											});
										}
									}
								})
							},
							// no
							() =>{
								frappe.msgprint("Please go through everything one more time and make sure it's correct.")
							}
						)
					}else{
						frappe.msgprint("Please save before syncing")
					}
				}).addClass("btn btn-primary btn-lg")
			}

		}

		if(frm.doc.hasOwnProperty("__islocal")){
			frm.set_value("item_description", "")

			if(typeof(frm.doc.uoms) == "undefined"){
				console.log("called");
				var new_row = frm.add_child("uoms");
				new_row.uom = "Unit";
				new_row.conversion_factor = 1;
				frm.refresh_field("uoms");

			}
			frm.set_query('item_category_link',function(){

				return {
					filters:{
						'item_group':frm.doc.item_group
					}
				};
			});
			frm.set_query('item_variant_link',function(){

				return {
					filters:{
						'item_subform':frm.doc.item_subform_link
					}
				};
			});
			// frm.set_query('item_color_link',function(){

			// 	return {
			// 		filters:{
			// 			'item_group':frm.doc.item_group
			// 		}
			// 	};
			// });

			// frm.set_query('item_size_link',function(){

			// 	return {
			// 		filters:{
			// 			'item_group':frm.doc.item_group
			// 		}
			// 	};
			// });



        }

        if(frm.doc.categorized_item_id){

            //Can't use depends on: can't do interactive hide/show
            frm.set_df_property("brand_link","hidden",1);
            frm.set_df_property("item_category_link","hidden",1);
            frm.set_df_property("item_form_link","hidden",1);
            frm.set_df_property("item_subform_link","hidden",1);
            frm.set_df_property("item_variant_link","hidden",1);
            frm.set_df_property("item_size_link","hidden",1);
            frm.set_df_property("item_color_link","hidden",1);
            frm.set_df_property("brand","hidden",0);

			//Read Only Price & Vat/Non-Vat
			

            //default attr hidden in doctype for ci draft
            frm.set_df_property("item_category","hidden",0);
            frm.set_df_property("item_form","hidden",0);
            frm.set_df_property("item_subform","hidden",0);
            frm.set_df_property("item_variant","hidden",0);
            frm.set_df_property("item_size","hidden",0);
            frm.set_df_property("item_color","hidden",0);


            add_event(frm,"item_category","item_category_link");
            add_event(frm,"item_form","item_form_link");
            add_event(frm,"item_subform","item_subform_link");
            add_event(frm,"item_variant","item_variant_link");
            add_event(frm,"item_size","item_size_link");
            add_event(frm,"item_color","item_color_link");
            add_event(frm,"brand","brand_link");


        }

        frappe.model.get_value("Item", {"name": frm.doc.item_code}, "synced", (r)=>{
        	if (r.synced==1){
        		var fields = ["price", "vat_nonvat", "uoms", "has_supplier_barcode", "supplier_barcode", "supplier", "discount"]
				for (var i=0; i<fields.length; i++){
					frm.set_df_property(fields[i], "read_only", 1)
				}

			}
		})

        frm.set_query('discount',function(){
			return {
				filters:{
					'supplier_party':frm.doc.supplier
				}
			};
		});

	},
	validate: function (frm,cdt,cdn) {
		if(typeof(window.x_trans_link) != "undefined"){
			frappe._from_link = window.x_trans_link;
		}

		frm.trigger("validate_supplier_barcode")

    },
	after_insert: function (frm,cdt,cdn) {
		setTimeout(function () {
			frm.refresh()
		}, 2000);
    },
	parent_group:function(frm,cdt,cdn){
		frm.set_query('item_group',function(){
			return {
				filters:{
					'parent_group':frm.doc.parent_group
				}
			}
		});

		generate_code(frm,cdt,cdn);

	},
	item_group:function(frm,cdt,cdn){
		generate_code(frm,cdt,cdn);
		frm.set_query('item_category_link',function(){

			return {
				filters:{
					'item_group':frm.doc.item_group
				}
			};
		});

		// frm.set_query('item_color_link',function(){

		// 	return {
		// 		filters:{
		// 			'item_group':frm.doc.item_group
		// 		}
		// 	};
		// });

		// frm.set_query('item_size_link',function(){

		// 	return {
		// 		filters:{
		// 			'item_group':frm.doc.item_group
		// 		}
		// 	};
		// });



	},

	item_category_link:function (frm,cdt,cdn) {

		frm.set_query('item_form_link',function(){

			return {
				filters:{
					'item_category':frm.doc.item_category_link
				}
			};
		});

		if(typeof(frm.doc.item_category_link) == "undefined" || frm.doc.item_form_link == ""){
			frm.set_value("item_category","");

		}

		cur_frm.set_df_property("item_category_link","hidden",1	);
		cur_frm.set_df_property("item_category","hidden",0	);
        add_event(frm,"item_category","item_category_link");
        generate_code(frm,cdt,cdn);

    },
	item_form_link:function (frm,cdt,cdn) {

		frm.set_query('item_subform_link',function(){

			return {
				filters:{
					'item_form':frm.doc.item_form_link
				}
			};
		});


		if(typeof(frm.doc.item_form_link) == "undefined" || frm.doc.item_form_link == ""){

			frm.set_value("item_form","");
		}

		cur_frm.set_df_property("item_form_link","hidden",1	);
		cur_frm.set_df_property("item_form","hidden",0	);
		add_event(frm,"item_form","item_form_link");
		generate_code(frm,cdt,cdn);

    },
	item_subform_link:function (frm,cdt,cdn) {

		frm.set_query('item_variant_link',function(){

			return {
				filters:{
					'item_subform':frm.doc.item_subform_link
				}
			};
		});

		if(typeof(frm.doc.item_subform_link) == "undefined" || frm.doc.item_form_link == ""){
			frm.set_value("item_subform","");
		}

		cur_frm.set_df_property("item_subform_link","hidden",1	);
		cur_frm.set_df_property("item_subform","hidden",0	);
		add_event(frm,"item_subform","item_subform_link");
		generate_code(frm,cdt,cdn);
    },
	item_variant_link:function (frm,cdt,cdn) {
		if(typeof(frm.doc.item_variant_link) == "undefined" || frm.doc.item_form_link == ""){
			frm.set_value("item_variant","");
		}


		cur_frm.set_df_property("item_variant_link","hidden",1	);
		cur_frm.set_df_property("item_variant","hidden",0	);
		add_event(frm,"item_variant","item_variant_link");
		generate_code(frm,cdt,cdn);

    },
	item_size_link:function (frm,cdt,cdn) {
		if(typeof(frm.doc.item_size_link) == "undefined" || frm.doc.item_form_link == ""){
			frm.set_value("item_size","");
		}


		cur_frm.set_df_property("item_size_link","hidden",1	);
		cur_frm.set_df_property("item_size","hidden",0	);
		add_event(frm,"item_size","item_size_link");
		generate_code(frm,cdt,cdn);

    },
	item_color_link:function (frm,cdt,cdn) {

		if(typeof(frm.doc.item_color_link) == "undefined" || frm.doc.item_form_link == ""){
			frm.set_value("item_color","");
		}

		cur_frm.set_df_property("item_color_link","hidden",1	);
		cur_frm.set_df_property("item_color","hidden",0	);
        add_event(frm,"item_color","item_color_link");
		generate_code(frm,cdt,cdn);
    },


	brand_link: function (frm, cdt, cdn) {
		if(typeof(frm.doc.brand_link) == "undefined" || frm.doc.item_form_link == ""){

			frm.set_value("brand","");
		}
		cur_frm.set_df_property("brand_link","hidden",1	);
        cur_frm.set_df_property("brand","hidden",0	);
        add_event(frm,"brand","brand_link");
        generate_code(frm,cdt,cdn);

    },

	supplier: function(frm){
		frappe.call({
			method: "category_management.category_management.doctype.categorized_item.categorized_item.get_md_discount",
			args: {supplier: frm.doc.supplier},
			callback: function(r){
				let res = r.message
				if (res){
					frm.set_value("discount", res)
				}
			}
		})

		frappe.model.get_value("Supplier", {"name": frm.doc.supplier}, ['vat_nonvat'], function(r){
			var vat_nonvat = r.vat_nonvat == "VAT" ? "VAT" : "VAT - Exempt"
			frm.set_value("vat_nonvat", vat_nonvat)
		})
	},

	supplier_barcode: function (frm) {
		frm.trigger("validate_supplier_barcode")
    },

    // toggle functions
	validate_supplier_barcode: function (frm) {
		if (frm.is_new()){
			frappe.model.get_value("Categorized Item", {"supplier_barcode": frm.doc.supplier_barcode}, ['name'], function (r) {
				if (r) {
					frappe.throw("Supplier Barcode <strong>"+ frm.doc.supplier_barcode +"</strong> already exist")
				}
			})
		}

	},
});


function generate_code(frm,cdt,cdn){
	frappe.call({
		method:'generate_code',
		doc:frm.doc,
		callback:function(response){
			const data = response.message;
			cur_frm.set_value('sku', data['sku']);


		}
	});
}

function insert_to_array(i, value) {
	var finalText=""
	if(itemDescription[i]==null){
		itemDescription[i] = value;

		for (var idx = 0; idx < itemDescription.length; idx++){
			finalText = finalText + " " + itemDescription[idx];
		}
	}
	else{
		itemDescription.splice(i, 1, value)
		for (var idx = 0; idx < itemDescription.length; idx++){
			finalText = finalText + " " + itemDescription[idx];
		}
	}

}

function add_event(frm,field,field_link){
    $("input[data-fieldname='"+field+"']").on("keyup keydown",function() {
    	if (frm.doc.doctype === "Categorized Item"){

			frm.set_df_property(field,"hidden",1);
			frm.set_df_property(field_link,"hidden",0);
			$("input[data-fieldname='"+field_link+"']").focus();
		}

    });

}