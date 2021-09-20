odoo.define('webdate_yubabikes.display_stock_qty', function(require) {
	"use strict";

	var sAnimations = require('website.content.snippets.animation');
	var VariantMixin = require('sale.VariantMixin');
    var ajaxIsWorking = false;

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
					if(execute && !ajaxIsWorking) {

					    ajaxIsWorking = true;
					    self.$("#loadingDiv").css("display", 'inline-block');
                        self.$("#loadingDiv2").css("display", 'inline-block');

                        return self._rpc({
                            model: 'website',
                            method: 'stockbldate',
                            args: [{
                                product: mproduct,
                                add_qty: added_quantity
                            }]
                        }).then(function (response2) {
                            if (response2 && response2[0].myqt < 0) {
                                        document.getElementById('add_to_cart').style.visibility = 'visible';
                                        self.$("p.state").css("visibility", 'hidden');
                                        self.$("#loadingDiv").css("display", 'none');
                                        self.$("#loadingDiv2").css("display", 'none');
                                        $('p.livr').append("<span class='add_qty_warning'>Livraison à partir du <label>" + response2[0].mdate + "</label></span>");
                                }
                            else if(available_qty >= added_quantity){
                                self.$("#loadingDiv").css("display", 'none');
                                self.$("#loadingDiv2").css("display", 'none');
                                document.getElementById('add_to_cart').style.visibility = 'visible';
                                $('p.state').append("<span class='add_dispo'><label>En Stock</label></span>");
                            }
                            else {
                                self.$("#loadingDiv").css("display", 'none');
                                self.$("#loadingDiv2").css("display", 'none');
                                document.getElementById('add_to_cart').style.visibility = 'visible';
                                self.$("p.state").css("visibility", 'hidden');
                                $('p.livr').append("<span class='add_qty_warning'>Livraison à définir</span>");
                            }

                            self.$("#loadingDiv").css("display", 'none');
                            self.$("#loadingDiv2").css("display", 'none');
                            ajaxIsWorking = false;

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
					if(execute && !ajaxIsWorking) {
					    ajaxIsWorking = true;
					    self.$("#loadingDiv").css("display", 'inline-block');
                        self.$("#loadingDiv2").css("display", 'inline-block');

                        return self._rpc({
                            model: 'website',
                            method: 'stockbldate',
                            args: [{
                                product: mproduct,
                                add_qty: added_quantity
                            }]
                        }).then(function (response2) {
                            if (response2 && response2[0].myqt < 0) {
                                        document.getElementById('add_to_cart').style.visibility = 'visible';
                                        self.$("p.state").css("visibility", 'hidden');
                                        self.$("#loadingDiv").css("display", 'none');
                                        self.$("#loadingDiv2").css("display", 'none');
                                        $('p.livr').append("<span class='add_qty_warning'>Livraison à partir du <label>" + response2[0].mdate + "</label></span>");
                                }
                            else if(available_qty >= added_quantity){
                                self.$("#loadingDiv").css("display", 'none');
                                self.$("#loadingDiv2").css("display", 'none');
                                document.getElementById('add_to_cart').style.visibility = 'visible';
                                $('p.state').append("<span class='add_dispo'><label>En Stock</label></span>");
                            }
                            else {
                                self.$("#loadingDiv").css("display", 'none');
                                self.$("#loadingDiv2").css("display", 'none');
                                document.getElementById('add_to_cart').style.visibility = 'visible';
                                self.$("p.state").css("visibility", 'hidden');
                                $('p.livr').append("<span class='add_qty_warning'>Livraison à définir</span>");
                            }

                            self.$("#loadingDiv").css("display", 'none');
                            self.$("#loadingDiv2").css("display", 'none');
                            ajaxIsWorking = false;
                        });

                    }
					return myret2
				}
			}
    });
});