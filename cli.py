#!/usr/bin/env python3
"""
Simulate the CLI interface without any project.
"""
import sys

if __name__ == '__main__':
	from pyplanet.core.management import execute_from_command_line
	execute_from_command_line(sys.argv)
