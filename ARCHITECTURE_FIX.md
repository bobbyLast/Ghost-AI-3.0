# Ghost AI 3.0 Architecture Fix Plan

## Current Problem: Circular Imports

The system has circular dependencies that prevent proper module loading:

```
system/auto_cleanup.py → core/ai_brain.py → core/ticket_generator.py → sports/mlb/mlb_props.py → core/data/data_fetcher.py → core/prop_processor.py → system/logging_config.py → system/auto_cleanup.py
```

## Solution: Restructure Architecture

### 1. Create Independent Data Layer
- Move `DataFetcher` to a separate `data/` module
- Remove dependencies on core modules from data layer
- Make data fetching completely independent

### 2. Separate Sports Modules
- Keep sports modules (`sports/mlb/`, `sports/wnba/`) independent
- Remove imports from core modules
- Use dependency injection for shared utilities

### 3. Create Service Layer
- Move business logic to `services/` module
- Separate concerns: data, business logic, system management
- Use interfaces/abstract classes for loose coupling

### 4. Fix Core Module Dependencies
- Remove circular imports in `core/` modules
- Use lazy imports where necessary
- Create proper abstraction layers

## Implementation Steps

### Phase 1: Data Layer Independence
1. Create `data/` module with independent data fetching
2. Move `DataFetcher` out of core
3. Update sports modules to use new data layer

### Phase 2: Service Layer Creation
1. Create `services/` module for business logic
2. Move ticket generation logic to services
3. Create proper interfaces

### Phase 3: Core Module Cleanup
1. Remove circular imports from core modules
2. Use dependency injection
3. Implement proper abstraction

### Phase 4: System Module Fix
1. Remove dependencies on core from system modules
2. Use event-driven architecture
3. Implement proper separation of concerns

## Benefits
- ✅ No circular imports
- ✅ Modular architecture
- ✅ Easy testing
- ✅ Independent deployment
- ✅ Clear separation of concerns

## Immediate Fix (Quick Solution)
For immediate functionality, we can:
1. Use lazy imports in critical paths
2. Create standalone scripts for data fetching
3. Implement proper error handling for import failures 