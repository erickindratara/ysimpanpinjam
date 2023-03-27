odoo.define('yudha_simpan_pinjam.GantiBackgroundImage', function (require) {
    "use strict";

    const session = require('web.session');
    const WebClient = require('web.WebClient');
    var rpc    = require('web.rpc');
    const AbstractWebClient = require('web.AbstractWebClient');
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var FieldMany2One = require('web.relational_fields').FieldMany2One;
    var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
    var Widget = require('web.Widget');
    var AbstractController = require('web.AbstractController');

    WebClient.include({
        async load_menus() {
            var self = this;
            const menuData = await this._super(...arguments);
            var mystyles = '';
            session.rpc('/web/webclient/getconfig', {})
            .then(function (result) {
                if (result.style ==='default'){
                } else {
                    if (result.background === 'image'){
                        const company_id = session.user_context.allowed_company_ids[0];
                        const url = session.url('/web/image', {
                            id: company_id,
                            model: 'res.company',
                            field: 'Yudha_background',
                        });
                         const mybody = $('body');
                         mybody.attr("class", 'o_web_client o_home_menu_background o_home_menu_background_custom');
                         mybody.attr('style', 'background-image: url('+ url+')');
                    } else {
                         const mybody = $('body');
                         mybody.attr("class", 'o_web_client o_home_menu_background o_home_menu_background_custom');
                         mybody.attr('style', 'background-color: ' +result.color +';');
                    }
                    const maintop = $('nav[class="o_main_navbar"]');
                    maintop.attr('style', 'background-color: ' +result.topmenucolor);
//                    var myinfo ='<div class="row justify-center" style="padding-bottom:80px;padding-top:5px;"> <div class="col-md-4"> <img src="/web_responsive/static/src/img/logo-polri.png" alt="logo" style="display:block;margin-left: auto; margin-right: auto;width: 50%"> </div> <div class="col-md-8" style="display:flex;align-items:center"> <h1 style="font-size:40px; color:#FFFFFF;justify-content:center;">SISTEM MANAJEMEN ASET</h1> </div> </div>';
//                    $('o_home_menu .o_search_hidden').append(myinfo);
//                         alert($('.o_home_menu .o_search_hidden'));
                 }

             });
            return menuData;
        },

        /**
         * @override
         */
        async toggleHomeMenu(display) {
            var self = this;

            return this._super(...arguments);
        },

        _instanciateHomeMenuWrapper() {
            const homeMenuManager = this._super(...arguments);
            if (this.homeMenuStyle) {
                homeMenuManager.state.style = this.homeMenuStyle;
            }
            return homeMenuManager;
        },
    });

    AbstractController.include({
        async start() {
            var self = this;
            var mystyles = '';
            const menuData = await this._super(...arguments);
            session.rpc('/web/webclient/getconfig', {})
            .then(function (result) {
                mystyles = result;
                if (result.style ==='default'){
                } else {
                    if (result.background === 'image'){
                        const company_id = session.user_context.allowed_company_ids[0];
                        const url = session.url('/web/image', {
                            id: company_id,
                            model: 'res.company',
                            field: 'Yudha_background',
                        });
                        var mystyle = `background-image: url(${url})`;
                        const content = $('.o_content .settings');
                        content.css('background-image', 'url('+ url+')');
                        const listview = $('.o_content .o_list_view');
                        listview.css('background-image', 'url('+ url+')');
                        const formview = $('.o_content .o_form_view .o_form_sheet_bg');
                        formview.attr('style', 'background-image: url('+ url+')');
                    } else {
                        const content = $('.o_content .settings');
                        content.attr('style', 'background-color: '+ mystyles.color);
                        const listview = $('.o_content .o_list_view');
                        listview.attr('style', 'background-color: '+ mystyles.color);
                        const formview = $('.o_content .o_form_view .o_form_sheet_bg');
                        formview.attr('style', 'background-color: '+ mystyles.color);
                    }
                }
            });

        return menuData;
        }
    });


});
