# Refactor Architecture Design - SOLID Principles Implementation

## 🎯 เป้าหมายการ Refactor
- ใช้หลักการ OOP, Clean Code และ SOLID principles
- แยก Business Logic จาก Presentation Layer
- ใช้ Dependency Injection และ Interface Segregation
- สร้าง Service Layer และ Repository Pattern

## 📊 Architecture ใหม่

### 1. Layer Structure (Clean Architecture)
```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │   Controllers   │ │   Middleware    ││
│  │   (Routes)      │ │   (Auth, etc)   ││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│            Application Layer            │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │   Services      │ │   DTOs/VOs      ││
│  │   (Business)    │ │   (Data Transfer)││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│             Domain Layer                │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │   Entities      │ │   Interfaces    ││
│  │   (Models)      │ │   (Contracts)   ││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          Infrastructure Layer           │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │  Repositories   │ │   External APIs ││
│  │  (Data Access)  │ │   (Google, etc) ││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
```

### 2. SOLID Principles Implementation

#### Single Responsibility Principle (SRP)
- **Controllers**: จัดการ HTTP requests/responses เท่านั้น
- **Services**: Business logic ของแต่ละ domain
- **Repositories**: Data access เท่านั้น
- **DTOs**: Data transfer objects

#### Open/Closed Principle (OCP)
- ใช้ Interfaces สำหรับ extensibility
- Strategy Pattern สำหรับ different implementations

#### Liskov Substitution Principle (LSP)
- All implementations ของ interface ต้องใช้แทนกันได้

#### Interface Segregation Principle (ISP)
- แยก interfaces ตาม specific needs
- ไม่บังคับให้ implement methods ที่ไม่ใช้

#### Dependency Inversion Principle (DIP)
- Depend on abstractions, not concretions
- Dependency Injection container

## 🏗️ โครงสร้างโฟลเดอร์ใหม่

```
app/
├── __init__.py                 # App factory
├── config/                     # Configuration
│   ├── __init__.py
│   ├── settings.py
│   └── database.py
├── domain/                     # Domain Layer
│   ├── __init__.py
│   ├── entities/               # Domain Models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── lesson.py
│   │   ├── note.py
│   │   └── task.py
│   ├── interfaces/             # Contracts/Interfaces
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── user_repository.py
│   │   │   ├── lesson_repository.py
│   │   │   └── note_repository.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── user_service.py
│   │       ├── lesson_service.py
│   │       └── auth_service.py
│   └── value_objects/          # Value Objects
│       ├── __init__.py
│       ├── email.py
│       └── password.py
├── application/                # Application Layer
│   ├── __init__.py
│   ├── services/               # Application Services
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── lesson_service.py
│   │   ├── auth_service.py
│   │   └── integration_service.py
│   ├── dto/                    # Data Transfer Objects
│   │   ├── __init__.py
│   │   ├── user_dto.py
│   │   ├── lesson_dto.py
│   │   └── response_dto.py
│   └── use_cases/              # Use Cases
│       ├── __init__.py
│       ├── user_use_cases.py
│       └── lesson_use_cases.py
├── infrastructure/             # Infrastructure Layer
│   ├── __init__.py
│   ├── database/               # Database
│   │   ├── __init__.py
│   │   ├── models/             # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── user_model.py
│   │   │   ├── lesson_model.py
│   │   │   └── note_model.py
│   │   └── repositories/       # Repository Implementations
│   │       ├── __init__.py
│   │       ├── user_repository.py
│   │       ├── lesson_repository.py
│   │       └── note_repository.py
│   ├── external/               # External Services
│   │   ├── __init__.py
│   │   ├── google_classroom/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── adapter.py
│   │   └── ms_teams/
│   │       ├── __init__.py
│   │       └── client.py
│   └── di/                     # Dependency Injection
│       ├── __init__.py
│       └── container.py
├── presentation/               # Presentation Layer
│   ├── __init__.py
│   ├── controllers/            # Controllers
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   ├── lesson_controller.py
│   │   └── note_controller.py
│   ├── middleware/             # Middleware
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   └── error_handler.py
│   └── routes/                 # Route Definitions
│       ├── __init__.py
│       ├── auth_routes.py
│       ├── user_routes.py
│       ├── lesson_routes.py
│       └── note_routes.py
└── shared/                     # Shared Components
    ├── __init__.py
    ├── exceptions/             # Custom Exceptions
    │   ├── __init__.py
    │   ├── base_exception.py
    │   ├── validation_exception.py
    │   └── not_found_exception.py
    ├── utils/                  # Utilities
    │   ├── __init__.py
    │   ├── validators.py
    │   ├── formatters.py
    │   └── decorators.py
    └── constants/              # Constants
        ├── __init__.py
        ├── status_codes.py
        └── messages.py
```

## 🔧 Key Components

### 1. Domain Entities
- Pure business objects
- No dependencies on external frameworks
- Business rules and validation

### 2. Interfaces (Contracts)
- Define contracts for repositories and services
- Enable dependency inversion
- Support testing with mocks

### 3. Application Services
- Orchestrate use cases
- Coordinate between domain and infrastructure
- Transaction management

### 4. Repository Pattern
- Abstract data access
- Enable different data sources
- Support unit testing

### 5. Dependency Injection
- Centralized dependency management
- Easy testing and configuration
- Loose coupling

## 🚀 Implementation Plan

1. **Phase 1**: Create new folder structure
2. **Phase 2**: Define interfaces and contracts
3. **Phase 3**: Implement domain entities
4. **Phase 4**: Create repository implementations
5. **Phase 5**: Build application services
6. **Phase 6**: Refactor controllers
7. **Phase 7**: Update routes
8. **Phase 8**: Testing and validation

## 📋 Benefits

- **Maintainability**: Clear separation of concerns
- **Testability**: Easy to unit test with mocks
- **Scalability**: Easy to add new features
- **Flexibility**: Easy to change implementations
- **Code Quality**: Follows SOLID principles
- **Team Collaboration**: Clear structure for team work
