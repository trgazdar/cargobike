odoo.define('quick_filter.quick_filter', function(require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).on("click", ".apply_quick_filter", function() {
        $("form.js_filters").submit();
    });

    $(document).on('change', ".container .as_quick_filter select", function() {
        if ($(".container .as_quick_filter select").length > 1) {
            var code = $(this).find('option:selected').attr("data-option_id");
            var clear_option = $(this).closest('li').nextAll().find('select');
            clear_option.find('option:selected').removeAttr("selected");
            clear_option.each(function() {
                var count = parseInt($(this).attr('data-count'));
                if (count) {
                    $(".container .as_quick_filter").find("select:eq(" + count + ") option").each(function() {
                        var parent_id = $(this).attr("data-super_parent_id");
                        $(this).show();
                        if (parent_id) {
                            if ((code !== undefined && code !== "") && !parent_id.includes(code) )
                                $(this).hide();
                        }
                    });
                }
            });
        }
    });
});