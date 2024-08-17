import logging

from werkzeug.urls import url_join

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.payment_thawani.controllers.main import ThawaniPayController
from odoo.addons.payment_thawani.utils import  prepare_product_name

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    thawani_checkout_session_id = fields.Char(
        string="Thawani Checkout Session ID",
        help="This field holds the Checkout Session ID related to this payment transaction."
    )

    def _get_specific_rendering_values(self, processing_values):
        """ Override of `payment` to return Thawani-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`.

        :param dict processing_values: The generic and specific processing values of the
                                       transaction.
        :return: The dict of provider-specific processing values.
        :rtype: dict
        """
        self.ensure_one()

        base_url = self.provider_id.get_base_url()

        # Get all sale order lines that have an amount > 0 (since thawani does not accespt products with 0 value)
        products = [
            {
                'name': prepare_product_name(sale_order_line.name),
                'quantity': int(sale_order_line.product_uom_qty),
                'unit_amount': int(sale_order_line.price_reduce_taxinc*1000)
            }
            for sale_order in self.sale_order_ids
            for sale_order_line in self.env['sale.order.line'].search([('order_id', '=', sale_order.id)])
            if int(sale_order_line.price_reduce_taxinc*1000) > 0
        ]
        discounts = [
            {
                'name': prepare_product_name(sale_order_line.name),
                'quantity': int(sale_order_line.product_uom_qty),
                'unit_amount': int(sale_order_line.price_reduce_taxinc*1000)
            }
            for sale_order in self.sale_order_ids
            for sale_order_line in self.env['sale.order.line'].search([('order_id', '=', sale_order.id)])
            if int(sale_order_line.price_reduce_taxinc*1000) < 0
        ]
        if not products:
            total_amount = int(processing_values['amount']*1000)

            if total_amount <= 0:
                raise ValidationError("Cannot create a checkout session as total amount is <= 0")

            products = [
                {
                    'name': 'Reference ID '+processing_values['reference'],
                    'quantity': 1,
                    'unit_amount': total_amount
                }
            ]
        all_products = []
        if len(discounts)>0:
            discount_amount = sum([discount['unit_amount'] for discount in discounts])
            products_count = sum([product['quantity'] for product in products])
            dics_per_unit = int(discount_amount/products_count)
            for product in products:
                product['unit_amount'] = product['unit_amount'] + dics_per_unit
                all_products.append(product)
        else:
            all_products = products


        _logger.info('Products:\n'+str(products))

        session_json = self.provider_id._thawani_make_request(
            endpoint='checkout/session',
            json={
                "client_reference_id": processing_values['reference'],
                "mode": "payment",
                "products": all_products,
                "success_url": url_join(
                    base=base_url,
                    url=ThawaniPayController._success_endpoint+'/'+processing_values['reference'].lower()
                ),
                "cancel_url": url_join(
                    base=base_url,
                    url=ThawaniPayController._cancel_endpoint+'/'+processing_values['reference'].lower()
                ),
                "metadata": {}
            },
            method='POST'
        )

        _logger.info('The result of craeting a new checkout session was the following:\n'+str(session_json))

        session_id = session_json['data']['session_id']

        self.thawani_checkout_session_id = session_id

        payment_page_url = url_join(
            base=self.provider_id._thawani_get_payment_page_url(),
            url=session_id
        )

        rendering_values = {
            'session_url': payment_page_url,
            'key': self.provider_id.thawani_publishable_key
        }
        return rendering_values

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on Thawani data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)

        if provider_code != 'thawani' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')

        if reference:
            tx = self.search([('reference', '=', reference), ('provider_code', '=', 'thawani')])
        else:
            raise ValidationError("Thawani: " + _("Received data with missing merchant reference"))

        if not tx:
            raise ValidationError(
                "Thawani: " + _("No transaction found matching reference %s.", reference)
            )

        return tx
