# Define the directory containing the test files and the Python script
TEST_DIR := tests
PYTHON_SCRIPT := myrpal.py

# Find all files in the test directory
TEST_FILES := $(wildcard $(TEST_DIR)/*)

# Define the target that will run the Python script for each test file
.PHONY: run_tests

run_tests: $(TEST_FILES)
	ForEach ($file in $^) { \
		Write-Output "Running test for $$file"; \
		python $(PYTHON_SCRIPT) $$file -ast; \
	}
