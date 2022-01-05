{
    'name': "Cap product template",
    "version": "1.0.1",
    'description':
        """
            amends on product_template
        """,

    'author': "Captivea-pgi",
    'website': "https://www.captivea.com",
    'category': 'Custom Modules',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
    ],
    "installable": True,
    "auto_install": False,
}