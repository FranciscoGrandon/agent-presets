#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentPresets Mini (Backward-compatible entry point)
Delegates execution directly to agentpresets.py.

Creado por Francisco Grandón Vergara
"""
import sys
from agentpresets import main

if __name__ == "__main__":
    sys.exit(main())
