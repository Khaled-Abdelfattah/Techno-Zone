# Product Service — Techno Zone

Manages the product catalog and categories.

**Port:** `3002`  
**Base URL:** `/api/products`

## Endpoints

| Method | Path                        | Auth   | Description                        |
|--------|-----------------------------|--------|------------------------------------|
| GET    | /                           | —      | List products (filter + paginate)  |
| GET    | /<id>                       | —      | Get single product                 |
| POST   | /                           | Admin  | Create product                     |
| PATCH  | /<id>                       | Admin  | Update product fields              |
| DELETE | /<id>                       | Admin  | Delete product                     |
| PATCH  | /<id>/stock                 | Internal | Adjust stock (called by Order Svc) |

## Query Parameters (GET /)

| Param      | Example           | Description               |
|------------|-------------------|---------------------------|
| category   | Laptops           | Filter by category name   |
| min_price  | 100               | Minimum price filter      |
| max_price  | 500               | Maximum price filter      |
| sort_by    | price_asc         | price_asc / price_desc / rating / newest |
| search     | Samsung           | Name keyword search       |
| page       | 1                 | Pagination page           |
| per_page   | 20                | Results per page (max 100)|

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py       # Dev server on :3002
```

## Docker

```bash
docker build -t product-service .
docker run -p 3002:3002 --env-file .env product-service
```
