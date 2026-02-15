# Beancount Plugin Tax UK

A Python plugin for [Beancount](https://beancount.github.io/) that generates UK tax reports for capital gains, dividends and other investment income. Available as both a command-line tool for Excel report generation and a Fava extension for interactive viewing.

**ALWAYS follow these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Quick Validation Checklist

Before making any changes, **ALWAYS** run this validation sequence to ensure your environment is working:

1. **Test import**: `python -c "import beancount_plugin_tax_uk.calculate_tax; print('Import works')"`
2. **Format code**: `make format` (takes <1 second)
3. **Lint code**: `make lint` (takes <1 second)  
4. **Run tests**: `make test` (takes ~3 seconds, 15 tests should pass)
5. **Test CLI**: `python -m beancount_plugin_tax_uk.calculate_tax tests/data/trivial_sample.beancount /tmp/test.xlsx` 
6. **Verify output**: `ls -la /tmp/test.xlsx` (should show ~6KB Excel file)

**If any step fails, DO NOT proceed with changes until the issue is resolved.**

## Working Effectively

Bootstrap the development environment:
- `make deps-testing` -- Installs package with testing dependencies via pip. Takes ~30 seconds when network allows. NEVER CANCEL. **WARNING**: May fail with network timeouts in restricted environments - this is expected.
- `make format` -- Formats code using ruff formatter. Takes <1 second.
- `make lint` -- Runs ruff linter and formatter checks. Takes <1 second.
- `make test` -- Runs pytest test suite (15 tests). Takes ~3 seconds. NEVER CANCEL.
- `python -m build` -- Builds distributable package. **WARNING**: Often fails due to network timeouts in restricted environments.

Run the command-line tool:
- `python -m beancount_plugin_tax_uk.calculate_tax --help` -- Shows CLI help and options
- `python -m beancount_plugin_tax_uk.calculate_tax <ledger_file> <output.xlsx>` -- Generates Excel tax report
- `python -m beancount_plugin_tax_uk.calculate_tax <ledger_file> <output.xlsx> --verbose` -- Generates Excel report with verbose debug output

Run Fava with the plugin:
- `fava <beancount_file>` -- Starts Fava web interface on http://localhost:5000
- `cd tests && ./show_tests_in_fava.sh` -- Starts Fava with multiple test ledgers available via dropdown

## Validation

Always run the complete validation sequence after making changes:
- `make format` -- Format code (automatic fixes)
- `make lint` -- Verify linting passes after formatting
- `make test` -- Run full test suite (15 tests, takes ~3 seconds)

**CRITICAL**: DO NOT skip validation steps. The CI will fail if code is not properly formatted and linted.

**MANUAL VALIDATION**: After code changes, manually test the CLI tool:
```bash
python -m beancount_plugin_tax_uk.calculate_tax tests/data/trivial_sample.beancount /tmp/test_output.xlsx --verbose
ls -la /tmp/test_output.xlsx  # Verify Excel file was created
```

Test Fava integration by starting the server and verifying it loads:
```bash
fava tests/data/trivial_sample.beancount --port 5001
# Should output: "Starting Fava on http://127.0.0.1:5001"
```

## Build Process

**CRITICAL NETWORK LIMITATION**: Package building and dependency installation frequently fails in restricted environments due to PyPI connection timeouts. This is expected behavior.

**When `make deps-testing` fails with network timeouts**:
- If dependencies are already installed, continue with development (use `make lint`, `make test`, etc.)
- The package likely works if it was previously installed
- Test functionality before assuming the build is broken
- Use `python -c "import beancount_plugin_tax_uk.calculate_tax; print('Import works')"` to verify

**When `make build` fails**:
- Skip building distribution packages - not required for development
- All functionality can be tested without building distribution packages  
- Focus on testing core features via CLI and Fava integration

**Working with existing installations**:
If dependencies are already installed but `make deps-testing` fails due to network issues:
- Test import: `python -c "import beancount_plugin_tax_uk.calculate_tax; print('Import works')"`
- If import succeeds, proceed with: `make format` → `make lint` → `make test`
- Manual validation commands will work with existing installation

## Common Tasks

### Repository structure
```
.
├── Makefile              # Main build commands
├── README.md             # Project documentation
├── pyproject.toml        # Build configuration
├── setup.cfg             # Package metadata and dependencies
├── setup.py              # Setup script
├── tox.ini               # Testing environments (optional)
├── src/                  # Source code
│   └── beancount_plugin_tax_uk/
│       ├── __init__.py
│       ├── calculate_tax.py      # CLI entry point
│       ├── fava_extension.py     # Fava plugin
│       ├── tax_report.py         # Core tax calculation logic
│       ├── models.py             # Data models
│       ├── rate_converter.py     # Exchange rate handling
│       └── spreadsheet_writer.py # Excel output
└── tests/                # Test files and data
    ├── test_report.py         # Main test suite
    ├── show_tests_in_fava.sh  # Script to view test data in Fava
    ├── cgtcalc_parser.py      # Converts test data formats
    └── data/                  # Test Beancount files
```

### Dependencies
Core dependencies (from setup.cfg):
- `beancount` -- Core accounting engine
- `pandas` -- Data processing
- `click` -- CLI interface
- `xlsxwriter` -- Excel file generation
- `fava>=1.25.1` -- Web interface

Development dependencies:
- `pytest` -- Testing framework
- `pytest-cov` -- Coverage reporting
- `ruff>=0.3.0` -- Linting and formatting
- `openpyxl>=3.1.0` -- Excel file reading (for tests)

### Key Files
- `src/beancount_plugin_tax_uk/calculate_tax.py` -- Main CLI entry point with tax calculation logic
- `src/beancount_plugin_tax_uk/tax_report.py` -- Core tax report generation
- `src/beancount_plugin_tax_uk/fava_extension.py` -- Fava web interface extension
- `tests/data/trivial_sample.beancount` -- Simple test case for manual validation
- `tests/show_tests_in_fava.sh` -- View multiple test cases in Fava interface

### Test Data
The `tests/data/` directory contains:
- Individual `.beancount` files for testing different tax scenarios
- `cgtcalc_inputs_beancount/` -- Converted test cases from external tools
- Sample files like `trivial_sample.beancount` for quick testing

### Configuration
The plugin accepts configuration in Beancount files via custom directives. Key functionality includes:
- Capital gains tax calculations using UK tax rules (Section 104 holding, bed & breakfast rules)
- Support for multiple asset types (stocks, crypto, etc.)
- Exchange rate conversion using HMRC rates or Beancount price directives
- Excel and interactive Fava reporting

## Timing Expectations

- `make deps-testing`: ~30 seconds
- `make format`: <1 second  
- `make lint`: <1 second
- `make test`: ~3 seconds (15 tests)
- CLI tool execution: ~1 second for simple files, longer for complex scenarios
- Fava startup: ~2-3 seconds

**NEVER CANCEL** any command - let all operations complete fully.

## Troubleshooting

**Network timeouts during build or deps-testing**: This is expected in restricted environments. 
- Check if existing installation works: `python -c "import beancount_plugin_tax_uk.calculate_tax; print('Import works')"`
- If import works, proceed with development using existing installation
- If import fails, dependencies need to be installed, try alternative installation methods

**Import errors**: First check if dependencies can be imported, then ensure `make deps-testing` completed successfully.

**Test failures**: Always run the validation sequence: `make format` → `make lint` → `make test`

**Fava plugin not appearing**: Verify installation via import test, then check the Fava extensions configuration in setup.cfg.

## Important Notes

- This is a tax calculation tool - accuracy is critical. Always verify results manually.
- The plugin implements UK-specific tax rules (Section 104 holding, bed & breakfast rules, etc.).
- Test files in `tests/data/` provide examples of supported transaction patterns.
- When making changes, always test with both the CLI tool and Fava interface.
- The codebase uses type hints and follows Python best practices.