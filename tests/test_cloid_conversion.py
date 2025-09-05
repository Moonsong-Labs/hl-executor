#!/usr/bin/env python3
"""Test script for cloid conversion functionality"""

import sys

sys.path.insert(0, "src")

from handlers.place_order import parse_cloid


def test_cloid_conversion():
    """Test various cloid input formats"""

    test_cases = [
        # (input, expected_success, description)
        ("123456", True, "Decimal integer"),
        ("0x1e240", True, "Hex with 0x prefix"),
        ("0", True, "Zero"),
        ("0x0", True, "Zero hex"),
        ("0xabcdef123456", True, "Large hex value"),
        ("999999999", True, "Large decimal"),
        ("0xffffffffffffffffffffffffffffffff", True, "Max 16-byte value"),
        ("340282366920938463463374607431768211455", True, "Max decimal (2^128-1)"),
        ("340282366920938463463374607431768211456", False, "Over max (2^128)"),
        ("0x100000000000000000000000000000000", False, "Over max hex"),
        ("1e240", False, "Hex without 0x prefix (not supported)"),
        ("invalid", False, "Invalid string"),
        ("0xGHI", False, "Invalid hex characters"),
        ("123abc", False, "Mixed decimal/hex"),
        ("abc123", False, "Hex-like without 0x"),
        ("", False, "Empty string"),
    ]

    print("Testing cloid conversion functionality:\n")
    print("-" * 60)

    passed = 0
    failed = 0

    for test_input, should_succeed, description in test_cases:
        try:
            result = parse_cloid(test_input)
            if should_succeed:
                # Get the raw cloid string representation
                cloid_str = str(result)
                # Check it's properly formatted (0x + 32 hex chars)
                if cloid_str.startswith("0x") and len(cloid_str) == 34:
                    print(f"✅ PASS: {description}")
                    print(f"   Input: {test_input}")
                    print(f"   Output: {cloid_str}")
                    passed += 1
                else:
                    print(f"❌ FAIL: {description}")
                    print(f"   Input: {test_input}")
                    print(f"   Output format invalid: {cloid_str}")
                    failed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Input: {test_input}")
                print(f"   Expected error but got: {result}")
                failed += 1
        except ValueError as e:
            if not should_succeed:
                print(f"✅ PASS: {description}")
                print(f"   Input: {test_input}")
                print(f"   Error (expected): {e}")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Input: {test_input}")
                print(f"   Unexpected error: {e}")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: {description}")
            print(f"   Input: {test_input}")
            print(f"   Unexpected exception: {e}")
            failed += 1

        print()

    print("-" * 60)
    print(f"\nResults: {passed} passed, {failed} failed")

    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(test_cloid_conversion())
