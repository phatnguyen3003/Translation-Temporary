"""Command-line interface for Auto_Translate."""

import argparse
import sys
from .translator import Translator
from .memory import get_ram_mb
from .config import LANGUAGE_MAP


def main():
    parser = argparse.ArgumentParser(
        description="Auto_Translate: Ultra-lightweight Vietnamese-to-Any-Language translator (< 512MB RAM)"
    )
    parser.add_argument(
        "-t", "--target", default="English", help="Target language (e.g. English, French, Japanese, German, Spanish, Chinese)"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Launch interactive translation session"
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="List supported target languages"
    )
    parser.add_argument(
        "text", nargs="?", default=None, help="Vietnamese text to translate"
    )

    args = parser.parse_args()

    if args.list:
        supported = sorted(set(k.capitalize() for k in LANGUAGE_MAP.keys() if len(k) > 2))
        print(f"Supported target languages: {', '.join(supported)}")
        sys.exit(0)

    print(f"[*] Initializing Auto_Translate (Current RAM: {get_ram_mb():.1f} MB)...")
    translator = Translator()
    print(f"[*] Engine ready. RAM: {get_ram_mb():.1f} MB\n")

    if args.interactive or not args.text:
        print("=== Auto_Translate Interactive Mode ===")
        print(f"Target Language: {args.target}")
        print("Type Vietnamese text and press Enter (or 'exit' / 'q' to quit):\n")
        try:
            while True:
                user_input = input("VI > ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit", "q"):
                    break
                result = translator.translate(user_input, args.target)
                print(f"{args.target} > {result}")
                print(f"[RAM: {get_ram_mb():.1f} MB]\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
    else:
        result = translator.translate(args.text, args.target)
        print(result)


if __name__ == "__main__":
    main()
