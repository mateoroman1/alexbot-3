## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_storage.py          # DataStorage class tests
├── test_game_mechanics.py   # Core game mechanics tests
├── test_managers.py         # Game manager classes tests
├── test_utilities.py        # Utility functions tests
└── README.md               # This file
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements.txt
```

### Basic Test Execution

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_storage.py
```

Run specific test class:
```bash
pytest tests/test_storage.py::TestDataStorage
```

Run specific test method:
```bash
pytest tests/test_storage.py::TestDataStorage::test_increment_user_stat
```

### Test Categories

Run only unit tests:
```bash
pytest -m unit
```

Run tests excluding slow tests:
```bash
pytest -m "not slow"
```

## Test Coverage

The test suite covers:

### Data Storage Layer (`test_storage.py`)
- ✅ DataStorage initialization and configuration
- ✅ CRUD operations for all stat types (character, boss, tool, user, server)
- ✅ Increment helper methods
- ✅ Data persistence (save/load cycle)
- ✅ Error handling for missing files
- ✅ Case folding for character names

### Game Mechanics (`test_game_mechanics.py`)
- ✅ Damage calculation with various multipliers
- ✅ Character-specific tool bonuses
- ✅ Group bonus calculations
- ✅ Evolution system mechanics
- ✅ Evolution recipe validation
- ✅ Path validation utilities
- ✅ Fuzzy string matching

### Manager Classes (`test_managers.py`)
- ✅ StatsManager statistical calculations
- ✅ RaidManager initialization and state management
- ✅ PVPManager battle logic
- ✅ Winner determination algorithms
- ✅ Campaign progression tracking

### Utility Functions (`test_utilities.py`)
- ✅ File operations and validation
- ✅ Image extension detection
- ✅ Random file selection
- ✅ Character and tool rolling mechanics
- ✅ Boss selection logic
- ✅ String matching and fuzzy search

## Test Fixtures

The test suite includes several fixtures in `conftest.py`:

- `temp_data_dir`: Temporary directory for test data files
- `mock_storage`: DataStorage instance with temporary files
- `populated_storage`: Storage instance with sample data
- `sample_*_stats`: Sample data for different stat types
- `mock_discord_*`: Mock Discord objects for testing
- `temp_assets_dir`: Temporary assets directory

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Test Structure
```python
def test_feature_behavior(self, fixture_name):
    """Test description of what this test verifies."""
    # Arrange
    setup_data = fixture_name
    
    # Act
    result = function_under_test(setup_data)
    
    # Assert
    assert result == expected_value
```

### Using Fixtures
```python
def test_with_populated_data(self, populated_storage):
    """Test using pre-populated storage."""
    stats = populated_storage.get_character_stats("alex")
    assert stats.count == 5
```

### Mocking External Dependencies
```python
@patch('module.external_function')
def test_with_mock(self, mock_external):
    """Test with mocked external dependency."""
    mock_external.return_value = "mocked_result"
    result = function_that_calls_external()
    assert result == "expected_result"
```

## Continuous Integration

The test suite is designed to run in CI environments:

- No external dependencies (Discord API, file system)
- Deterministic test data
- Fast execution (< 30 seconds for full suite)
- Clear error messages and stack traces

## Debugging Tests

### Verbose Output
```bash
pytest -v -s
```

### Stop on First Failure
```bash
pytest -x
```

### Show Local Variables on Failure
```bash
pytest -l
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

## Common Issues

### Import Errors
If you get import errors, ensure you're running tests from the project root:
```bash
cd /path/to/alexbot-3
pytest
```

### File Permission Errors
Tests use temporary directories that should be automatically cleaned up. If you encounter permission errors, ensure the test process has write access to the system temp directory.

### Mock Issues
If mocks aren't working as expected, check that you're patching the correct import path. Use the path where the function is imported, not where it's defined.

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Add tests for edge cases and error conditions
4. Update this README if adding new test categories
5. Consider performance impact of new tests

## Test Data

Test data is kept minimal and focused. Each test should be self-contained and not depend on external state. Use fixtures for shared test data rather than global variables.
