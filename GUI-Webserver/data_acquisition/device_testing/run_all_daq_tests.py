#!/usr/bin/env python3
"""
Master Test Runner for All DAQ Readers
Runs comprehensive tests for all data acquisition devices:
- LabJack1 (U3) - Pressure and temperature sensors
- LabJack2 (T4) - Flow meters  
- LakeShore - Temperature controller
- Teledyne - Flow meter
- MaxiGauge - Pressure controller
- IVC - Pressure controller
- QT - Modbus TCP PLC
"""

import sys
import time
import logging
import traceback
import subprocess
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('all_daq_tests.log')
    ]
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_SCRIPTS = {
    "LabJack1 (U3)": "test_labjack1.py",
    "LabJack2 (T4)": "test_labjack_t4.py", 
    "LakeShore": "test_lakeshore_comprehensive.py",
    "Teledyne": "test_teledyne.py",
    "MaxiGauge": "test_maxigauge.py",
    "IVC": "test_ivc_comprehensive.py",
    "QT": "test_qt_comprehensive.py"
}

def run_single_test(test_name, script_path):
    """Run a single test script and return results"""
    logger.info(f"Running {test_name} test...")
    
    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per test
        )
        
        success = result.returncode == 0
        
        # Log the output
        if result.stdout:
            logger.info(f"{test_name} stdout:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"{test_name} stderr:\n{result.stderr}")
            
        return {
            "name": test_name,
            "success": success,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": 0  # Could add timing if needed
        }
        
    except subprocess.TimeoutExpired:
        logger.error(f"{test_name} test timed out after 5 minutes")
        return {
            "name": test_name,
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "Test timed out",
            "duration": 300
        }
    except Exception as e:
        logger.error(f"Error running {test_name} test: {e}")
        return {
            "name": test_name,
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": 0
        }

def run_all_tests():
    """Run all DAQ tests and return comprehensive results"""
    logger.info("=" * 80)
    logger.info("STARTING COMPREHENSIVE DAQ TEST SUITE")
    logger.info("=" * 80)
    logger.info(f"Test started at: {datetime.now()}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Working directory: {Path.cwd()}")
    
    results = []
    total_tests = len(TEST_SCRIPTS)
    
    for i, (test_name, script_path) in enumerate(TEST_SCRIPTS.items(), 1):
        logger.info(f"\n{'='*20} Test {i}/{total_tests}: {test_name} {'='*20}")
        
        # Check if script exists
        if not Path(script_path).exists():
            logger.error(f"Test script not found: {script_path}")
            results.append({
                "name": test_name,
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Script not found: {script_path}",
                "duration": 0
            })
            continue
        
        # Run the test
        result = run_single_test(test_name, script_path)
        results.append(result)
        
        # Brief pause between tests
        time.sleep(2)
    
    return results

def generate_summary_report(results):
    """Generate a comprehensive summary report"""
    logger.info("\n" + "=" * 80)
    logger.info("COMPREHENSIVE DAQ TEST SUMMARY REPORT")
    logger.info("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    logger.info(f"Test Execution Summary:")
    logger.info(f"  Total Tests: {total_tests}")
    logger.info(f"  Passed: {passed_tests}")
    logger.info(f"  Failed: {failed_tests}")
    logger.info(f"  Success Rate: {success_rate:.1f}%")
    logger.info(f"  Test Duration: {datetime.now()}")
    
    logger.info(f"\nDetailed Results:")
    logger.info("-" * 80)
    
    for result in results:
        status = "✓ PASSED" if result["success"] else "✗ FAILED"
        logger.info(f"{status:10} {result['name']}")
        
        if not result["success"]:
            logger.info(f"           Return Code: {result['returncode']}")
            if result["stderr"]:
                logger.info(f"           Error: {result['stderr'][:100]}...")
    
    logger.info("-" * 80)
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL DAQ TESTS PASSED! All devices are working correctly.")
        return True
    else:
        logger.error(f"❌ {failed_tests} test(s) failed. Please check individual test logs.")
        
        # List failed tests
        failed_names = [r["name"] for r in results if not r["success"]]
        logger.error(f"Failed tests: {', '.join(failed_names)}")
        
        return False

def main():
    """Main test runner function"""
    try:
        # Run all tests
        results = run_all_tests()
        
        # Generate summary report
        all_passed = generate_summary_report(results)
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        logger.info("\nTest suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in test suite: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 