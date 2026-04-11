# For more information please refer to https://github.com/checkout/checkout-sdk-python
# For more information please refer to https://github.com/checkout/checkout-sdk-python
import checkout_sdk
from checkout_sdk.checkout_sdk import CheckoutSdk
from checkout_sdk.common.common import Phone, Address, CustomerRequest, Product
from checkout_sdk.common.enums import Country, Currency, PaymentSourceType
from checkout_sdk.payments.hosted.hosted_payments import HostedPaymentsSessionRequest
from checkout_sdk.payments.payments_previous import BillingInformation
from checkout_sdk.payments.payments import ThreeDsRequest, ProcessingSettings, RiskRequest, ShippingDetails, PaymentRecipient
from checkout_sdk.environment import Environment
from checkout_sdk.exception import CheckoutApiException, CheckoutArgumentException, CheckoutAuthorizationException




def create_checkout_page(SECRET_KEY, PROCESSING_CHANNEL_ID, products, description, success_url, failure_url, cancel_url, reference="reference", currency="USD", country="US", locale="en-US"):
    api = CheckoutSdk.builder() \
    .secret_key(SECRET_KEY) \
    .environment(Environment.sandbox()) \
    .build()
    # or 
    phone = Phone()
    phone.country_code = '44'
    phone.number = '4155552671'

    address = Address()
    # address.address_line1 = '123 High St.'
    # address.address_line2 = 'Flat 456'
    # address.city = 'London'
    # address.state = 'US'
    # address.zip = 'SW1A 1AA'
    address.country = country

    # customer_request = CustomerRequest()
    # customer_request.email = 'email@docs.checkout.com'
    # customer_request.name = 'awili'

    billing_information = BillingInformation()
    billing_information.address = address
    billing_information.phone = phone

    # shipping_details = ShippingDetails()
    # shipping_details.address = address
    # shipping_details.phone = phone

    # recipient = PaymentRecipient()
    # recipient.account_number = '123456789'
    # recipient.country = Country.ES
    # recipient.dob = '1922-05-18'
    # recipient.first_name = 'First'
    # recipient.last_name = 'Last'
    # recipient.zip = '12345'

    _products = []
    total = 0
    for prod in products:
        product = Product()
        product.name = prod['name']
        product.quantity = prod['quantity']
        product.price = prod['price']*100
        total+=prod['price']*100*prod['quantity']
        _products.append(product)

    # three_ds_request = ThreeDsRequest()
    # three_ds_request.enabled = True
    # three_ds_request.attempt_n3d = False

    processing_settings = ProcessingSettings()
    # processing_settings.aft = True

    # risk_request = RiskRequest()
    # risk_request.enabled = True

    request = HostedPaymentsSessionRequest()
    request.amount = total
    request.reference = reference
    request.currency = currency
    request.description = description
    request.billing = billing_information
    request.processing = processing_settings
    request.products = _products
    request.success_url = success_url
    request.failure_url = failure_url
    request.cancel_url = cancel_url
    request.locale = locale
    request.processing_channel_id = PROCESSING_CHANNEL_ID
    # request.allow_payment_methods = [PaymentSourceType.CARD, PaymentSourceType.KLARNA]
    print(request, request.processing_channel_id, request.products)
    response = api.hosted_payments.create_hosted_payments_page_session(request)
    return response
    # except CheckoutApiException as err:
    #     error_details = err.error_details
    #     print(error_details)
    #     # http_response = err.http_response
    # except CheckoutArgumentException as err:
    #     # Bad arguments
    #     print('Bad argument')

    # except CheckoutAuthorizationException as err:
    #     print('Invalid authorization')
        # Invalid authorization