// WARNING: DO NOT USE IN PRODUCTION - Exposes sensitive API keys!

document.getElementById('checkout-button').addEventListener('click', async () => {
    const finalAmount = 1000; // Example amount, replace with actual cart total
    
    // --- Step 1: Generate Token ---
    const tokenUrl = "https://pluraluat.v2.pinepg.in/api/auth/v1/token";
    const tokenHeaders = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Cookie': 'TS01922b00=012ce8bebce0b0c60363ded49952700396b8fd3ed58c8ddb45667e53c44bdcc35e56c9005c4a56f29e572ed999e679f039d8d96016'
    };
    const tokenPayload = {
      "client_id": "6a7a29ca-ad0f-4c8b-aff9-f1ebfa0a3548", // EXPOSED
      "client_secret": "24979829127b40139a3d581eb1da592f", // EXPOSED
      "grant_type": "client_credentials"
    };

    try {
        const tokenResponse = await fetch(tokenUrl, {
            method: 'POST',
            headers: tokenHeaders,
            body: JSON.stringify(tokenPayload)
        });

        if (!tokenResponse.ok) {
            const errorText = await tokenResponse.text();
            console.error('Token generation failed:', errorText);
            alert('Failed to generate token: ' + errorText);
            return;
        }

        const tokenData = await tokenResponse.json();
        const accessToken = tokenData.access_token;
        console.log('Generated Access Token:', accessToken);

        // --- Step 2: Create Order ---
        const orderUrl = "https://pluraluat.v2.pinepg.in/api/pay/v1/orders";
        const orderHeaders = {
            'Merchant-ID': '110553', // EXPOSED
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
            'Cookie': 'TS01922b00=012ce8bebce0b0c60363ded49952700396b8fd3ed58c8ddb45667e53c44bdcc35e56c9005c4a56f29e572ed999e679f039d8d96016'
        };
        const orderPayload = {
            "merchant_order_reference": `order-${Date.now()}-${Math.floor(Math.random() * 1000)}`, // Simple unique ID
            "order_amount": {
                "value": finalAmount,
                "currency": "INR"
            },
            "pre_auth": false,
            "purchase_details": {
                "customer": {
                    "email_id": "joe.sam@example.com",
                    "first_name": "Joe",
                    "last_name": "Kumar",
                    "mobile_number": "192192883",
                    "billing_address": {
                        "address1": "H.No 15, Sector 17",
                        "address2": "",
                        "address3": "",
                        "pincode": "61232112",
                        "city": "CHANDIGARH",
                        "state": "PUNJAB",
                        "country": "INDIA"
                    },
                    "shipping_address": {
                        "address1": "H.No 15, Sector 17",
                        "address2": "string",
                        "address3": "string",
                        "pincode": "144001123",
                        "city": "CHANDIGARH",
                        "state": "PUNJAB",
                        "country": "INDIA"
                    }
                },
                "merchant_metadata": {
                    "key1": "value1",
                    "key2": "value2"
                }
            }
        };

        const orderResponse = await fetch(orderUrl, {
            method: 'POST',
            headers: orderHeaders,
            body: JSON.stringify(orderPayload)
        });

        if (!orderResponse.ok) {
            const errorText = await orderResponse.text();
            console.error('Order creation failed:', errorText);
            alert('Failed to create order: ' + errorText);
            return;
        }

        const orderData = await orderResponse.json();


        // --- Step 3: Call checkout copy ---

        const checkoutUrl = "https://pluraluat.v2.pinepg.in/api/checkout/v1/orders";
        
        const checkoutMerchantOrderReference = orderData.merchant_order_reference; // Use order reference from previous step or generate a new one
        const checkoutHeaders = {
            'Merchant-ID': '110553', // EXPOSED
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
            'Cookie': 'TS01922b00=012ce8bebce0b0c60363ded49952700396b8fd3ed58c8ddb45667e53c44bdcc35e56c9005c4a56f29e572ed999e679f039d8d96016'
        };

        const checkoutPayload = {
            "merchant_order_reference": checkoutMerchantOrderReference, // Simple unique ID
            "order_amount": {
                "value": finalAmount,
                "currency": "INR"
            },
            "pre_auth": false,
            "purchase_details": {
                "customer": {
                    "email_id": "joe.sam@example.com",
                    "first_name": "Joe",
                    "last_name": "Kumar",
                    "mobile_number": "192192883",
                    "billing_address": {
                        "address1": "H.No 15, Sector 17",
                        "address2": "",
                        "address3": "",
                        "pincode": "61232112",
                        "city": "CHANDIGARH",
                        "state": "PUNJAB",
                        "country": "INDIA"
                    },
                    "shipping_address": {
                        "address1": "H.No 15, Sector 17",
                        "address2": "string",
                        "address3": "string",
                        "pincode": "144001123",
                        "city": "CHANDIGARH",
                        "state": "PUNJAB",
                        "country": "INDIA"
                    }
                },
                "merchant_metadata": {
                    "key1": "value1",
                    "key2": "value2"
                }
            }
        };

        const checkoutResponse = await fetch(checkoutUrl, {
            method: 'POST',
            headers: checkoutHeaders,
            body: JSON.stringify(checkoutPayload)
        });

        if (!checkoutResponse.ok) {
            const errorText = await checkoutResponse.text();
            console.error('Order creation failed:', errorText);
            alert('Failed to create order: ' + errorText);
            return;
        }

        const checkoutData = await checkoutResponse.json();

        const redirectUrl = checkoutData.redirect_url;

        if (redirectUrl) {
            // Step 3: Redirect to Payment Page
            window.location.replace(redirectUrl);
        } else {
            alert('Error: Payment URL not received.');
        }

    } catch (error) {
        console.error('Error during payment initiation:', error);
        alert('An error occurred while preparing for payment. Please try again.');
    }
});