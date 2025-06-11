# CSV Utility API

A lightweight RESTful API for splitting and converting CSV files. Built with Django REST Framework and powered by Supabase Storage.


---

## ✨ Features

- 🔐 JWT-based Authentication (via SimpleJWT)
- 📤 Upload CSV and split by:
  - **Line count**
  - **File size (MB)**
- 🔁 Convert CSV to JSON and receive a downloadable ZIP
- ☁️ Upload output to **Supabase Storage**
- 🔗 Secure, expiring download links
- 🧹 Scheduled Supabase cleanup endpoint
- 🧪 DRF Spectacular-powered auto docs (`/api/schema/swagger-ui/`)

---

## 🛠️ Technologies

- Python, Django, Django REST Framework
- Supabase Storage
- Cron job
- PostgreSQL/MySQL (flexible)
- DRF Spectacular (for OpenAPI)

---

## 📦 API Endpoints

Base URL: `https://file-splitter-api.onrender.com/`

---

### 🔐 Authentication

| Method | Endpoint              | Description       |
|--------|-----------------------|-------------------|
| POST   | `/users/register/`     | Register a user   |
| POST   | `/users/login/`        | Login and get JWT |
| GET    | `/users/user/`         | Get logged-in user (JWT required) |

---

### 📂 File Operations

**All endpoints are prefixed with `/files/`**

#### ✅ Upload & Split CSV

**POST** `/files/split-csv/`

```bash
multipart/form-data:
- file: CSV file
- lines_per_file (int) OR size_per_file (int)
````

Returns:

```json
{
  "download-url": "<Signed Supabase ZIP URL>"
}
```

#### 🔁 Convert CSV to JSON (zipped)

**POST** `/files/convert-csv/`

```bash
multipart/form-data:
- file: CSV file
```

Returns:

```json
{
  "download-url": "<Signed Supabase ZIP URL>"
}
```

#### ⬇️ Download File

**GET** `/files/<id>/download-file/`
Requires JWT token (authenticated users only)

#### 🧹 Cleanup Supabase Buckets

**GET** `/files/cleanup-files/`

* Cron-protected via `X-Cron-Token` header
* Requires a secret token from `.env`

Returns:

```json
{
  "success": "Files cleaned successfully"
}
```

---

## 🔐 Auth Flow (JWT)

1. **Register**: `POST /users/register/`
2. **Login**: `POST /users/login/`

   * Returns `access_token` and `refresh_token`
3. Use `Authorization: Bearer <access_token>` on protected routes

---

## ⚙️ Dev Setup

```bash
git clone https://github.com/carnage999-max/file-splitter-api
cd file-splitter-api

# Setup virtualenv
python -m venv venv
source venv/bin/activate 

# Install dependencies
pip install -r requirements.txt

## Using pipenv

### Activate virtual environment
pipenv shell

### Install requirements
pipenv install

# Setup environment variables
touch .env

# Run migrations
python manage.py migrate

# Run dev server
python manage.py runserver
```

---

## 📖 Interactive Docs

Once running, visit:

```
http://localhost:8000/api/schema/swagger-ui/
```

---

## 🧪 Sample Usage (Python + Requests)

```python
import requests

url = "https://file-splitter-api.onrender.com/files/split-csv/"
headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}
files = {
    "file": open("data.csv", "rb"),
}
data = {
    "lines_per_file": 1000
}
res = requests.post(url, headers=headers, files=files, data=data)
print(res.json())  # => { "download-url": "<supabase_link>" }
```

---

## 👤 Author

**Ezekiel Okebule**, Backend Engineer
🔗 [LinkedIn](https://linkedin.com/in/ezekiel-okebule)
🌐 [ezekiel-okebule.vercel.app](https://ezekiel-okebule.vercel.app)

---

## 📝 License

MIT
