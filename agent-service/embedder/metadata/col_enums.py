COL_ENUMS = {
    "products": {
        "category": (
            "Electronics | Fashion | Home & Kitchen | Books | "
            "Sports & Fitness | Beauty & Personal Care | "
            "Toys & Baby Products | Grocery & Gourmet | "
            "Automotive | Office Products"
        ),
        "subcategory": (
            "Mobiles | Laptops | Tablets | Cameras | Headphones | Speakers | "
            "Smart Watches | TV & Home Theatre | Air Conditioners | Refrigerators | "
            "Men's Clothing | Women's Clothing | Kids' Clothing | Footwear | "
            "Watches | Sunglasses | Bags & Luggage | Jewellery | "
            "Cookware | Bedding | Home Décor | Lighting | Cleaning | Furniture | "
            "Fiction | Non-Fiction | Academic | Children's Books | Self-Help | "
            "Cricket | Football | Badminton | Cycling | Yoga | Running | "
            "Skincare | Haircare | Makeup | Fragrances | Men's Grooming | Baby Care | "
            "Educational Toys | Board Games | Building Blocks | Puzzles | "
            "Staples | Snacks | Beverages | Organic | Ready to Cook | Dry Fruits | "
            "Car Accessories | Bike Accessories | Helmets | GPS | Batteries | "
            "Stationery | Printers | Office Furniture | Calculators | Whiteboards"
        ),
        "is_active": "true | false",
        "discount_percent": "0 | 5 | 10 | 15 | 20 | 25 | 30 | 40 | 50 | 60 | 70",
    },
    "sellers": {
        "seller_type": (
            "Brand Store | Authorised Reseller | Individual Seller | "
            "Wholesaler | Distributor"
        ),
        "is_verified": "true | false",
        "city": (
            "Mumbai | Delhi | Bengaluru | Hyderabad | Ahmedabad | Chennai | "
            "Kolkata | Pune | Jaipur | Lucknow | Surat | Kanpur | Nagpur | "
            "Indore | Thane | Bhopal | Visakhapatnam | Patna | Vadodara | "
            "Ghaziabad | Ludhiana | Agra | Nashik | Faridabad | Meerut"
        ),
        "state": (
            "Maharashtra | Delhi | Karnataka | Telangana | Gujarat | Tamil Nadu | "
            "West Bengal | Rajasthan | Uttar Pradesh | Punjab | Madhya Pradesh | "
            "Bihar | Andhra Pradesh | Haryana | Jharkhand | Assam | Chhattisgarh"
        ),
    },
    "customers": {
        "gender": "Male | Female | Other",
        "is_premium": "true | false  -- premium members get priority delivery and offers",
        "city": (
            "Mumbai | Delhi | Bengaluru | Hyderabad | Ahmedabad | Chennai | "
            "Kolkata | Pune | Jaipur | Lucknow | Surat | Kanpur | Nagpur | "
            "Indore | Thane | Bhopal | Visakhapatnam | Patna | Vadodara | "
            "Ghaziabad | Ludhiana | Agra | Nashik | Faridabad | Meerut | "
            "Rajkot | Varanasi | Aurangabad | Amritsar | Ranchi | Coimbatore | "
            "Jodhpur | Madurai | Raipur | Kota | Chandigarh | Guwahati | Mysuru"
        ),
        "state": (
            "Maharashtra | Delhi | Karnataka | Telangana | Gujarat | Tamil Nadu | "
            "West Bengal | Rajasthan | Uttar Pradesh | Punjab | Madhya Pradesh | "
            "Bihar | Andhra Pradesh | Haryana | Jharkhand | Assam | Chhattisgarh | "
            "Chandigarh | Jammu & Kashmir"
        ),
    },
    "inventory": {
        "warehouse": (
            "Mumbai | Delhi | Bengaluru | Hyderabad | Chennai | "
            "Kolkata | Pune | Ahmedabad"
        ),
        "is_in_stock": "true | false  -- false means product is currently out of stock",
    },
    "orders": {
        "order_status": (
            "delivered | shipped | processing | cancelled | returned | failed_delivery"
        ),
        "shipping_type": "Standard | Express | Same Day | Scheduled",
        "delivery_partner": (
            "Delhivery | BlueDart | Ekart | DTDC | XpressBees | "
            "Shadowfax | Dunzo | Ecom Express"
        ),
        "is_gift": "true | false",
        "coupon_code": (
            "SAVE10 | FLAT50 | SUMMER20 | DIWALI30 | NEWUSER  "
            "-- empty string means no coupon used"
        ),
        "shipping_city": (
            "Mumbai | Delhi | Bengaluru | Hyderabad | Ahmedabad | Chennai | "
            "Kolkata | Pune | Jaipur | Lucknow | Surat | and 40+ other Indian cities"
        ),
    },
    "order_items": {
        "gst_rate": "5 | 12 | 18 | 28  -- GST percentage slab applied to this item",
        "is_returned": "true | false  -- true means this specific item was returned",
        "quantity": "1 | 2 | 3 | 4 | 5  -- units of this product in the order",
    },
    "order_payments": {
        "payment_method": (
            "UPI | Credit Card | Debit Card | Net Banking | COD | EMI | Wallet"
        ),
        "payment_status": (
            "completed | refunded | failed  "
            "-- completed = successful, refunded = cancelled/returned orders, "
            "failed = payment gateway failure"
        ),
        "wallet_name": (
            "Paytm | PhonePe | Amazon Pay | Google Pay | Mobikwik | FreeCharge  "
            "-- only populated when payment_method = Wallet"
        ),
        "emi_months": (
            "3 | 6 | 9 | 12 | 18 | 24  "
            "-- EMI tenure in months, only populated when payment_method = EMI"
        ),
    },
}
