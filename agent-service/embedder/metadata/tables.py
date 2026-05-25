TABLE_METADATA = {
    "products": {
        "description": (
            "Master product catalogue. Each row is one SKU listed on the platform. "
            "Contains pricing (MRP and selling price), discount percentage, brand, "
            "category, subcategory, ratings, and review counts. "
            "Use for product search, category analysis, brand comparison, "
            "price range queries, and discount analysis."
        ),
        "use_when": (
            "product catalogue — category brand price MRP discount rating reviews; "
            "Electronics Fashion Grocery Books Sports Beauty Toys Automotive Office; "
            "not for sales volume or revenue (use order_items for that)"
        ),
        "relates_to": ["order_items", "inventory"],
    },
    "sellers": {
        "description": (
            "Registered seller / merchant profiles on the platform. "
            "Contains seller name, type (Brand Store, Reseller, Individual etc.), "
            "location (city, state), GSTIN, rating, verification status, "
            "and bank details. Use for seller performance, top sellers, "
            "verified vs unverified seller analysis, and seller geography."
        ),
        "use_when": (
            "seller merchant profile — name type rating verified GSTIN city state; "
            "Brand Store Authorised Reseller Individual Wholesaler Distributor; "
            "not for revenue or product queries (use order_items for earnings)"
        ),
        "relates_to": ["order_items", "inventory"],
    },
    "customers": {
        "description": (
            "Registered customer profiles with demographic and location data. "
            "Contains name, email, phone, date of birth, gender, city, state, "
            "pincode, address, premium membership status, and registration date. "
            "Use for customer segmentation, geographic analysis, premium member "
            "queries, demographic breakdowns, and new customer registration trends."
        ),
        "use_when": (
            "customer profile — gender age premium membership city state registration date; "
            "Male Female premium is_premium Maharashtra Gujarat Karnataka; "
            "not for what they bought or how they paid (use orders + order_payments)"
        ),
        "relates_to": ["orders"],
    },
    "inventory": {
        "description": (
            "Stock levels for each product at each seller's warehouse. "
            "Tracks quantity in stock, reorder level threshold, reorder quantity, "
            "last restock date, next planned restock, and in-stock boolean flag. "
            "Use for low stock alerts, out-of-stock analysis, warehouse distribution, "
            "and inventory health across Mumbai Delhi Bengaluru etc. warehouses."
        ),
        "use_when": (
            "stock levels warehouse — low stock out of stock reorder quantity is_in_stock; "
            "Mumbai Delhi Bengaluru Hyderabad Chennai Kolkata Pune Ahmedabad warehouse; "
            "not for sales or orders (use order_items for sold quantities)"
        ),
        "relates_to": ["products", "sellers"],
    },
    "orders": {
        "description": (
            "Master order header table. One row per customer order. "
            "Contains order status, timestamps (placed, shipped, delivered), "
            "shipping type, shipping charge, delivery partner, tracking number, "
            "delivery address, coupon code, and coupon discount. "
            "Use for total order counts, delivery performance, cancellation rates, "
            "return analysis, order trends over time, and shipping analysis. "
            "Join with order_items for product detail, order_payments for payment method."
        ),
        "use_when": (
            "order status delivery shipping — cancelled delivered returned shipped processing; "
            "coupon code SAVE10 FLAT50 DIWALI30 delivery partner Delhivery BlueDart Ekart; "
            "not for payment method or revenue (use order_payments for UPI EMI Wallet)"
        ),
        "relates_to": ["customers", "order_items", "order_payments"],
    },
    "order_items": {
        "description": (
            "Line-item detail for every order — one row per product per order. "
            "Contains product, seller, quantity, unit price, MRP, discount percent, "
            "subtotal, GST rate (5/12/18/28%), GST amount, and return flag. "
            "This is the central fact table — use it for revenue calculation, "
            "product sales volume, category-level revenue, GST analysis, "
            "seller earnings, and cross-table joins (products + orders + payments)."
        ),
        "use_when": (
            "revenue subtotal GST returned items — central fact table for all sales data; "
            "quantity sold seller earnings category revenue 5% 12% 18% 28% GST slab; "
            "join hub — connects products sellers orders payments for any cross-table query"
        ),
        "relates_to": ["orders", "products", "sellers"],
    },
    "order_payments": {
        "description": (
            "Payment transactions for every order. One row per payment attempt; "
            "some orders have two rows due to split payments. "
            "Contains payment method, status, amount, transaction ID, payment timestamp, "
            "EMI months, wallet name, coupon discount applied, and grand total. "
            "Use for payment method analysis (UPI, COD, Credit Card, Debit Card, "
            "Net Banking, EMI, Wallet), refund tracking, failed payment analysis, "
            "Paytm PhonePe Amazon Pay Google Pay Mobikwik FreeCharge wallet breakdown, "
            "revenue collection, EMI tenure analysis, and split payment queries."
        ),
        "use_when": (
            "payment method how customer paid — UPI, COD, EMI, Credit Card, Debit Card, Net Banking, Wallet; "
            "Paytm, PhonePe, Google Pay, Amazon Pay, Mobikwik, FreeCharge, EMI tenure months; "
            "not for order status or shipping (use orders for that)"
        ),
        "relates_to": ["orders", "customers"],
    },
}
