# Category Service — Techno Zone

Manages product categories with live product counts.

**Port:** `3003`  
**Base URL:** `/api/categories`

## Endpoints

| Method | Path          | Auth  | Description                    |
|--------|---------------|-------|--------------------------------|
| GET    | /             | —     | List all categories + counts   |
| GET    | /<id>         | —     | Single category + count        |
| POST   | /             | Admin | Create category                |
| PATCH  | /<id>         | Admin | Update name / icon             |
| DELETE | /<id>         | Admin | Delete category                |

## Response Example (GET /)

```json
{
  "success": true,
  "data": [
    { "id": 1, "name": "Laptops", "icon": "laptop", "product_count": 12 },
    { "id": 2, "name": "Phones",  "icon": "phone",  "product_count": 8 }
  ]
}
```

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py     # Dev server on :3003
```

## Docker

```bash
docker build -t category-service .
docker run -p 3003:3003 --env-file .env category-service
```

## Note on product counts

The service counts products from a local `products` mirror table.
For full independence, replace the DB count with an HTTP call to
Product Service:  `GET /api/products?category=<name>&per_page=1`
and use the `total` field from the response.
