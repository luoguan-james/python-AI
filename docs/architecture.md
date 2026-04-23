# Project Architecture

## Overview
This document describes the high-level architecture of the project, including module responsibilities, data flow, and interface contracts.

## System Context
The system is composed of three main layers:
- **API Layer**: Handles HTTP requests, authentication, and input validation.
- **Service Layer**: Contains business logic and orchestrates data operations.
- **Data Layer**: Manages persistence, caching, and external integrations.

## Module Responsibilities

### 1. API Layer (`src/api/`)
- Exposes RESTful endpoints under `/api/v1/`.
- Uses middleware for logging, rate limiting, and JWT validation.
- Controllers are thin; they delegate to services.

### 2. Service Layer (`src/services/`)
- Implements core business logic.
- Each service is stateless and depends on repositories via dependency injection.
- Services throw domain-specific exceptions.

### 3. Data Layer (`src/repositories/`)
- Abstracts database access (PostgreSQL via SQLAlchemy).
- Provides CRUD operations and custom queries.
- Returns domain models or DTOs.

## Data Flow
```
Client → API Controller → Service → Repository → Database
         ← JSON Response ← DTO/Model ←
```

## Key Design Decisions
- **Separation of concerns**: Each layer has a single responsibility.
- **Dependency injection**: Services receive repositories through constructors, enabling testability.
- **DTOs**: Data Transfer Objects decouple internal models from API responses.
- **Error handling**: Centralized error middleware maps exceptions to HTTP status codes.

## Interface Contracts
See `docs/interfaces.md` for detailed API specifications.
