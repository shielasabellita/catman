# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "category_management"
app_title = "Category Management"
app_publisher = "Gaisano"
app_description = "Category Management"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "itdepartment.gaisano@gmail.com"
app_license = "MIT"
app_logo_url = '/assets/category_management/images/catman-logo.png'
website_context = {
    "favicon": "/assets/category_management/images/catman-logo.png",
    "splash_image":"/assets/category_management/images/catman-logo.png",
    'app_logo_url' : '/assets/category_management/images/catman-logo.png'
}

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/category_management/css/category_management.css"
app_include_js = "/assets/category_management/js/category_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/category_management/css/category_management.css"
# web_include_js = "/assets/category_management/js/category_management.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "category_management.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "category_management.install.before_install"
# after_install = "category_management.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "category_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

jenv = {
	"methods": [
		"get_total_uom:category_management.category_management.print_format.x_purchase_order.get_total_uom",
	]
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron": {
        "0 0 * * *": [
            "category_management.scheduled_task.available_stock_sync"
        ]
    },
# 	"all": [
# 		"category_management.tasks.all"
# 	],
# 	"daily": [
# 		"category_management.scheduled_task.available_stock_sync"
# 	],
# 	"hourly": [
# 		"category_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"category_management.tasks.weekly"
# 	]
# 	"monthly": [
# 		"category_management.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "category_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "category_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "category_management.task.get_dashboard_data"
# }

