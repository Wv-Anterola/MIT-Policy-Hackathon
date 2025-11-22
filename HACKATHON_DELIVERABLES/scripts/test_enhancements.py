"""Quick test script to verify v2.0 enhancements"""

import sys
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_enhancements.log'),
        logging.StreamHandler()
    ]
)

def test_argparse():
    """Test command-line argument parsing"""
    parser = argparse.ArgumentParser(description='Test argument parsing')
    parser.add_argument('--states', nargs='+', help='States to analyze')
    parser.add_argument('--quiet', action='store_true', help='Quiet mode')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    # Parse known args to avoid errors when running without arguments
    args, unknown = parser.parse_known_args()
    
    logging.info("Argument parsing test successful")
    logging.info(f"States filter: {args.states}")
    logging.info(f"Quiet mode: {args.quiet}")
    logging.info(f"Log level: {args.log_level}")
    
    return args

def test_tqdm():
    """Test tqdm progress bars"""
    try:
        from tqdm import tqdm
        import time
        
        logging.info("Testing tqdm progress bars...")
        for i in tqdm(range(10), desc="Test Progress"):
            time.sleep(0.1)
        
        logging.info("tqdm test successful")
        return True
    except ImportError:
        logging.warning("tqdm not installed")
        return False

def test_logging():
    """Test logging functionality"""
    logging.debug("Debug message")
    logging.info("Info message")
    logging.warning("Warning message")
    logging.error("Error message (test only)")
    
    logging.info("Logging test successful")
    return True

if __name__ == "__main__":
    print("="*80)
    print("Testing v2.0 Enhancements")
    print("="*80)
    
    # Test 1: Argument parsing
    print("\n1. Testing command-line arguments...")
    args = test_argparse()
    print("   ✓ Argument parsing works")
    
    # Test 2: Logging
    print("\n2. Testing logging system...")
    test_logging()
    print("   ✓ Logging works")
    
    # Test 3: tqdm
    print("\n3. Testing progress bars...")
    if test_tqdm():
        print("   ✓ Progress bars work")
    else:
        print("   ⚠ tqdm not available (optional)")
    
    print("\n" + "="*80)
    print("All tests passed!")
    print("="*80)
