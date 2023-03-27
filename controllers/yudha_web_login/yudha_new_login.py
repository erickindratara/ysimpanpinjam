# -*- encoding: utf-8 -*-

import logging
import werkzeug.exceptions
import werkzeug.utils
from werkzeug.urls import iri_to_uri
import werkzeug
import odoo
from odoo.tools.translate import _
from odoo import http, tools
from odoo.http import request, Response
from odoo.addons.web.controllers.main import Home,WebClient
import requests
_logger = logging.getLogger(__name__)

db_monodb = http.db_monodb

def _get_login_redirect_url(uid, redirect=None):
    if request.session.uid: # fully logged
        return redirect or '/web'
    url = request.env(user=uid)['res.users'].browse(uid)._mfa_url()
    if not redirect:
        return url

    parsed = werkzeug.urls.url_parse(url)
    qs = parsed.decode_query()
    qs['redirect'] = redirect
    return parsed.replace(query=werkzeug.urls.url_encode(qs)).to_url()


def abort_and_redirect(url):
    r = request.httprequest
    response = werkzeug.utils.redirect(url, 302)
    response = r.app.get_response(r, response, explicit_session=False)
    werkzeug.exceptions.abort(response)


def ensure_db(redirect='/web/database/selector'):
    db = request.params.get('db') and request.params.get('db').strip()

    # Ensure db is legit
    if db and db not in http.db_filter([db]):
        db = None

    if db and not request.session.db:
        r = request.httprequest
        url_redirect = werkzeug.urls.url_parse(r.base_url)
        if r.query_string:
            # in P3, request.query_string is bytes, the rest is text, can't mix them
            query_string = iri_to_uri(r.query_string)
            url_redirect = url_redirect.replace(query=query_string)
        request.session.db = db
        abort_and_redirect(url_redirect)

    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db

    if not db:
        db = db_monodb(request.httprequest)

    if not db:
        werkzeug.exceptions.abort(werkzeug.utils.redirect(redirect, 303))

    if db != request.session.db:
        request.session.logout()
        abort_and_redirect(request.httprequest.url)

    request.session.db = db

class YudhaNewLogin(Home):

    def _login_redirect(self, uid, redirect=None):
        return _get_login_redirect_url(uid, redirect)

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        myuse_blocked = request.env['ir.config_parameter'].sudo().get_param('used_blocked')
        block_access = request.env['ir.config_parameter'].sudo().get_param('blocked_by')
        isproxy = False
        myreq =['HTTP_VIA',
                'VIA',
                'Proxy-Connection',
                'HTTP_X_FORWARDED_FOR',
                'HTTP_FORWARDED_FOR',
                'HTTP_X_FORWARDED',
                'HTTP_FORWARDED',
                'HTTP_CLIENT_IP',
                'HTTP_FORWARDED_FOR_IP',
                'X-PROXY-ID',
                'MT-PROXY-ID',
                'X-TINYPROXY',
                'X_FORWARDED_FOR',
                'FORWARDED_FOR',
                'X_FORWARDED',
                'FORWARDED',
                'CLIENT-IP',
                'CLIENT_IP',
                'PROXY-AGENT',
                'HTTP_X_CLUSTER_CLIENT_IP',
                'FORWARDED_FOR_IP',
                'HTTP_PROXY_CONNECTION']
        for allreq in myreq:
            if request.httprequest.environ.get(allreq):
                isproxy = True
        if isproxy:
            myvalues = []
            return request.render('yudha_simpan_pinjam.access_denied_proxy', myvalues)
        if myuse_blocked:
            if block_access == 'by_country':
                myvalues = []
                contry_blocked =  request.env['ir.config_parameter'].sudo().get_param('blocked_by_country')
                user_country = request.env['res.country'].sudo().search([('id','=',int(contry_blocked))])
                cekcountry = 'http://ip-api.com/json'
                headersauth = {'Content-type': 'application/json'}
                req = requests.get(cekcountry, headers=headersauth)
                # if  req.json().get('country') == user_country.name:
                #     return request.render('yudha_simpan_pinjam.access_denied_country', myvalues)
            elif block_access == 'by_ip':
                myvalues = []
                contry_blocked = request.env['ir.config_parameter'].sudo().get_param('blocked_by_ip')
                cekip = 'http://ip-api.com/json'
                headersauth = {'Content-type': 'application/json'}
                req = requests.get(cekip, headers=headersauth)
                if req.json().get('query') == contry_blocked:
                    return request.render('yudha_simpan_pinjam.access_denied_ip', myvalues)
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID
        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            if myuse_blocked:
                myuser = request.env['res.users'].sudo().search([('login', '=', request.params['login'])])
                allowed_attempts = int(request.env["ir.config_parameter"].sudo().get_param("allowed_login_attempts"))
                if  myuser.login_attempt >= allowed_attempts:
                    values['error'] = _("Maximum Login Attempt")
                else:
                    if myuse_blocked:
                        if block_access == 'by_user':
                            user_blocked = request.env['ir.config_parameter'].sudo().get_param('blocked_by_username')
                            name_user = request.env['res.users'].sudo().search([('id', '=', int(user_blocked))])
                            if request.params['login'] == name_user.login:
                                values['error'] = _("Blocked User Login")
                            else:
                                try:
                                    uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                                    request.params['login_success'] = True
                                    if request.session.uid:
                                        myuser.write({'login_attempt': 0})
                                    return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                                except odoo.exceptions.AccessDenied as e:
                                    request.uid = old_uid
                                    myuser.write({'login_attempt': int(myuser.login_attempt) + 1})
                                    if e.args == odoo.exceptions.AccessDenied().args:
                                        values['error'] = _("Wrong login/password")
                                    else:
                                        values['error'] = e.args[0]
                        else:
                            try:
                                uid = request.session.authenticate(request.session.db, request.params['login'],
                                                                   request.params['password'])
                                request.params['login_success'] = True
                                if request.session.uid:
                                    myuser.write({'login_attempt': 0})
                                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                            except odoo.exceptions.AccessDenied as e:
                                request.uid = old_uid
                                myuser.write({'login_attempt': int(myuser.login_attempt) + 1})
                                if e.args == odoo.exceptions.AccessDenied().args:
                                    values['error'] = _("Wrong login/password")
                                else:
                                    values['error'] = e.args[0]
                    else:
                        try:
                            uid = request.session.authenticate(request.session.db, request.params['login'],
                                                               request.params['password'])
                            request.params['login_success'] = True
                            if request.session.uid:
                                myuser.write({'login_attempt': 0})
                            return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                        except odoo.exceptions.AccessDenied as e:
                            request.uid = old_uid
                            myuser.write({'login_attempt': int(myuser.login_attempt) + 1})
                            if e.args == odoo.exceptions.AccessDenied().args:
                                values['error'] = _("Wrong login/password")
                            else:
                                values['error'] = e.args[0]
            else:
                try:
                    uid = request.session.authenticate(request.session.db, request.params['login'],
                                                       request.params['password'])
                    request.params['login_success'] = True
                    return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                except odoo.exceptions.AccessDenied as e:
                    request.uid = old_uid
                    if e.args == odoo.exceptions.AccessDenied().args:
                        values['error'] = _("Wrong login/password")
                    else:
                        values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')
        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        param_obj = request.env['ir.config_parameter'].sudo()
        style = param_obj.get_param('login_background.style')
        background = param_obj.get_param('login_background.background')
        values['background_color'] = param_obj.get_param('login_background.color')
        background_image = param_obj.get_param('login_background.background_image')
        url_root = request.httprequest.url_root
        if background == 'image':
            image_url = ''
            if background_image:
                image_url = f'{url_root}web/image?' + 'model=yudha.login.image&id=' + background_image + '&field=image'
                values['background_src'] = image_url
                values['background_color'] = ''
        else:
            values['background_src'] = ''
        hasil = None
        if style == 'default' or style is False:
            hasil = request.render('web.login', values)
        elif style == 'left':
            hasil = request.render('yudha_simpan_pinjam.left_login_template', values)
        elif style == 'right':
            hasil = request.render('yudha_simpan_pinjam.right_login_template', values)
        else:
            hasil = request.render('yudha_simpan_pinjam.middle_login_template', values)
        #response.headers['X-Frame-Options'] = 'DENY'
        return hasil

class WebClientInherit(WebClient):


    @http.route('/web/webclient/getconfig', type='json', auth="none")
    def getresconfig(self):
        res = request.env['res.config.settings'].sudo().get_values()
        return res