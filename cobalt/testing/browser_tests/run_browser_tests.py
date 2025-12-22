#!/usr/bin/env python3
import subprocess
import sys
import os
import re

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_browser_tests.py <path_to_executable> [gtest_filter]")
        sys.exit(1)

    binary_path = sys.argv[1]
    extra_filter = sys.argv[2] if len(sys.argv) > 2 else "*"

    if not os.path.isfile(binary_path):
        print(f"Error: Binary not found at {binary_path}")
        sys.exit(1)

    # 1. List all tests
    print(f"Listing tests from {binary_path}...")
    try:
        output = subprocess.check_output(
            [binary_path, "--gtest_list_tests", f"--gtest_filter={extra_filter}"], 
            text=True
        )
    except subprocess.CalledProcessError as e:
        print("Failed to list tests.")
        sys.exit(e.returncode)

    tests = []
    current_suite = None
    for line in output.splitlines():
        # Clean up the line
        line = line.strip()
        
        # Skip empty lines or logs (logs usually start with [pid:...)
        if not line or line.startswith('['):
            continue
            
        # Remove comments (starting with #)
        line = line.split('#')[0].strip()
        
        if not line:
            continue

        if line.endswith('.'):
            current_suite = line
        else:
            # It's a test name
            if current_suite:
                full_test_name = f"{current_suite}{line}"
                if "DISABLED_" not in full_test_name:
                    tests.append(full_test_name)
            else:
                print(f"Warning: Found test '{line}' without a suite. Skipping.")

    if not tests:
        print("No tests found matching the filter.")
        sys.exit(0)

    print(f"Found {len(tests)} tests. Running them one by one...\n")

    # 2. Run each test in a fresh process
    failed_tests = []
    passed_count = 0
    
    for i, test in enumerate(tests):
        print(f"[{i+1}/{len(tests)}] Running {test}...")
        try:
            # We pass the filter to run EXACTLY this test case.
            # Using --gtest_filter=ExactTestName
            # Add --single-process-tests to avoid content::LaunchTests creating a duplicate AtExitManager
            # Add standard Cobalt flags: --no-sandbox --single-process --no-zygote --ozone-platform=starboard
            cmd = [
                binary_path, 
                f"--gtest_filter={test}", 
                "--single-process-tests",
                "--no-sandbox",
                "--single-process",
                "--no-zygote",
                "--ozone-platform=starboard"
            ]
            
            # Run the test and let it print to stdout/stderr
            retcode = subprocess.call(cmd)
            
            if retcode != 0:
                print(f"FAILED: {test} (Exit code: {retcode})")
                failed_tests.append(test)
            else:
                passed_count += 1
                
        except KeyboardInterrupt:
            print("\nAborted by user.")
            sys.exit(130)
        except Exception as e:
            print(f"Error running {test}: {e}")
            failed_tests.append(test)

    print("\n" + "="*40)
    print(f"Total: {len(tests)}, Passed: {passed_count}, Failed: {len(failed_tests)}")
    
    if failed_tests:
        print("\nFailed Tests:")
        for t in failed_tests:
            print(f"  {t}")
        sys.exit(1)
    else:
        print("\nAll tests PASSED.")
        sys.exit(0)

if __name__ == '__main__':
    main()
