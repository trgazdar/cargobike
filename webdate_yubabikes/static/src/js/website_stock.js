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
					this._super.apply(this, arguments);
					available_qty = parseInt($(".available_qty").val());
					added_quantity = parseInt($(".quantity").val());
					mproduct = parseInt($parent.find('input.js_product_change:checked').val())
					self.$("span.add_qty_warning").css("display", 'none');
					self.$("span.add_dispo").css("display", 'none');
					if(execute){
						return this._rpc({
							model: 'website',
							method: 'createbldate',
							args: [{
								product: mproduct,
								add_qty: added_quantity
							}]
							}).then(function (response) {
							if (available_qty >= added_quantity) {
								document.getElementById('add_to_cart').style.visibility = 'visible';
								$('p.state').append("<span class='add_dispo' style='display:block;position:relative;top:20px;bottom:10px;right:0px;color:white;background-color:#FCB731;padding: 0.5rem 1rem;font-size: 1.09rem;line-height: 1.5;border-radius: 0.3rem;z-index:2001;'><label>En Stock</label></span>");
								return
							} else if (response) {
								document.getElementById('add_to_cart').style.visibility = 'visible';
								self.$("p.state").css("visibility", 'hidden');
								$('p.livr').append("<span class='add_qty_warning' style='display:block;position:relative;top:20px;bottom:10px;right:0px;color:white;background-color:#FCB731;padding: 0.5rem 1rem;font-size: 1.09rem;line-height: 1.5;border-radius: 0.3rem;z-index:2001;'>Livraison à partir du <label>"+response+"</label></span>");
							}
							else{
								document.getElementById('add_to_cart').style.visibility = 'visible';
								self.$("p.state").css("visibility", 'hidden');
								$('p.livr').append("<span class='add_qty_warning' style='display:block;position:relative;top:20px;bottom:10px;right:0px;color:white;background-color:#FCB731;padding: 0.5rem 1rem;font-size: 1.09rem;line-height: 1.5;border-radius: 0.3rem;z-index:2001;'>Livraison à définir</span>");
							}
							});
					}
					return myret

				}
				else {
					var myret2 = VariantMixin._getProductId.apply(this, arguments);
					this._super.apply(this, arguments);
					available_qty = parseInt($(".available_qty").val());
					added_quantity = parseInt($(".quantity").val());
					mproduct = VariantMixin._getProductId.apply(this, arguments);
					self.$("span.add_qty_warning").css("display", 'none');
					self.$("span.add_dispo").css("display", 'none');
					if(execute){
						return this._rpc({
							model: 'website',
							method: 'createbldate',
							args: [{
								product: mproduct,
								add_qty: added_quantity
							}]
							}).then(function (response) {
							if (available_qty >= added_quantity) {
								document.getElementById('add_to_cart').style.visibility = 'visible';
								$('p.state').append("<span class='add_dispo' style='display:block;position:relative;top:20px;bottom:10px;right:0px;color:white;background-color:#FCB731;padding: 0.5rem 1rem;font-size: 1.09rem;line-height: 1.5;border-radius: 0.3rem;z-index:2001;'><label>En Stock</label></span>");
								return
							} else if (response) {
								document.getElementById('add_to_cart').style.visibility = 'visible';
								self.$("p.state").css("visibility", 'hidden');
								$('p.livr').append("<span class='add_qty_warning' style='display:block;position:relative;top:20px;bottom:10px;right:0px;color:white;background-color:#FCB731;padding: 0.5rem 1rem;font-size: 1.09rem;line-height: 1.5;border-radius: 0.3rem;z-index:2001;'>Livraison à partir du <label>"+response+"</label></span>");
							}
							else{
								document.getElementById('add_to_cart').style.visibility = 'visible';
								self.$("p.state").css("visibility", 'hidden');
								$('p.livr').append("<span class='add_qty_warning' style='display:block;position:relative;top:20px;bottom:10px;right:0px;color:white;background-color:#FCB731;padding: 0.5rem 1rem;font-size: 1.09rem;line-height: 1.5;border-radius: 0.3rem;z-index:2001;'>Livraison à définir</span>");
							}
							});
					}
					return myret2

				}

			},

    });
});

