import logging
import pprint

import requests
from werkzeug.urls import url_join

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.payment_thawani.const import SUPPORTED_CURRENCIES, PROVIDER_ADDRESSES, DEFAULT_PAYMENT_METHODS


_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('thawani', "Thawani")],
        ondelete={'thawani': 'set default'}
    )

    thawani_publishable_key = fields.Char(
        string="Publishable Key",
        help="The key solely used to identify the account with Thawani",
        required_if_provider='thawani'
    )

    thawani_api_secret_key = fields.Char(
        string="Secret API Key",
        required_if_provider='thawani',
        groups='base.group_system'
    )

    # === BUSINESS METHODS ===#
    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()

        if self.code != 'thawani':
            return supported_currencies

        return supported_currencies.filtered(
            lambda c: c.name in SUPPORTED_CURRENCIES
        )

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        if self.code != 'thawani':
            return super()._get_default_payment_method_codes()
        return DEFAULT_PAYMENT_METHODS

    def _thawani_get_api_url(self):
        """ Return the URL of the API corresponding to the provider's state.

        :return: The API URL.
        :rtype: str
        """
        self.ensure_one()

        environment = 'production' if self.state == 'enabled' else 'test'
        return url_join(base=PROVIDER_ADDRESSES[environment], url='api/v1/')

    def _thawani_get_payment_page_url(self):
        """ Return the URL of the API corresponding to the provider's state.

        :return: The API URL.
        :rtype: str
        """
        self.ensure_one()

        environment = 'production' if self.state == 'enabled' else 'test'
        return url_join(base=PROVIDER_ADDRESSES[environment], url='pay/')

    def _thawani_make_request(self, endpoint, json=None, method='POST'):
        """ Make a request to Thawani API at the specified endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request.
        :param dict payload: The payload of the request.
        :param str method: The HTTP method of the request.
        :return The JSON-formatted content of the response.
        :rtype: dict
        :raise ValidationError: If an HTTP error occurs.
        """
        self.ensure_one()

        url = url_join(self._thawani_get_api_url(), endpoint)

        try:
            if method == 'GET':
                response = requests.get(
                    url,
                    json=json,
                    headers={'thawani-api-key': self.thawani_api_secret_key},
                    timeout=10
                )
            else:
                response = requests.post(
                    url,
                    json=json,
                    headers={'thawani-api-key': self.thawani_api_secret_key},
                    timeout=10
                )

            response.raise_for_status()

        except requests.exceptions.HTTPError:
            _logger.exception(
                "Invalid Thawani API request at %s with data:\n%s", url, pprint.pformat(json),
            )
            raise ValidationError("Thawani: " + _(
                "Thawani API returned the following response: %s\n%s",
                str(response),
                "'"+str(response.text)+"'"
            ))
        
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", url)
            raise ValidationError(
                "Thawani: " + _("Could not establish the connection to the API.")
            )
        
        return response.json()

    #=== ONCHANGE METHODS ===#

    @api.onchange('state')
    def _onchange_state_switch_is_published(self):
        """ Automatically publish or unpublish the provider depending on its state.

        :return: None
        """
        self.is_published = self.state != 'disabled'
