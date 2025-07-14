#!/usr/bin/env python3
"""
Standalone Ticket Generation Script
Generates tickets using the Ghost AI ticket generator.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    import logging
    from core.ticket_generator import TicketGenerator
    import argparse

    parser = argparse.ArgumentParser(description="Generate tickets with Ghost AI.")
    parser.add_argument('--num', type=int, default=3, help='Number of tickets to generate')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    generator = TicketGenerator(base_dir=Path.cwd())
    tickets = generator.generate_tickets(num_tickets=args.num)
    print(f"Generated {len(tickets)} tickets:")
    for t in tickets:
        print(t)

if __name__ == "__main__":
    main() 