# Genzzone Backend API

Django REST Framework backend API for the Genzzone e-commerce platform.

## Features

- Product management
- Order processing
- Shopping cart functionality
- Integration with Steadfast shipping API
- RESTful API endpoints
- CORS enabled for frontend integration

## Tech Stack

- **Django 6.0** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Production database (via Railway)
- **Gunicorn** - WSGI server for production
- **Pillow** - Image processing
- **psycopg2** - PostgreSQL adapter

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL (for production) or SQLite (for development)

### Installation

1. Clone the repository:
```bash
git clone <your-backend-repo-url>
cd genzzone-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (copy from `.env.example` if available):
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000
STEADFAST_API_KEY=your-api-key
STEADFAST_SECRET_KEY=your-secret-key
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `/api/products/` - List and create products
- `/api/products/{id}/` - Product details
- `/api/best-selling/` - Best selling products
- `/api/notifications/active/` - Active notifications
- `/api/cart/` - Shopping cart operations
- `/api/cart/add/` - Add item to cart
- `/api/cart/checkout/` - Checkout cart
- `/api/orders/create/` - Create order

## Deployment to Railway

1. Connect your GitHub repository to Railway
2. Add a PostgreSQL database service
3. Set the following environment variables:
   - `SECRET_KEY` - Django secret key
   - `DATABASE_URL` - Automatically provided by Railway
   - `ALLOWED_HOSTS` - Your Railway domain
   - `CORS_ALLOWED_ORIGINS` - Your Vercel frontend URL
   - `STEADFAST_API_KEY` - Your Steadfast API key
   - `STEADFAST_SECRET_KEY` - Your Steadfast secret key
   - `DEBUG` - Set to `False` for production

4. Railway will automatically:
   - Install dependencies from `requirements.txt`
   - Run migrations
   - Start the server using the `Procfile`

## Project Structure

```
genzzone-backend/
├── backend/                 # Django project settings
│   ├── settings.py          # Production settings
│   ├── settings_local.py    # Local development settings (SQLite, no R2)
│   ├── urls.py              # URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── products/         # Products app
├── orders/           # Orders app
├── manage.py         # Django management script
├── requirements.txt  # Python dependencies
└── Procfile          # Railway deployment config
```

## Local Development

The project ships with a dedicated `backend/settings_local.py` for local development. It uses **SQLite** and **local file storage** — no environment variables or external services are required.

### Activate local settings

**Option A — per-command flag (recommended):**
```bash
python manage.py runserver --settings=backend.settings_local
python manage.py migrate --settings=backend.settings_local
python manage.py createsuperuser --settings=backend.settings_local
```

**Option B — export once per shell session:**
```bash
export DJANGO_SETTINGS_MODULE=backend.settings_local
python manage.py runserver
```

### What the local settings change vs production

| Setting | Production (`settings.py`) | Local (`settings_local.py`) |
|---|---|---|
| `DATABASE` | PostgreSQL via `DATABASE_URL` | SQLite (`db.sqlite3`) |
| `DEBUG` | `False` | `True` |
| File storage | Cloudflare R2 (`S3Boto3Storage`) | Local filesystem |
| `MEDIA_URL` | `https://media.genzzone.com/` | `/media/` |
| `CSRF_COOKIE_DOMAIN` | `.genzzone.com` | `None` |
| `CSRF_COOKIE_SAMESITE` | `None` | `Lax` |
| `CSRF_COOKIE_SECURE` | `True` | `False` |
| `SESSION_COOKIE_DOMAIN` | `.genzzone.com` | `None` |
| Required env vars | Several (SECRET_KEY, DATABASE_URL, R2_*, …) | None |

### Quick start (first time)

```bash
python manage.py migrate --settings=backend.settings_local
python manage.py createsuperuser --settings=backend.settings_local
python manage.py runserver --settings=backend.settings_local
```

The API will be available at `http://localhost:8000` and the admin panel at `http://localhost:8000/admin/`.

> **Note:** `settings_local.py` is safe to commit — it contains no secrets and is never loaded in production. Production deployments on Railway always use `backend.settings` (the default in `manage.py` and `wsgi.py`).

---

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Test Products

```bash
python manage.py create_test_products
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode | Yes |
| `ALLOWED_HOSTS` | Allowed host domains | Yes |
| `DATABASE_URL` | Database connection URL | Yes (production) |
| `CORS_ALLOWED_ORIGINS` | Frontend origins | Recommended |
| `STEADFAST_API_KEY` | Steadfast API key | Yes |
| `STEADFAST_SECRET_KEY` | Steadfast secret key | Yes |

## License

[Your License Here]

