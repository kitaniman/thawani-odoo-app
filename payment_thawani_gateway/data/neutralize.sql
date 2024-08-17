-- disable thawani payment provider
UPDATE payment_provider
   SET thawani_secret_key = NULL,
       thawani_publishable_key = NULL,
       thawani_webhook_secret = NULL;