# Fitly - Fitness Application

A fitness application with microservices architecture using .NET, Python AI, and Docker.

## Services

- **Auth Services**: User authentication (C# .NET 9)
- **Body Analysis AI**: Body shape analysis (Python + YOLOv8)
- **User Services**: User management
- **Workout Services**: Workout management
- **Meal Services**: Meal management
- **Notification Services**: Notifications

## Prerequisites

- Docker & Docker Compose
- Git

## Quick Start

1. **Clone repository:**
```bash
git clone https://github.com/tiao051/Fitly.git
cd Fitly
```

2. **Setup environment:**
```bash
cp .env.example .env
# Edit .env if needed
```

3. **Start all services:**
```bash
docker-compose up --build -d
```

Note: First run will take longer as it downloads AI models.

4. **Access services:**
- Body Analysis AI: http://localhost:8000
- RabbitMQ Management: http://localhost:15672 (admin/admin)
- PostgreSQL: localhost:5432

## API Documentation

- Auth API Swagger: http://localhost:5000/swagger
- Body Analysis Swagger: http://localhost:8000/docs

## Environment Variables

Copy `.env.example` to `.env` and update values if needed.

## Database Migration

Auth service will auto-migrate database on startup.

## Troubleshooting

### Common Issues:
1. **Port conflicts**: Change ports in docker-compose.yml
2. **Database connection**: Check PostgreSQL is running
3. **RabbitMQ connection**: Check RabbitMQ is running
4. **Body Analysis AI slow start**: First run downloads YOLO model (~6MB)
5. **OpenCV errors**: Rebuild body_analysis_ai container if needed

### Build and start all services:
```bash
docker-compose up --build -d
```

### Rebuild specific service:
```bash
docker-compose up --build body_analysis_ai
```

### View logs:
```bash
docker-compose logs -f [service_name]
```

### Stop all services:
```bash
docker-compose down
```

## Development

### Auth Services (.NET)
```bash
cd auth_services/auth_services
dotnet run
```

### Body Analysis AI (Python)
```bash
cd body_analysis_ai_services/body_analysis_ai
pip install -r requirements.txt
python run.py
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Auth Service  │
│                 │───▶│                 │───▶│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                │                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Body Analysis AI │    │   User Service  │    │   PostgreSQL    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                │                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Workout Service │    │  Meal Service   │    │    RabbitMQ     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```