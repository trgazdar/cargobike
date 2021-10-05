odoo.define('quick_filter.front_js_multi',function(require){
    'use strict';
    var sAnimation = require('website.content.snippets.animation');
    var ajax = require('web.ajax');

    sAnimation.registry.advance_quick_filter_vertical = sAnimation.Class.extend({
        disabledInEditableMode: false,
        selector : ".tqt_website_quickfilter_vertical",
        events: {
            'change .container .as_quick_filter select': '_onVerticalParentFilterClick',
            'click .apply_quick_filter':'_onSubmitVerticalForm'
        },
        
        start: function (editable_mode) {
            var self = this;
            if (self.editableMode){
                $(".as-quickfilter-vertical-form").empty();
            }
            if(!self.editableMode){
                var list_id=self.$target.attr('data-list-id') || false;
                ajax.jsonRpc("/shop/quick_filter_snippet",'call',{
                    'collection_id':list_id,
                }).then(function( data ) {
                    if(!data.disable_group){
                        var value = data.value
                        $(".content-id").empty();
                        $(".tqt_website_quickfilter_vertical").removeClass('hidden');
                        self.$target.find(".as-quickfilter-vertical-form").empty().append(value);
                        self.$target.find(".js_filters").show();
                        self.$target.find('input[name="parent_applied"]').val(data.parent_option);
                        self.$target.find(".select_select2").select2({
                            dropdownCssClass: "asq-dropdown-hide"
                        });
                        if (data.parent_option == 'True'){
                            self.$target.find('ul li.asq-group select').not(':first').each(function(ev){
                                $(this).children().each(function(ev){
                                    $(this).attr('disabled', 'disabled');
                                })
                            });
                        }
                    } else {
                        $(".content-id").empty();
                        $(".tqt_website_quickfilter_vertical").removeClass('hidden');
                        self.$target.find(".as-quickfilter-vertical-form").empty().append("<div class='alert alert-danger'> Please Enable This Filter Group</div>");
                    }
                });
            }
        },

        _onVerticalParentFilterClick: function (ev) {
            if($(ev.currentTarget).parent().prev().val() == 'True'){
                var code = $(ev.currentTarget).find('option:selected').attr("data-option_id");
                var clear_option = $(ev.currentTarget).closest('li').nextAll().find('select');
                clear_option.select2('data', null);
                clear_option.each(function(ev) {
                    var current_ele = $(this);
                    var count = parseInt(current_ele.attr('data-count'));
                    if (count) {
                        $(".container .as_quick_filter").find("select:eq(" + count + ") option").each(function() {
                            var current_ele_opt = $(this);
                            var parent_id = current_ele_opt.attr("data-super_parent_id");
                            current_ele_opt.show();
                            current_ele_opt.prop("disabled", false);
                            if (parent_id) {
                                if (code !== undefined && code !== ""){
                                    var parent_id_list = JSON.parse(parent_id)
                                    if(jQuery.inArray(parseInt(code), parent_id_list) <= -1)
                                    { 
                                        current_ele_opt.attr('disabled', 'disabled'); 
                                    }
                                }  
                            }
                            else{
                                current_ele_opt.attr('disabled', 'disabled');
                            }
                        });
                    }
                });
            } else {}
        },


        _onSubmitVerticalForm: function(ev){
            $(ev.currentTarget).parent().prev().find("input[name='parent_applied']").remove();
            $(ev.currentTarget).closest('form').submit();
        },
        
    });

    sAnimation.registry.advance_quick_filter_horizontal = sAnimation.Class.extend({
        disabledInEditableMode: false,
        selector : ".tqt_website_quickfilter_horizontal",
        events: {
            'change .container .as_quick_filter select': '_onHorizontalParentFilterClick',
            'click .apply_quick_filter':'_onSubmitHorizontalForm'
        },
        
        start: function (editable_mode) {
            var self = this;
            if (self.editableMode){
                $(".as-quickfilter-horizontal-form").empty();
            }
            if(!self.editableMode){
                var list_id=self.$target.attr('data-list-id') || false;
                 ajax.jsonRpc("/shop/quick_filter_snippet",'call',{
                    'collection_id':list_id,
                }).then(function( data ) {
                    if(!data.disable_group){
                        var value = data.value
                        $(".content-id").empty();
                        $(".tqt_website_quickfilter_horizontal").removeClass('hidden');
                        self.$target.find(".as-quickfilter-horizontal-form").empty().append(value);
                        self.$target.find(".js_filters").show();
                        self.$target.find('input[name="parent_applied"]').val(data.parent_option);
                        self.$target.find(".select_select2").select2({
                            dropdownCssClass: "asq-dropdown-hide"
                        });
                        if (data.parent_option == 'True'){
                            self.$target.find('ul li.asq-group select').not(':first').each(function(ev){
                                $(this).children().each(function(ev){
                                    $(this).attr('disabled', 'disabled');
                                })
                            });
                        }
                    } else {
                        $(".content-id").empty();
                        $(".tqt_website_quickfilter_horizontal").removeClass('hidden');
                        self.$target.find(".as-quickfilter-horizontal-form").empty().append("<div class='alert alert-danger'> Please Enable This Filter Group </div>");
                    }
                });
            }
        },

         _onHorizontalParentFilterClick: function (ev) {
            
            if($(ev.currentTarget).parent().prev().val() == 'True'){
                var code = $(ev.currentTarget).find('option:selected').attr("data-option_id");
                var clear_option = $(ev.currentTarget).closest('li').nextAll().find('select');
                clear_option.select2('data', null);
                clear_option.each(function(ev) {
                    var current_ele = $(this);
                    var count = parseInt(current_ele.attr('data-count'));
                    if (count) {
                        $(".container .as_quick_filter").find("select:eq(" + count + ") option").each(function() {
                            var current_ele_opt = $(this);
                            var parent_id = current_ele_opt.attr("data-super_parent_id");
                            current_ele_opt.show();
                            current_ele_opt.prop("disabled", false);
                            if (parent_id) {
                                if (code !== undefined && code !== ""){
                                    var parent_id_list = JSON.parse(parent_id)
                                    if(jQuery.inArray(parseInt(code), parent_id_list) <= -1)
                                    { 
                                        current_ele_opt.attr('disabled', 'disabled'); 
                                    }
                                }  
                            }
                            else{
                                current_ele_opt.attr('disabled', 'disabled');
                            }
                        });
                    }
                });
            } else {}
        },

        _onSubmitHorizontalForm: function(ev){
            $(ev.currentTarget).parent().prev().find("input[name='parent_applied']").remove();
            $(ev.currentTarget).closest('form').submit();
        },

    });

    sAnimation.registry.advance_quick_filter_slider = sAnimation.Class.extend({
        disabledInEditableMode: false,
        selector : ".tqt_website_quickfilter_slider",
        events: {
            'change .container .as_quick_filter select': '_onSliderParentFilterClick',
            'click .apply_quick_filter':'_onSubmitSliderForm'
        },
        
        start: function (editable_mode) {
            var self = this;
            if (self.editableMode){
                $(".as-quickfilter-slider-form").empty();
            }
            if(!self.editableMode){
                var list_id=self.$target.attr('data-list-id') || false;
                 ajax.jsonRpc("/shop/quick_filter_snippet",'call',{
                    'collection_id':list_id,
                }).then(function( data ) {
                    if(!data.disable_group){
                        var value = data.value
                        $(".content-id").empty();
                        $(".tqt_website_quickfilter_slider").removeClass('hidden');
                        self.$target.find(".as-quickfilter-slider-form").empty().append(value);
                        self.$target.find(".js_filters").show();
                        self.$target.find('input[name="parent_applied"]').val(data.parent_option);
                        self.$target.find(".select_select2").select2({
                            dropdownCssClass: "asq-dropdown-hide"
                        });
                        if (data.parent_option == 'True'){
                            self.$target.find('ul li.asq-group select').not(':first').each(function(ev){
                                $(this).children().each(function(ev){
                                    $(this).attr('disabled', 'disabled');
                                })
                            });
                        }
                    } else {
                        $(".content-id").empty();
                        $(".tqt_website_quickfilter_slider").removeClass('hidden');
                        self.$target.find(".as-quickfilter-slider-form").empty().append("<div class='alert alert-danger'> Please Enable This Filter Group </div>");
                    }
                });
            }
        },

         _onSliderParentFilterClick: function (ev) {
            
            if($(ev.currentTarget).parent().prev().val() == 'True'){
                var code = $(ev.currentTarget).find('option:selected').attr("data-option_id");
                var clear_option = $(ev.currentTarget).closest('li').nextAll().find('select');
                clear_option.select2('data', null);
                clear_option.each(function(ev) {
                    var current_ele = $(this);
                    var count = parseInt(current_ele.attr('data-count'));
                    if (count) {
                        $(".container .as_quick_filter").find("select:eq(" + count + ") option").each(function() {
                            var current_ele_opt = $(this);
                            var parent_id = current_ele_opt.attr("data-super_parent_id");
                            current_ele_opt.show();
                            current_ele_opt.prop("disabled", false);
                            if (parent_id) {
                                if (code !== undefined && code !== ""){
                                    var parent_id_list = JSON.parse(parent_id)
                                    if(jQuery.inArray(parseInt(code), parent_id_list) <= -1)
                                    { 
                                        current_ele_opt.attr('disabled', 'disabled'); 
                                    }
                                }  
                            }
                            else{
                                current_ele_opt.attr('disabled', 'disabled');
                            }
                        });
                    }
                });
            } else {}
        },

        _onSubmitSliderForm: function(ev){
            $(ev.currentTarget).parent().prev().find("input[name='parent_applied']").remove();
            $(ev.currentTarget).closest('form').submit();
        },

    });

});