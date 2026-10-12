"""
Stock Portfolio Tracker
=======================
A clean, dependency-free command-line tool that calculates the total value
of a stock portfolio from manually defined prices.

  * Prices come from a hardcoded dictionary (STOCK_PRICES).
  * The user enters stock symbols and quantities.
  * A formatted report shows each holding, its portfolio weight and the total.
  * The report can optionally be saved as a .txt or .csv file.

Run:  python stock_tracker.py
"""

import csv
import os
import sys
from datetime import datetime

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

# Hardcoded stock prices (USD per share)
STOCK_PRICES = {
    "AAPL": 180,
    "TSLA": 250,
    "GOOGL": 140,
    "MSFT": 330,
    "AMZN": 125,
}

INNER = 68          # inner width of every box
BAR_WIDTH = 10      # width of the allocation bar

# --------------------------------------------------------------------------
# Terminal styling helpers
# --------------------------------------------------------------------------

if os.name == "nt":
    os.system("")   # enables ANSI escape codes on Windows 10+
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

USE_COLOR = (
    (sys.stdout.isatty() or os.environ.get("FORCE_COLOR"))
    and not os.environ.get("NO_COLOR")
)

CODES = {
    "bold": "1", "dim": "2",
    "red": "31", "green": "32", "yellow": "33",
    "blue": "34", "magenta": "35", "cyan": "36", "grey": "90",
}


def style(text, *names):
    """Wrap text in ANSI colour codes (no-op when colour is disabled)."""
    if not USE_COLOR or not names:
        return text
    codes = ";".join(CODES[n] for n in names)
    return f"\033[{codes}m{text}\033[0m"


def money(value):
    return f"${value:,.2f}"


def cell(text, width, align="<", *styles):
    """Pad plain text to a fixed width first, then colour it."""
    padded = f"{text:{align}{width}}"
    return style(padded, *styles)


# --------------------------------------------------------------------------
# Box drawing
# --------------------------------------------------------------------------

def box_top(colour="cyan"):
    return style("┌" + "─" * INNER + "┐", colour)


def box_bottom(colour="cyan"):
    return style("└" + "─" * INNER + "┘", colour)


def box_rule(colour="cyan"):
    return style("├" + "─" * INNER + "┤", colour)


def box_line(content="", plain_len=0, colour="cyan"):
    """A boxed row. plain_len is the visible length of `content`."""
    pad = max(INNER - 2 - plain_len, 0)
    edge = style("│", colour)
    return f"{edge} {content}{' ' * pad} {edge}"


def box_center(text, *styles, colour="cyan"):
    left = (INNER - 2 - len(text)) // 2
    right = INNER - 2 - len(text) - left
    edge = style("│", colour)
    return f"{edge} {' ' * left}{style(text, *styles)}{' ' * right} {edge}"


# --------------------------------------------------------------------------
# Screens
# --------------------------------------------------------------------------

def show_banner():
    print()
    print(style("╔" + "═" * INNER + "╗", "cyan"))
    print(box_center("", colour="cyan").replace("│", "║"))
    print(box_center("STOCK  PORTFOLIO  TRACKER", "bold", "cyan", colour="cyan").replace("│", "║"))
    print(box_center("Know what your portfolio is worth", "dim", colour="cyan").replace("│", "║"))
    print(box_center("", colour="cyan").replace("│", "║"))
    print(style("╚" + "═" * INNER + "╝", "cyan"))


def show_price_list():
    print()
    print(box_top("grey"))
    print(box_line(style("MARKET PRICES", "bold"), 13, "grey"))
    print(box_rule("grey"))
    items = list(STOCK_PRICES.items())
    for i in range(0, len(items), 3):
        row = ""
        plain = 0
        for symbol, price in items[i:i + 3]:
            label = f"{symbol:<6}"
            value = f"{money(price):<12}"
            row += style(label, "bold", "yellow") + style(value, "grey") + "  "
            plain += len(label) + len(value) + 2
        print(box_line(row, plain, "grey"))
    print(box_bottom("grey"))
    print()
    print(style("  Enter a symbol and quantity. Type ", "dim")
          + style("done", "bold")
          + style(" when finished.", "dim"))
    print()


def prompt(label):
    return input(style("  ›", "cyan", "bold") + f" {label:<10}" + style(": ", "grey")).strip()


def note(symbol, message, kind="ok"):
    icon = {"ok": style("✔", "green"), "err": style("✖", "red"),
            "info": style("•", "cyan")}[kind]
    print(f"    {icon} {message}")


def show_report(portfolio):
    """Print the final report. Returns the total value."""
    total = sum(h["value"] for h in portfolio.values())
    stamp = datetime.now().strftime("%d %b %Y, %H:%M")

    print()
    print(box_top())
    title = "PORTFOLIO REPORT"
    gap = INNER - 2 - len(title) - len(stamp)
    print(box_line(style(title, "bold", "cyan") + " " * gap + style(stamp, "dim"),
                   len(title) + gap + len(stamp)))
    print(box_rule())

    # header
    header = (cell("STOCK", 8, "<", "bold") + "  " + cell("QTY", 6, ">", "bold") + "  "
              + cell("PRICE", 11, ">", "bold") + "  " + cell("VALUE", 14, ">", "bold")
              + "  " + cell("WEIGHT", 7, ">", "bold") + "  " + " " * BAR_WIDTH)
    print(box_line(header, 8 + 2 + 6 + 2 + 11 + 2 + 14 + 2 + 7 + 2 + BAR_WIDTH))
    print(box_rule())

    # holdings, largest first
    for symbol, h in sorted(portfolio.items(), key=lambda kv: -kv[1]["value"]):
        weight = h["value"] / total * 100
        filled = round(weight / 100 * BAR_WIDTH)
        bar = style("█" * filled, "green") + style("░" * (BAR_WIDTH - filled), "grey")
        row = (cell(symbol, 8, "<", "bold", "yellow") + "  "
               + cell(f"{h['quantity']:,}", 6, ">") + "  "
               + cell(money(h["price"]), 11, ">", "grey") + "  "
               + cell(money(h["value"]), 14, ">", "green") + "  "
               + cell(f"{weight:.1f}%", 7, ">") + "  " + bar)
        print(box_line(row, 8 + 2 + 6 + 2 + 11 + 2 + 14 + 2 + 7 + 2 + BAR_WIDTH))

    # total
    print(box_rule())
    label = "TOTAL INVESTMENT"
    amount = money(total)
    gap = INNER - 2 - len(label) - len(amount)
    print(box_line(style(label, "bold") + " " * gap + style(amount, "bold", "green"),
                   len(label) + gap + len(amount)))
    print(box_bottom())

    # quick stats
    top_symbol, top = max(portfolio.items(), key=lambda kv: kv[1]["value"])
    shares = sum(h["quantity"] for h in portfolio.values())
    print()
    print(style("  Holdings      ", "grey") + f"{len(portfolio)}")
    print(style("  Total shares  ", "grey") + f"{shares:,}")
    print(style("  Largest       ", "grey") + f"{top_symbol} ({top['value'] / total * 100:.1f}% of portfolio)")
    return total


# --------------------------------------------------------------------------
# Input
# --------------------------------------------------------------------------

def get_portfolio():
    """Collect symbols and quantities. Repeated symbols are combined."""
    portfolio = {}
    while True:
        symbol = prompt("Symbol").upper()

        if symbol in ("DONE", "Q", "QUIT"):
            break
        if not symbol:
            continue
        if symbol not in STOCK_PRICES:
            note(symbol, f"'{symbol}' is not in the price list.", "err")
            continue

        raw = prompt("Quantity")
        try:
            quantity = int(raw.replace(",", ""))
            if quantity <= 0:
                raise ValueError
        except ValueError:
            note(symbol, "Quantity must be a whole number greater than 0.", "err")
            continue

        price = STOCK_PRICES[symbol]
        if symbol in portfolio:
            portfolio[symbol]["quantity"] += quantity
        else:
            portfolio[symbol] = {"quantity": quantity, "price": price}
        portfolio[symbol]["value"] = portfolio[symbol]["quantity"] * price

        note(symbol, f"{quantity:,} × {symbol} @ {money(price)} = "
                     f"{style(money(quantity * price), 'green')}")
        print()
    return portfolio


# --------------------------------------------------------------------------
# File export
# --------------------------------------------------------------------------

def save_txt(portfolio, total, filename):
    stamp = datetime.now().strftime("%d %b %Y, %H:%M")
    line = "=" * 62
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{line}\n  PORTFOLIO REPORT  |  {stamp}\n{line}\n")
        f.write(f"{'STOCK':<8}{'QTY':>6}{'PRICE':>13}{'VALUE':>16}{'WEIGHT':>10}\n")
        f.write("-" * 62 + "\n")
        for symbol, h in sorted(portfolio.items(), key=lambda kv: -kv[1]["value"]):
            weight = h["value"] / total * 100
            f.write(f"{symbol:<8}{h['quantity']:>6,}{money(h['price']):>13}"
                    f"{money(h['value']):>16}{weight:>9.1f}%\n")
        f.write("-" * 62 + "\n")
        f.write(f"{'TOTAL INVESTMENT':<27}{money(total):>35}\n{line}\n")


def save_csv(portfolio, total, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Stock", "Quantity", "Price", "Value", "Weight %"])
        for symbol, h in sorted(portfolio.items(), key=lambda kv: -kv[1]["value"]):
            writer.writerow([symbol, h["quantity"], h["price"], h["value"],
                             round(h["value"] / total * 100, 1)])
        writer.writerow(["TOTAL", "", "", total, 100.0])


def offer_save(portfolio, total):
    print()
    choice = prompt("Save? (txt/csv/no)").lower()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if choice in ("txt", "t"):
        name = f"portfolio_{stamp}.txt"
        save_txt(portfolio, total, name)
    elif choice in ("csv", "c"):
        name = f"portfolio_{stamp}.csv"
        save_csv(portfolio, total, name)
    else:
        print(style("\n  Report not saved.", "dim"))
        return
    print()
    note("", f"Saved to {style(name, 'bold')}")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    show_banner()
    show_price_list()
    portfolio = get_portfolio()

    if not portfolio:
        print(style("\n  No stocks entered. Goodbye!\n", "dim"))
        return

    total = show_report(portfolio)
    offer_save(portfolio, total)
    print()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(style("\n\n  Goodbye!\n", "dim"))