import re
import json

def load_receipt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_prices(text):
    """
    Extract all price values like:
    308,00
    1 200,00
    """
    pattern = r'\d{1,3}(?: \d{3})*,\d{2}'
    prices = re.findall(pattern, text)

    # convert to float
    prices = [float(p.replace(" ", "").replace(",", ".")) for p in prices]

    return prices


def extract_products(text):
    """
    Extract product names between numbering and quantity lines
    """
    pattern = r'\d+\.\s*\n(.+?)\n\s*\d+,\d+\s*x'
    products = re.findall(pattern, text, re.DOTALL)

    cleaned = [p.replace("\n", " ").strip() for p in products]

    return cleaned


def extract_total(text):
    match = re.search(r'ИТОГО:\s*\n?\s*([\d\s]+,\d{2})', text)

    if match:
        return float(match.group(1).replace(" ", "").replace(",", "."))

    return None


def extract_payment_method(text):
    match = re.search(r'(Банковская карта|Наличные)', text)

    if match:
        return match.group(1)

    return "Unknown"


def extract_datetime(text):
    match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4})\s*(\d{2}:\d{2}:\d{2})', text)

    if match:
        return {
            "date": match.group(1),
            "time": match.group(2)
        }

    return None


def parse_receipt(text):

    prices = extract_prices(text)
    products = extract_products(text)
    total = extract_total(text)
    payment = extract_payment_method(text)
    datetime = extract_datetime(text)

    return {
        "products": products,
        "prices": prices,
        "total_amount": total,
        "payment_method": payment,
        "datetime": datetime
    }


def main():

    text = load_receipt("raw.txt")

    parsed = parse_receipt(text)

    print(json.dumps(parsed, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
