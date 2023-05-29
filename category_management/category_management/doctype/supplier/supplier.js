// Copyright (c) 2020, Gaisano and contributors
// For license information, please see license.txt
frappe.ui.form.on('Supplier', {
	refresh: function(frm) {

	    var regions = ["01", '02', '03', '4A', '4B', '05', '06', '07', '08', '09', '10', '11', '12', '13', 'BARMM', 'CAR', 'NCR']
        set_options(frm, 'address_0', regions)

        frm.set_df_property('address_1', 'read_only', 1);
        frm.set_df_property('address_2', 'read_only', 1);
        frm.set_df_property('address_3', 'read_only', 1);

	},
    address_0: function (frm) {
        get_place(frm, frm.doc.address_0, null, null, null);
        frm.set_df_property('address_1', 'read_only', 0);
        frm.set_df_property('address_1', 'reqd', 0);
    },
    address_1: function (frm) {
        get_place(frm, frm.doc.address_0, frm.doc.address_1, null, null);
        frm.set_df_property('address_2', 'read_only', 0);
        frm.set_df_property('address_2', 'reqd', 0);
    },
    address_2: function (frm) {
        get_place(frm, frm.doc.address_0, frm.doc.address_1, frm.doc.address_2, null);
        frm.set_df_property('address_3', 'read_only', 0);
        frm.set_df_property('address_3', 'reqd', 0);
    },
});


function get_place(frm, region, province, city, brgy) {
    frappe.call({
        method: "category_management.utils.get_reg_prov_city_brgy",
        args: {region: region},
        callback: function (r) {
            const result = r.message

            if (province == null && city == null && brgy == null){
                set_options(frm, "address_1", Object.keys(result['province_list']))

            }else if (city == null && brgy == null){
                set_options(frm, "address_2", Object.keys(result['province_list'][province]['municipality_list']))

            }else if (brgy == null){
                set_options(frm, "address_3", result['province_list'][province]['municipality_list'][city]['barangay_list'])
            }

        }
    })
}


function set_options(frm, field, value){
    frm.set_df_property(field, 'options', value);
    frm.refresh_field(field);
}

