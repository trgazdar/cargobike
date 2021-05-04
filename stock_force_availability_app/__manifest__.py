# -*- coding: utf-8 -*-

{
    "name" : "Force Availability button in Delivery/Picking",
    "author": "Tripode-Services",
    "version" : "13.0.1.0",
    "images":["static/description/main_screenshot.png"],
    'summary':'Forcefully Available Stock on delivery Force Availability for delivery order Force Availability for picking Force Availability button in Stock picking Force Availability button in delivery order Force Availability button in picking stock Force Availability',
    "description": """ Force Availability In Stock.""",
    "license" : "OPL-1",
    "depends" : ['base','stock','sale_management','account'],
    "data": [
       'views/stock_force_availability_view.xml'
    ],
    "auto_install": False,
    "installable": True,
    "category" : "Warehouse",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
