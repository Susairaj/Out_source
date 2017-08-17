odoo.define('pos_validate_client.pos_client', function (require) {
"use strict";
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var _t = core._t;

    var _super_order = screens.ActionpadWidget.prototype;
    screens.ActionpadWidget.include({
        raise_employee_required_error : function(){
            var self = this;
            self.gui.show_popup('error',{
            'title': _t('Customer Is not set yet.'),
            'body': _t('Please Select any customer from list'),
            });
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').unbind();

            this.$('.pay').click(function(){
                if(self.pos.config.is_customer_mandatory){
                    if(self.pos.get_client()) {
                        self.gui.show_screen('payment');
                    }
                    else{
                        self.raise_employee_required_error()
                        return;
                    }
                }
                else{
                   self.gui.show_screen('payment');
                }
            });
        },
    });
});