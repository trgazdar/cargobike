odoo.define('webdate_yubabikes.display_stock_qty', function(require) {
	"use strict";

	var sAnimations = require('website.content.snippets.animation');
	var VariantMixin = require('sale.VariantMixin');

	sAnimations.registry.WebsiteSale.include({


		_getProductId: function ($parent) {
				var available_qty = false;
				var added_quantity = false;
				var execute = true;
				var mproduct = false;
				var crr_added_qty = $($parent.currentTarget).val();
				if ($parent.find('input.js_product_change').length !== 0) {
					var myret = parseInt($parent.find('input.js_product_change:checked').val())
					var self = this;
					available_qty = parseInt($(".available_qty").val());
					added_quantity = parseInt($(".quantity").val());
					mproduct = parseInt($parent.find('input.js_product_change:checked').val())
					self.$("span.add_qty_warning").css("display", 'none');
					self.$("span.add_dispo").css("display", 'none');
					if(execute) {
                        return self._rpc({
                            model: 'website',
                            method: 'stockbldate',
                            args: [{
                                product: mproduct,
                                add_qty: added_quantity
                            }]
                        }).then(function (response2) {
                            if (response2 < 0) {

								document.getElementById('add_to_cart').style.visibility = 'visible';
								self.$("p.state").css("visibility", 'hidden');
								$('p.livr').append("<span class='add_qty_warning'>Livraison à partir du <label>" + response2 + "</label></span>");
							}

                            else {
                                return self._rpc({
                                    model: 'website',
                                    method: 'createbldate',
                                    args: [{
                                        product: mproduct,
                                        add_qty: added_quantity
                                    }]
                                }).then(function (response) {

                                    if (response) {
                                        document.getElementById('add_to_cart').style.visibility = 'visible';
                                        self.$("p.state").css("visibility", 'hidden');
                                        $('p.state').append("<span class='add_dispo'><label>En Stock</label></span>");
                                    }
                                    else {
                                        document.getElementById('add_to_cart').style.visibility = 'visible';
                                        self.$("p.state").css("visibility", 'hidden');
                                        $('p.livr').append("<span class='add_qty_warning'>Livraison à définir</span>");
                                    }

                                });
                            }
                            });

                    }
					return myret


                    }


				else {
					var myret2 = VariantMixin._getProductId.apply(this, arguments);
					var self = this;
					available_qty = parseInt($(".available_qty").val());
					added_quantity = parseInt($(".quantity").val());
					mproduct = VariantMixin._getProductId.apply(this, arguments);
					self.$("span.add_qty_warning").css("display", 'none');
					self.$("span.add_dispo").css("display", 'none');
					if(execute) {
                        return self._rpc({
                            model: 'website',
                            method: 'stockbldate',
                            args: [{
                                product: mproduct,
                                add_qty: added_quantity
                            }]
                        }).then(function (response2) {
                            if (response2 < 0) {
                                return self._rpc({
                                    model: 'website',
                                    method: 'stockblmydate',
                                    args: [{
                                        product: mproduct,
                                        add_qty: added_quantity
                                    }]
                                }).then(function (response3) {


                                        document.getElementById('add_to_cart').style.visibility = 'visible';
                                        self.$("p.state").css("visibility", 'hidden');
                                        $('p.livr').append("<span class='add_qty_warning'>Livraison à partir du <label>" + response3 + "</label></span>");
                                    });
                                }

                            else {
                                return self._rpc({
                                    model: 'website',
                                    method: 'createbldate',
                                    args: [{
                                        product: mproduct,
                                        add_qty: added_quantity
                                    }]
                                }).then(function (response) {

                                    if (response) {
                                        document.getElementById('add_to_cart').style.visibility = 'visible';
                                        self.$("p.state").css("visibility", 'hidden');
                                        $('p.state').append("<span class='add_dispo'><label>En Stock</label></span>");
                                    }
                                    else {
                                        document.getElementById('add_to_cart').style.visibility = 'visible';
                                        self.$("p.state").css("visibility", 'hidden');
                                        $('p.livr').append("<span class='add_qty_warning'>Livraison à définir</span>");
                                    }

                                });
                            }
                        });





                    }
					return myret2

				}

			}

    });
});

