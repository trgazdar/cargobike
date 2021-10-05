odoo.define('quick_filter.editor_js', function(require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var weContext = require('web_editor.context');
    var web_editor = require('web_editor.editor');
    var options = require('web_editor.snippets.options');
    var wUtils = require('website.utils');
    var qweb = core.qweb;
    var _t = core._t;

    var advance_quick_filters = options.Class.extend({
        popup_template_id: "editor_new_website_quick_filter",
        popup_title: _t("Select Collection"),

        start: function () {
            var self = this;
            return this._super.apply(this, arguments);
        },

        website_filter_configure_collection: function(previewMode, value) {
            var self = this;
            var def = wUtils.prompt({
                'id': this.popup_template_id,
                'window_title': this.popup_title,
                'select': _t("Collection"),
                'init': function(field, dialog) {
                    return rpc.query({
                        model: 'filter.collection.configure',
                        method: 'name_search',
                        args: ['', []],
                        context: self.options.recordInfo.context,
                    }).then(function (data) {
                        $(dialog).find('.btn-primary').prop('disabled', !data.length);
                        return data;
                    });
                },
            });
            def.then(function(result) {
                var collection_id = parseInt(result.val);
                self.$target.attr("data-list-id", collection_id);
                rpc.query({
                    model: 'filter.collection.configure',
                    method: 'read',
                    args: [[collection_id],['name']],
                }).then(function(data) {
                    if (data && data[0] && data[0].name)
                        self.$target.append('<div class="content-id">' + data[0].name + '</div>');
                });
            });
            return def;
        },
        onBuilt: function() {
            var self = this;
            this._super();
            this.website_filter_configure_collection('click').guardedCatch(function() {
                self.getParent()._onRemoveClick($.Event("click"));
            });
        }
    });

    options.registry.advance_quick_filter_slider = advance_quick_filters.extend({
        cleanForSave: function() {}
    });
    
    options.registry.advance_quick_filter_vertical = advance_quick_filters.extend({
        cleanForSave: function() {}
    });

    options.registry.advance_quick_filter_horizontal = advance_quick_filters.extend({
        cleanForSave: function() {}
    });
});