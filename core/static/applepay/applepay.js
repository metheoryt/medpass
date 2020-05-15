const paymentRequest = {
    total: {
        label: 'wooppay.com',
        amount: 50
    },
    countryCode: 'RU',
    currencyCode: 'RUR',
    merchantCapabilities: ['supports3DS'],
    supportedNetworks: ['masterCard', 'visa']
};

let performValidation = (validation_url) => {
    return new Promise(function(resolve, reject) {
    setTimeout(() => {resolve('opaque-session-object');}, 5000);
    });
}

let performAuthorization = (pk_payment) => {
    return new Promise(function(resolve, reject) {
        console.log(pk_payment)
        resolve(true);
    });
}


if (window.ApplePaySession) {
    //Apple Pay JS API доступно
    let merchantIdentifier = 'merchant.com.wooppay.processing';
    let promise = window.ApplePaySession.canMakePaymentsWithActiveCard(merchantIdentifier);
    promise.then(function (canMakePayments) {
        if (canMakePayments) {
            // у пользователя есть активная карта Apple Pay
            // отображаем кнопку
//            document.getElementById('applepay').style.display = "block";
            document.getElementById('applepay-btn').onclick = function (event) {
                const applePaySession = new window.ApplePaySession(1, paymentRequest);
                applePaySession.onvalidatemerchant = (event) => {
                    // отправляем запрос на валидацию сессии
                    console.log(event);
                    alert(event);
                    performValidation(event.validationURL)
                        .then((merchantSession) => {
                            // завершаем валидацию платежной сессии
                            applePaySession.completeMerchantValidation(merchantSession);
                        })
                        .catch((reason) => {
                                console.log(reason);
                                applePaySession.abort();
                                // показ сообщения об ошибке и т.п.
                            }
                        );
                };
                applePaySession.onpaymentauthorized = (pk_payment) => {
                    performAuthorization(pk_payment)
                        .then((success) => {
                            if (success) {
                                applePaySession.completePayment(window.ApplePaySession.STATUS_SUCCESS);
                            } else {
                                applePaySession.completePayment(window.ApplePaySession.STATUS_FAILURE);
                            }
                        })
                        .catch((reason) => {
                            console.log(reason);
                            applePaySession.completePayment(window.ApplePaySession.STATUS_FAILURE);
                        })
                };
                applePaySession.begin();
            }
        }
    });

}

