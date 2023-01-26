odoo.define('ks_dashboard_ninja.ks_graph_preview', function(require) {
    "use strict";

    console.log("======================================")

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');

    var QWeb = core.qweb;

    console.log("pasoooooooooooooooooooooooooooooooo")

    var KsGraphPreview = AbstractField.extend({

        supportedFieldTypes: ['char'],

        init: function () {
            this._super.apply(this, arguments);
            console.log("iniciaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        },

        _render: function() {
            console.log("renderrrrrrrr KsGrapks_graph_previewhPreview");
            var self = this;
            console.log("finnnnnnnnnnnnnnn render");
        },

    });
    console.log("generadoooooooooooooooooooooo")
    console.log(KsGraphPreview)

    registry.add('ks_graph_preview', KsGraphPreview);

    return KsGraphPreview;

});