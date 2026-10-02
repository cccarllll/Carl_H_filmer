import os


# Frågar efter ett årtal och räknar fram årtiondets första år.
def get_decade_from_user():
    while True:
        year = input("Ange ett årtal mellan 1920 och 2029 (Enter för 1990): ").strip()
        if year == "":
            return 1990
        if year.isdigit():
            year = int(year)
            if 1920 <= year <= 2029:
                # Heltalsdivision tar bort entalet; gånger tio ger årtiondet.
                return year // 10 * 10
        print("Fel: ange ett årtal mellan 1920 och 2029.")



def main():
    os.makedirs("data", exist_ok=True)
    decade = get_decade_from_user()
    print(f"{decade}-talet")


if __name__ == "__main__":
    main()
