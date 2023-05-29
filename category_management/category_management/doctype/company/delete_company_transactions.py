

from __future__ import unicode_literals
import frappe

from frappe.utils import cint
from frappe import _
from frappe.desk.notifications import clear_notifications

import functools


@frappe.whitelist()
def delete_company_transactions(company_name):
	frappe.only_for("System Manager")
	doc = frappe.get_doc("Company", company_name)

	if frappe.session.user != doc.owner:
		frappe.throw(_("Transactions can only be deleted by the creator of the Company"),
			frappe.PermissionError)


	for doctype in frappe.db.sql_list("""select parent from
		tabDocField where fieldtype='Link' and options='Company'"""):
		if doctype in ("X Transaction"):
				delete_for_doctype(doctype, company_name)


	doc.save()
	# Clear notification counts
	clear_notifications()

def delete_for_doctype(doctype, company_name):

	meta = frappe.get_meta(doctype)
	company_fieldname = meta.get("fields", {"fieldtype": "Link",
		"options": "Company"})[0].fieldname

	if not meta.issingle:
		if not meta.istable:

			# delete children
			for df in meta.get_table_fields():
				frappe.db.sql("""delete from `tab{0}` where parent in
					(select name from `tab{1}` where `{2}`=%s)""".format(df.options,
						doctype, company_fieldname), company_name)

		#delete version log
		frappe.db.sql("""delete from `tabVersion` where ref_doctype=%s and docname in
			(select name from `tab{0}` where `{1}`=%s)""".format(doctype,
				company_fieldname), (doctype, company_name))

		# delete parent
		frappe.db.sql("""delete from `tab{0}`
			where {1}= %s """.format(doctype, company_fieldname), company_name)

		# reset series
		# naming_series = meta.get_field("naming_series")


		series = frappe.db.sql("SELECT * FROM `tabSeries`", as_dict=1)
		masters_series = ['9898', 'ITM_DG', 'B-', 'SL-', 'SUP_', 'PATCHLOG', '']
		items = frappe.get_list("Item")
		if len(items) == 0:
			masters_series = ['9898', 'B-', 'SL-', 'SUP_', 'PATCHLOG', '']
		for s in series:
			if s['name'] not in masters_series:
				frappe.db.sql("UPDATE `tabSeries` SET current = 0 WHERE name = '{0}'".format(s['name']))
				frappe.db.commit()