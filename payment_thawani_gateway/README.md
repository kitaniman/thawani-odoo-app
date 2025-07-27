# Odoo Thawani Payment Gateway Intetgration Addon
An application that adds support for Thawani payment gateway to Odoo.

# Installation

The add addon should be installed in a folder named `payment_thawani` for example: `path/to/extra-addons/payment_thawani`. If not done this way Odoo will raise an error about `payment_thawani` module import not found.

## Configuration
The currency must be set to `OMR` in the website before using the module, otherwise a message
will be shown in the checkout page saying no appropriate payment method was found. This
setting can be found in `Settings > Invoicing > Currencies > Main Currency`.

## Adding Thawani Provider

The Thawani payment provider must be added to `Invoicing > Configuration > Payment Providers`.

## Thawani API Documentaiton 

Thawani API [Docs](https://thawani-technologies.stoplight.io/docs/thawani-ecommerce-api/5534c91789a48-thawani-e-commerce-api) contain an explanation of how the API works in addition to a secre and a publishable key for testing (when using the test mode)

## Features

* Payments using the Thawani's checkout sessions.
* Support for test mode.
* Handling of discounts.

# Example Testing Docker Compoer

An example testing `docker-compose.yml` can be found in [thawani-odoo-app](https://github.com/kitaniman/thawani-odoo-app) for a quick setup and testing.

## Issue Reporting Tracking

Issues are tracked on the [GitHub Issues page](https://github.com/kitaniman/thawani-odoo-app/issues). In case of trouble, please check there if your issue has already been reported. Feel free to contact me via LinkedIn (can be found in my [GitHub profile](https://github.com/kitaniman)) I recieve any questions or positive comments. :)
