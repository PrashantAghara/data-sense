TABLE_METADATA = {
    "products": {
        "description": (
            "Master product catalogue. Each row is one SKU listed on the platform. "
            "Contains pricing (MRP and selling price), discount percentage, brand, "
            "category, subcategory, ratings, and review counts. "
            "Use for product search, category analysis, brand comparison, "
            "price range queries, and discount analysis."
        ),
        "use_when": [
            "which products are in the Electronics Fashion Grocery Books Sports Beauty Toys Automotive Office category",
            "what is the price MRP selling price discount of a product",
            "which brand makes this product — Samsung Apple Xiaomi Amul Prestige Boat",
            "how many products are listed on the platform",
            "what are the top rated or best reviewed products",
            "find the cheapest or most expensive products",
            "which products are currently active or inactive",
            "show product details subcategory rating reviews",
            "compare products by brand or category",
            "products with highest discount percent",
        ],
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
        "use_when": [
            "which seller has the most returned items or highest return count",
            "which seller sold the most products or generated the highest revenue",
            "rank sellers by number of returns cancellations or refunds",
            "show top performing sellers by order count or earnings",
            "which sellers are verified or unverified on the platform",
            "what is the rating of a seller — seller performance score",
            "how many sellers are registered in Mumbai Delhi Bengaluru or other cities",
            "which sellers are Brand Store Authorised Reseller Individual Wholesaler Distributor",
            "when did a seller join the platform",
            "seller GSTIN GST registration and bank details",
        ],
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
        "use_when": [
            "how many customers bought a product or placed an order",
            "which customers are from Maharashtra Gujarat Karnataka Tamil Nadu or other states",
            "which customers live in Mumbai Delhi Bengaluru Hyderabad Chennai Kolkata Pune Ahmedabad",
            "show top 10 customers by total spending or number of orders",
            "how many male female or other gender customers are there",
            "which customers have premium membership",
            "what is the age or date of birth distribution of customers",
            "how many new customers registered in a given month or year",
            "find customer profile by email phone pincode or location",
            "customer segmentation demographic breakdown by city state gender",
        ],
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
        "use_when": [
            "which products are low on stock or need to be restocked",
            "which products are out of stock at a warehouse",
            "how much inventory is available in Mumbai Delhi Bengaluru Hyderabad Chennai Kolkata Pune Ahmedabad warehouse",
            "which products have stock below the reorder level threshold",
            "when was stock last replenished or restocked at a warehouse",
            "show inventory health across all warehouses",
            "which products are currently in stock and available for sale",
            "how many units of a product are available at each warehouse",
            "reorder quantity needed for low stock products",
            "warehouse stock distribution by city location",
        ],
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
        "use_when": [
            "how many orders were placed delivered shipped cancelled returned or failed",
            "how many orders were cancelled in Maharashtra Gujarat Delhi Karnataka or other states",
            "show monthly or weekly order volume trend over time",
            "what is the cancellation rate or return rate across all orders",
            "which delivery partner Delhivery BlueDart Ekart DTDC XpressBees handled the most orders",
            "what is the average delivery time from order placed to delivered",
            "which orders used a coupon code SAVE10 FLAT50 DIWALI30 NEWUSER",
            "how many orders used Standard Express Same Day or Scheduled shipping",
            "how many gift orders were placed by customers",
            "order count breakdown by city state pincode shipping address region",
        ],
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
        "use_when": [
            "what is the total revenue or sales amount for a product seller or category",
            "show monthly revenue trend or total sales amount over time in 2023 2024",
            "which products were bought or sold the most by quantity",
            "which seller has the most returned items — join sellers with order_items on is_returned",
            "how much GST tax was collected across all orders — 5% 12% 18% 28% slab breakdown",
            "what is the average order value subtotal per order",
            "how many items were returned by customers across all orders",
            "revenue breakdown by product category Electronics Fashion Grocery Sports Beauty",
            "how much total discount was given on all items sold",
            "seller earnings or revenue contribution per seller",
        ],
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
        "use_when": [
            "how many customers paid using UPI — UPI payment method count",
            "how many orders were paid by Credit Card Debit Card Net Banking COD or EMI",
            "which customers used Paytm PhonePe Google Pay Amazon Pay Mobikwik FreeCharge wallet to pay",
            "which Paytm wallet users placed orders — filter by wallet_name = Paytm",
            "what is the average EMI tenure in months for orders above 10000 rupees",
            "how many orders used EMI and what was the tenure 3 6 9 12 18 24 months",
            "show total revenue collected broken down by payment method",
            "how many payments were completed refunded or failed",
            "what is the grand total revenue collected across all successful payments",
            "which orders had split payments — two payment records for one order",
        ],
        "relates_to": ["orders", "customers"],
    },
}
