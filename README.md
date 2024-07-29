# 🛍️ FastAPI E-Commerce Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

A robust and scalable e-commerce backend built with FastAPI, featuring real-time notifications, background task processing, and containerized deployment.

## 🌟 Features

- 🔐 User authentication and authorization
- 🛒 Product management and categorization
- 📦 Order processing and tracking
- 🚚 Shipping integration
- 💳 Secure payment processing
- 🔔 Real-time notifications via WebSockets
- 🔄 Background task processing
- 🐳 Containerized with Docker for easy deployment

## 🛠️ Technologies Used

- FastAPI
- PostgreSQL
- Docker
- WebSockets
- Asyncio
- Alembic (for database migrations)

## 🚀 Getting Started

1. Clone the repository:
    git clone https://github.com/your-username/fast-ecommerce.git
    cd fast-ecommerce

2. Set up environment variables:
    Edit the `.env` file with your configuration.

3. Build and run the Docker containers:
    docker-compose up --build

4. Access the API documentation at:
    `http://localhost:8000/docs` / `http://localhost:8000/redoc/` / `http://localhost:8000/rapidoc`

## 📚 API Documentation

Our API provides comprehensive endpoints for managing all aspects of the e-commerce platform:

- 👤 User Management
- 🏷️ Product Catalog
- 🛒 Shopping Cart
- 📦 Order Processing
- 🚚 Shipping
- 💰 Payment Integration
- 🔔 Real-time Notifications

For detailed API documentation, please refer to the Swagger UI at `/docs` or ReDoc at `/redoc` when running the application.

## 🔧 Development

To run the application in development mode:

1. Install dependencies:
    pip install -r requirements.txt

2. Run the FastAPI server:
    uvicorn main:app --reload

3. For database migrations:
    alembic upgrade head

## 🧪 Testing

Run tests using pytest:
    pytest

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License .

## 📞 Contact

For any queries or support, please open an issue or contact [omar.desi.100@gmail.com].

---

Happy coding! 🚀✨
