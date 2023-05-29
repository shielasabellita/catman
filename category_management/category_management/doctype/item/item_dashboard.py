from frappe import _
def get_data():
	return {
		'fieldname': 'item_code',
		'transactions': [
			{
				'label': _('Pricing'),
				'items': ['Item Price']
			}
		]
	}