#!/usr/bin/env python3
"""
Test script to verify PyO3 module can be imported and used.
"""

import sys
import os

# Add the release directory to Python path
so_dir = os.path.join(
    os.path.dirname(__file__), "..", "apps", "control-plane", "target", "release"
)
sys.path.insert(0, so_dir)

print(f"Searching for module in: {so_dir}")
print("Files in directory:")
for f in os.listdir(so_dir):
    if f.startswith("libmastermind"):
        print(f"  - {f}")

try:
    import mastermind_control_plane

    print("\n✅ Successfully imported mastermind_control_plane")

    # Test detect_flow_py function
    flow = mastermind_control_plane.detect_flow_py("Create a report for me")
    print(f"✅ detect_flow_py('Create a report for me') = '{flow}'")

    # Test detect_flow_with_metadata_py
    metadata = mastermind_control_plane.detect_flow_with_metadata_py("Tell me a joke")
    print("✅ detect_flow_with_metadata_py('Tell me a joke'):")
    for key, value in metadata.items():
        print(f"    {key}: {value}")

    # Test FlowDetector class
    detector = mastermind_control_plane.FlowDetector()
    flow2 = detector.detect("Generate reports for multiple users")
    print(f"✅ FlowDetector.detect('Generate reports for multiple users') = '{flow2}'")

    print("\n✅ All tests passed!")

except ImportError as e:
    print(f"\n❌ Failed to import: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
