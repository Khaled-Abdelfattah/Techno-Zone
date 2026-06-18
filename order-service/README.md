# Order Service — Techno Zone

Handles checkout, order history, and order status management.  
Calls **Product Service** to resolve prices and **Coupon Service** to validate discounts.

**Port:** `3005`  
**Base URL:** `/api/orders`

## Endpoints

| Method | Path                  | Auth | Description                          |
|--------|-----------------------|------|--------------------------------------|
| POST   | /checkout             | JWT  | Place order from cart items          |
| GET    | /                     | JWT  | List current user's orders           |
| GET    | /<id>                 | JWT  | Single order with items              |
| PATCH  | /<id>/status          | JWT  | Update order status (admin)          |
| DELETE | /<id>                 | JWT  | Cancel a pending/confirmed order     |

## Checkout Request

```json
POST /api/orders/checkout
Authorization: Bearer <jwt>

{
  "items": [
    { "product_id": "P001", "qty": 2 },
    { "product_id": "P005", "qty": 1 }
  ],
  "coupon_code": "SAVE10"
}
```

If `items` is omitted, the service fetches the cart automatically from Cart Service.

## Checkout Response (201)

```json
{
  "success": true,
  "data": {
    "id": 42,
    "user_id": 7,
    "coupon_code": "SAVE10",
    "subtotal": 250.00,
    "discount": 25.00,
    "total": 225.00,
    "status": "pending",
    "items": [
      { "product_id": "P001", "name": "Laptop X", "qty": 2, "unit_price": 100.00, "subtotal": 200.00 }
    ]
  }
}
```

## Inter-Service Calls

| Call                              | When                        |
|-----------------------------------|-----------------------------|
| GET  Product Service `/api/products/{id}` | Resolve price per item  |
| POST Coupon Service `/api/coupon/validate` | Validate coupon code   |
| PATCH Product Service `/api/products/{id}/stock` | Decrement stock    |
| DELETE Cart Service `/api/cart/clear`   | Clear cart after order  |

## Setup

```bash
cp .env.example .env    # Set DATABASE_URL + service URLs
pip install -r requirements.txt
python app.py           # Dev server on :3005
```

## Docker

```bash
docker build -t order-service .
docker run -p 3005:3005 --env-file .env order-service
```
