# Fitly - Fitness Application

Ứng dụng fitness với microservices architecture sử dụng .NET, Python AI và Docker.

## Services

- **Auth Services**: Xác thực người dùng (C# .NET 9)
- **Body Analysis AI**: Phân tích hình dạng cơ thể (Python + YOLOv8)
- **User Services**: Quản lý người dùng
- **Workout Services**: Quản lý bài tập
- **Meal Services**: Quản lý chế độ ăn
- **Notification Services**: Thông báo

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
docker-compose up -d
```

Note: First run will take longer as it downloads AI models.

3. **Access services:**

- RabbitMQ Management: http://localhost:15672 (admin/admin)
- PostgreSQL: localhost:5432

## API Documentation

- Auth API Swagger: http://localhost:5000/swagger

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

### Rebuild specific service:
```bash
docker-compose up --build body_analysis_ai
```

### Logs:
```bash
docker-compose logs -f [service_name]
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