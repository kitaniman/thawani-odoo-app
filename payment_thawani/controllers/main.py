import logging
import pprint

from werkzeug.exceptions import Conflict

from odoo import http
from odoo.http import request


_logger = logging.getLogger(__name__)


class ThawaniPayController(http.Controller):
    _success_endpoint = '/payment/thawani/success'
    _cancel_endpoint = '/payment/thawani/cancel'
    _webhook_url = '/payment/thawani/webhook'

    @http.route(_success_endpoint+'/<path:reference>', type='http', auth='public', methods=['GET'])
    def thawani_confirm_checkout(self, **data):
        """ Process the notification data sent by Thawani after redirection.

        :param dict data: The notification data.
        """
        # Don't process the notification data as they contain no valuable information except for the
        # reference and Thawani doesn't expose an endpoint to fetch the data from the API.
        _logger.info("Received a payment confirmation request with data:\n%s", pprint.pformat(data))
        
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'thawani', dict(reference=data['reference'].upper())
        )

        self._verify_payment_status(tx_sudo, {'paid'})

        tx_sudo._set_done()

        return request.redirect('/payment/status')

    @http.route(_cancel_endpoint+'/<path:reference>', type='http', auth='public', methods=['GET'])
    def thawani_cancel_checkout(self, **data):
        """ Process the notification data sent by Thawani after redirection.

        :param dict data: The notification data.
        """
        # Don't process the notification data as they contain no valuable information except for the
        # reference and Thawani doesn't expose an endpoint to fetch the data from the API.
        _logger.info("Received a pay cancelation request with data:\n%s", pprint.pformat(data))

        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'thawani', dict(reference=data['reference'].upper())
        )

        self._verify_payment_status(tx_sudo, {'cancelled', 'unpaid'})

        tx_sudo._set_canceled()
        
        return request.redirect('/payment/status')

    
    @staticmethod
    def _verify_payment_status(tx_sudo, possible_payment_statuses: set):
        session_json = tx_sudo.provider_id._thawani_make_request(
            endpoint='checkout/session/'+tx_sudo.thawani_checkout_session_id,
            method='GET'
        )
        _logger.info("Retrieved Thawani checkout session info:\n%s", pprint.pformat(session_json))

        payment_status = session_json['data']['payment_status']

        if payment_status not in possible_payment_statuses:
            message = "The alleged payment statuses ("+str(possible_payment_statuses)+") do not contain the current payment status ("+str(payment_status)+")."
            _logger.warning(message)
            raise Conflict(message)
