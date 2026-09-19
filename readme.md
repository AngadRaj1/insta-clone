# Instagram Clone API 📸

A production-grade, asynchronous RESTful API for a social media platform, built with Python and FastAPI. This project implements Domain-Driven Design (DDD) principles and features a fully relational PostgreSQL database handling complex user interactions like follows, timeline feeds, likes, and comments.

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python 3.12)
* **Database:** PostgreSQL (with `asyncpg` driver)
* **ORM:** SQLAlchemy 2.0 (Async)
* **Migrations:** Alembic
* **Authentication:** JSON Web Tokens (JWT) & bcrypt
* **Data Validation:** Pydantic
* **File Handling:** `python-multipart` for local image uploads
* **Containerization:** Docker & Docker Compose

## ✨ Key Features

* **JWT Authentication:** Secure user registration, login, and route protection.
* **Image Uploads:** Real file handling for post images, served statically via a local `uploads/` directory.
* **Social Graph:** Self-referential many-to-many relationships allowing users to follow and unfollow each other.
* **Personalized Timeline:** Advanced SQL subqueries to generate a feed of posts exclusively from the user and the people they follow.
* **Interactions:** Like/unlike toggles (composite primary keys) and chronological commenting.
* **Eager Loading:** Optimized database queries using `selectinload` to fetch posts with their associated authors in a single trip.

## 📁 Project Structure (Domain-Driven Design)

The codebase is organized by business domains rather than technical layers, making it scalable and easy to maintain.

```text
├── alembic/                # Database migration configurations
├── app/
│   ├── core/               # App-wide settings, database connection, security logic
│   ├── domains/
│   │   ├── users/          # Models, schemas, routes for Auth & Follows
│   │   ├── posts/          # Models, schemas, routes for Posts & Timelines
│   │   └── interactions/   # Models, schemas, routes for Likes & Comments
│   └── main.py             # FastAPI application entry point
├── uploads/                # Local directory for static image storage
├── docker-compose.yml      # Multi-container orchestration
├── Dockerfile              # API container blueprint
└── requirements.txt        # Python dependencies

```

## 🚀 Running Locally (Without Docker)

### 1. Prerequisites

* Python 3.12+
* PostgreSQL installed and running locally.
* A database created (e.g., `insta-db`).

### 2. Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt

```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL="postgresql+asyncpg://your_db_user:your_password@localhost:5432/insta-db"

```

### 4. Run Migrations

Generate the database tables using Alembic:

```bash
alembic upgrade head

```

### 5. Start the Server

```bash
uvicorn app.main:app --reload

```

The API documentation (Swagger UI) will be available at **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.

---

## 🐳 Running with Docker (Production Setup)

The Docker setup spins up an isolated, containerized PostgreSQL database and API server communicating over a private network.

### 1. Build and Launch

Run this command in the project root to start the containers in the background:

```bash
docker-compose up --build -d

```

### 2. Run Migrations Inside the Container

Because Docker uses a fresh database, you must run the migrations inside the API container to create the tables:

```bash
docker-compose exec api alembic upgrade head

```

### 3. Access the App

The API is now live at **http://localhost:8000/docs**.

*Note: The database credentials in the `docker-compose.yml` file (`insta_user` / `super_secure_password`) are used to initialize the internal Docker database and do not interfere with your local machine's Postgres installation.*

## 🔌 Core API Endpoints

**Auth & Users**

* `POST /users/register` - Create a new account
* `POST /users/login` - Authenticate and receive a JWT
* `GET /users/me` - Get current logged-in user profile
* `POST /users/{user_id}/follow` - Follow a user
* `DELETE /users/{user_id}/follow` - Unfollow a user

**Posts & Feeds**

* `POST /posts/` - Create a post (accepts `multipart/form-data` image upload)
* `GET /posts/` - Get global explore feed
* `GET /posts/feed` - Get personalized timeline (followed users only)

**Interactions**

* `POST /posts/{post_id}/like` - Toggle like/unlike on a post
* `POST /posts/{post_id}/comments` - Add a comment
* `GET /posts/{post_id}/comments` - Fetch comments for a post

---

*Built with FastAPI and SQLAlchemy.*