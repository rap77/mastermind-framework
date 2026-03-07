---
source_id: "FUENTE-614"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Python Testing with pytest: Effective Testing for Professional Developers"
author: "Brian Okken"
expert_id: "EXP-614"
type: "book"
language: "en"
year: 2017
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Python Testing with pytest"
status: "active"
---

# Python Testing with pytest

**Brian Okken**

## 1. Principios Fundamentales

> **P1 - Tests son código de primera clase**: Los tests no son ciudadanos de segunda clase. Deben tener la misma calidad que el código de producción. Si no, son un liability, no un asset.

> **P2 - La estructura del test comunica intención**: Un buen test lee como documentación ejecutable. AAA (Arrange-Act-Assert) no es un formato, es comunicación. Cualquiera debería entender qué se está testeando y por qué.

> **P3 - Los tests deben ser independientes**: Un test no debe depender de otro. Cada test debería poder correr en cualquier orden, solo, o en paralelo. Si comparten estado, son frágiles y poco confiables.

> **P4 - Fixture sobre setup/teardown**: Las funciones setup/teardown tradicionales crean código oculto y difícil de seguir. Las fixtures de pytest son explícitas, declarativas, y fácilmente componibles.

> **P5 - Un test debería fallar por una sola razón**: Si un test falla por múltiples razones, es demasiado grande o está testeando múltiples cosas. Un test = una assertion es el ideal. Varios asserts relacionados = acceptable. Muchos asserts no relacionados = refactorizar.

## 2. Frameworks y Metodologías

### The AAA Pattern (Arrange-Act-Assert)

```python
def test_calculate_total():
    # Arrange (Setup): Prepara el contexto
    cart = ShoppingCart()
    cart.add_item(Item("Widget", price=10.00), quantity=2)

    # Act (Exercise): Ejecuta el sistema bajo test
    total = cart.calculate_total()

    # Assert (Verify): Verifica el resultado esperado
    assert total == 20.00
```

**Por qué funciona**:
- Separa claramente qué, cómo, y qué se espera
- Hace el test fácil de leer y debuggear
- Fallo en assert = problema en act o arrange

### pytest Fixture System

**Fixture básica**:
```python
import pytest

@pytest.fixture
def empty_cart():
    """Crea un cart vacío para cada test."""
    return ShoppingCart()

def test_add_item(empty_cart):
    empty_cart.add_item(Item("Widget", 10.00))
    assert len(empty_cart.items) == 1
```

**Fixture con setup/teardown**:
```python
@pytest.fixture
def database():
    """Setup database, cleanup after test."""
    db = Database(":memory:")
    db.create_tables()
    yield db  # ← Test ejecuta aquí
    db.cleanup()  # ← Teardown
```

**Fixture parametrizada**:
```python
@pytest.fixture(params=[
    ("user@example.com", True),
    ("invalid-email", False),
    ("", False)
])
def email_validation(request):
    return request.param

def test_email_validation(email_validation):
    email, should_be_valid = email_validation
    assert is_valid_email(email) == should_be_valid
```

### Conftest.py: Shared Fixtures

```python
# conftest.py (autodiscovered by pytest)
@pytest.fixture(scope="session")
def api_client():
    """Un API client compartido por todos los tests."""
    return APIClient(base_url="http://test.example.com")

@pytest.fixture(scope="function")
def clean_db(api_client):
    """Limpia la DB antes de cada test."""
    api_client.db.truncate_all()
    yield
    api_client.db.truncate_all()  # Cleanup
```

### Test Discovery Rules

```
test_*.py
*_test.py
tests/
  ├── test_module.py
  └── package/
      └── test_module.py
```

**pytest automáticamente descubre**:
- Archivos con prefijo `test_`
- Funciones con prefijo `test_`
- Clases con prefijo `Test`
- Métodos con prefijo `test_`

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("PyTeSt", "PYTEST")
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected
```

**Ventaja sobre loops**: Un test por combinación, no uno que falla en la primera iteración.

### Markers and Categories

```python
# Definir custom marker (pytest.ini)
# markers =
#     slow: marks tests as slow (deselect with '-m "not slow"')
#     integration: marks tests as integration tests
#     unit: marks tests as unit tests

@pytest.mark.slow
def test_slow_operation():
    time.sleep(10)

@pytest.mark.integration
def test_database_integration():
    # Test contra DB real
    pass

# Run solo unit tests: pytest -m unit
# Skip slow: pytest -m "not slow"
```

### Test Coverage

```bash
# Instalar pytest-cov
pip install pytest-cov

# Run con coverage
pytest --cov=src --cov-report=html

# HTML report en htmlcov/index.html
```

**Coverage targets**:
- 80%: Minimum acceptable
- 90%: Good
- 95%+: Excellent (pero no obsesionarse)

## 3. Modelos Mentales

### Modelo de "Test Pyramid"

```
        /\
       /  \  E2E tests (10%)
      /────\
     /      \ Integration tests (30%)
    /────────\
   /          \ Unit tests (60%)
  /────────────\
```

**Por qué esta distribución**:
- Unit tests: Rápidos, baratos, foco en lógica
- Integration tests: Más lentos, prueban integraciones
- E2E tests: Más lentos, prueban flujos completos

**Anti-patrón**: Pirámide invertida (demasiados E2E)

### Modelo de "Testing What to Test"

**SUT**: System Under Test (lo que testeas)
**DOC**: Depended-On Component (dependencias externas)

**Regla**: Testea SUT, mockea DOC.

```python
# SUT = OrderCalculator
# DOC = PaymentGateway (external service)

def test_order_total():
    calculator = OrderCalculator()  # SUT real
    payment = MockPaymentGateway()  # DOC mockeado
    order = Order(items=[...])

    total = calculator.calculate(order, payment)
    assert total == expected
```

### Modelo de "Test Isolation"

Cada test debería ser:
1. **Independiente**: No depende de otros tests
2. **Determinístico**: Siempre mismo resultado con mismo input
3. **Rápido**: < 100ms idealmente
4. **Claro**: Se entiende qué se está testeando

**Violación de aislamiento**:
```python
# ❌ MAL: Test depende del orden
test_state = {}
def test_set_value():
    test_state['x'] = 1

def test_get_value():
    assert test_state['x'] == 1  # Falla si test_set_value no corre primero
```

### Modelo de "Red-Green-Refactor" (TDD)

1. **Red**: Escribes un test que falla
2. **Green**: Escribes el código mínimo para pasar
3. **Refactor**: Mejoras el código, tests siguen pasando

**Ciclo continua**: Cada feature comienza con test.

## 4. Criterios de Decisión

### When to Mock

| ✅ Mock cuando | ❌ No mockees cuando |
|----------------|---------------------|
| DOC es lento (DB, API, file system) | DOC es rápido (in-memory structures) |
| DOC es no-determinista (random, time) | DOC es determinista |
- DOC tiene efectos secundarios | DOC es pure function |
| DOC no está bajo tu control | DOC es parte de SUT |

### Unit vs Integration Tests

| Unit Test | Integration Test |
|------------|------------------|
| Prueba una función/clase aislada | Prueba múltiples componentes juntos |
| Mocks dependencies | Usa dependencies reales o test doubles parciales |
| Rápido (ms) | Más lento (seconds) |
| Aísla failures | Fallos pueden venir de múltiples lugares |

### Assertion Strategies

```python
# ❌ BAD: Assertion menos específica
assert result  # Cualquier truthy value pasa

# ❌ BAD: Demasiado específico, frágil
assert result == {
    "id": 123,
    "name": "Widget",
    "price": 10.00,
    "description": "A widget"
}  # Falla si agrega campo

# ✅ GOOD: Específico pero flexible
assert result["id"] == 123
assert result["name"] == "Widget"
assert result["price"] == 10.00
# Ignora campos no relevantes para el test
```

### Test Data: Fixtures vs Factories

```python
# Fixture: Data hardcoded
@pytest.fixture
def user():
    return User(id=1, name="Alice", email="alice@example.com")

# Factory: Data generativo
def make_user(**kwargs):
    defaults = {"id": 1, "name": "Alice", "email": "alice@example.com"}
    return User(**{**defaults, **kwargs})

def test_user_update():
    user = make_user(name="Bob")  # Override defaults
    assert user.name == "Bob"
```

**Cuándo usar**:
- Fixture: Data específico para test
- Factory: Data flexible, variaciones

### Test Organization

```
tests/
├── unit/
│   ├── test_services.py
│   ├── test_models.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
└── e2e/
    └── test_user_flows.py
```

**Alternativa**: Por módulo
```
tests/
├── test_users/
│   ├── unit/
│   └── integration/
└── test_orders/
    ├── unit/
    └── integration/
```

## 5. Anti-patrones

### Anti-patrón: "Testing Implementation Details"

**Problema**: Testea que el código hace X de una forma específica.

```python
# ❌ MAL: Testea que llama a un método específico
def test_calculate():
    calculator = Calculator()
    calculator.add(5, 3)  # Implementation detail
    assert calculator._result == 8  # Private field
```

**Solución**:
```python
# ✅ BIEN: Testea behavior, no implementación
def test_calculate():
    result = calculate(5, 3)  # Public interface
    assert result == 8
```

### Anti-patrón: "Greedy Test"

**Problema**: Un test que prueba demasiadas cosas.

```python
# ❌ MAL: 10 asserts, test podría fallar por 10 razones
def test_user_workflow():
    user = create_user()
    assert user.email is not None
    assert user.name is not None
    assert user.created_at is not None
    # ... 7 más asserts
```

**Solución**:
```python
# ✅ BIEN: Un test por concern
def test_user_has_required_fields():
    user = create_user()
    assert user.email is not None

def test_user_name_is_not_empty():
    user = create_user()
    assert user.name != ""
```

### Anti-patrón: "Flaky Test"

**Problema**: Test que falla intermitentemente.

```python
# ❌ MAL: Depende de tiempo real
def test_recent_posts():
    posts = get_recent_posts()
    assert posts[0].date > datetime.now() - timedelta(days=7)
    # Falla si corre exactamente a las 00:00 del día 7
```

**Solución**:
```python
# ✅ BIEN: Mockea el tiempo
def test_recent_posts(freezegun):
    frozen = freezegun.freeze_time("2024-01-01")
    frozen.start()
    posts = get_recent_posts()
    assert len(posts) == expected
```

### Anti-patrón: "Shared Test State"

**Problema**: Tests comparten estado global.

```python
# ❌ MAL
cache = {}
def test_set_cache():
    cache['x'] = 1
def test_get_cache():
    assert cache['x'] == 1  # Falla si test_set_cache no corre
```

**Solución**:
```python
# ✅ BIEN: Cada test crea su contexto
@pytest.fixture
def cache():
    return {}
def test_set_cache(cache):
    cache['x'] = 1
    assert cache['x'] == 1
```

### Anti-patrón: "No Tests After Exception"

**Problema**: Código después de una excepción no se ejecuta.

```python
# ❌ MAL
def test_with_exception():
    result = function_that_raises()
    assert result == 5  # Nunca se ejecuta
    assert other_thing  # Nunca se ejecuta
```

**Solución**:
```python
# ✅ BIEN: Separar tests
def test_function_raises():
    with pytest.raises(ValueError):
        function_that_raises()

def test_function_when_valid():
    result = function_that_works()
    assert result == expected
```

### Anti-patrón: "Magic Numbers in Tests"

**Problema**: Números sin contexto.

```python
# ❌ MAL
assert len(result) == 7
assert user.age == 18
```

**Solución**:
```python
# ✅ BIEN: Constantes con nombre
DAYS_IN_WEEK = 7
ADULT_AGE = 18
assert len(result) == DAYS_IN_WEEK
assert user.age == ADULT_AGE
```

### Anti-patrón: "Testing the Mock"

**Problema**: Test que solo verifica que se llamó el mock.

```python
# ❌ MAL
def test_with_mock():
    mock_db = Mock()
    save_user(mock_db, user)
    mock_db.save.assert_called_once()  # ¿Y qué?
```

**Solución**:
```python
# ✅ BIEN: Test behavior, no mock
def test_save_user():
    db = InMemoryDB()  # Test double real
    save_user(db, user)
    assert db.get(user.id) == user  # Verifica estado real
```

### Anti-patrón: "Ignoring Test Failures"

**Problema**: Tests que fallan se ignoran o se comentan.

**Solución**:
- Un test que falla es deuda técnica
- Arreglarlo o marcarlo como `@pytest.mark.xfail` con razón documentada
- Nunca comments tests, el código muerto no ayuda
