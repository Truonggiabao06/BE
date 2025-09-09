# Jewelry Auction System

A comprehensive RESTful API for managing jewelry auctions, built with Flask and Clean Architecture principles.

## 🚀 Features

### Core Functionality
- **User Management**: Registration, authentication, role-based access control
- **Jewelry Management**: Item submission, appraisal workflow, status tracking
- **Auction System**: Session management, real-time bidding, automated settlement
- **Payment Processing**: Secure payment handling, fee calculation, payout management
- **Notification System**: Real-time notifications for important events
- **File Management**: Photo upload and storage for jewelry items

### Technical Features
- **Clean Architecture**: Domain-driven design with clear separation of concerns
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Fine-grained permissions (Guest, Member, Staff, Manager, Admin)
- **RESTful API**: Well-structured endpoints with comprehensive documentation
- **Database Migrations**: Alembic integration for schema management
- **Comprehensive Testing**: Unit tests for critical business logic
- **Docker Support**: Containerized deployment with Docker Compose
- **API Documentation**: Interactive Swagger/OpenAPI documentation

## 🏗️ Architecture

```
src/
├── domain/                 # Business logic and entities
│   ├── entities/          # Domain entities (User, JewelryItem, etc.)
│   ├── enums.py          # Business enums and constants
│   ├── business_rules.py  # Business rule validation
│   ├── constants.py      # Domain constants
│   └── exceptions.py     # Custom exceptions
├── infrastructure/        # External concerns
│   ├── models/           # SQLAlchemy database models
│   ├── repositories/     # Data access implementations
│   ├── services/         # Infrastructure services
│   └── databases/        # Database configuration
├── services/             # Application services (use cases)
├── api/                  # Web layer
│   ├── controllers/      # API endpoints
│   ├── middleware/       # Authentication, CORS, etc.
│   └── routes.py        # Route registration
└── config.py            # Application configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- SQL Server 2022+ (or SQLite for development)
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd jewelry-auction-system
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r src/requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database and other settings
```

5. **Initialize database**
```bash
# For development with SQLite
export DB_URL="sqlite:///jewelry_auction.db"

# For SQL Server
export DB_URL="mssql+pyodbc://sa:password@localhost:1433/jewelry_auction_dev?driver=ODBC+Driver+17+for+SQL+Server"
```

6. **Run the application**
```bash
python run.py
```

The API will be available at `http://localhost:5000`
- API Documentation: `http://localhost:5000/api/docs`
- Health Check: `http://localhost:5000/health`

### 🐳 Docker Deployment

```bash
# Start all services (SQL Server, Redis, App, Nginx)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## 📚 API Usage

### Authentication

**Register a new user:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "role": "MEMBER"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### Jewelry Management

**Submit a sell request:**
```bash
curl -X POST http://localhost:5000/api/v1/jewelry/sell-requests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Diamond Ring",
    "description": "Beautiful 2-carat diamond ring",
    "photos": ["photo1.jpg", "photo2.jpg"],
    "attributes": {"material": "gold", "weight": "5.2g"},
    "weight": 5.2
  }'
```

## 👥 User Roles

- **GUEST**: Can view public auction information
- **MEMBER**: Can sell items, place bids, make payments
- **STAFF**: Can manage appraisals, auction sessions
- **MANAGER**: Can approve items, manage staff actions
- **ADMIN**: Full system access, user management

## 🔄 Business Workflow

### Selling Process
1. **Submit Sell Request**: Member submits jewelry with photos and description
2. **Preliminary Appraisal**: Staff reviews and provides initial estimate
3. **Item Receipt**: Physical item received and verified
4. **Final Appraisal**: Detailed appraisal with final estimate
5. **Manager Approval**: Manager reviews and approves for auction
6. **Seller Acceptance**: Seller accepts terms and reserve price
7. **Auction Assignment**: Item assigned to upcoming auction session

### Auction Process
1. **Session Creation**: Staff creates auction session
2. **Item Assignment**: Approved items assigned to session
3. **User Enrollment**: Bidders enroll in session
4. **Live Auction**: Real-time bidding during session
5. **Settlement**: Winning bids processed, payments collected
6. **Fulfillment**: Items shipped, sellers paid

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## ⚙️ Configuration

Key environment variables:

```bash
# Application
APP_ENV=development|testing|production
DEBUG=true|false
SECRET_KEY=your-secret-key

# Database
DB_URL=mssql+pyodbc://sa:password@localhost:1433/jewelry_auction_dev?driver=ODBC+Driver+17+for+SQL+Server

# JWT
JWT_SECRET=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600  # seconds

# File Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛣️ Roadmap

- [ ] Real-time bidding with WebSockets
- [ ] Advanced search and filtering
- [ ] Mobile app API enhancements
- [ ] Integration with payment gateways
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Automated testing pipeline

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact: support@jewelryauction.com
