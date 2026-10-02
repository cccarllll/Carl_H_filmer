# Svenska filmer per årtionde

Examensarbete i Python grund.

## Funktioner i detta steg

- Omvandlar ett årtal till årtionde, exempelvis 1991 till 1990. Enter ger 1990.
- Hämtar råa filmträffar från Wikidata med requests och hanterar nätverksfel.
- Bygger enkla filmfält och behåller den första träffen per titel med en mängd (set).
- Klassificerar filmer efter hur många viktiga fält som är ifyllda.
- Sparar den rensade filmlistan som JSON och CSV i data-mappen.
- Läser lokal JSON före nya nätanrop och hanterar fel vid filinläsning.
- Hämtar eller återanvänder IMDb-filen och matchar betyg och röster med IMDb-id.
- Använder Film och RatedFilm med arv för en topplista med minst 500 röster.
- Visar meny och diagram. Inmatningen kräver nu ett jämnt årtionde; 1991 ger en ny fråga.
- Delar upp funktionerna i moduler med tydliga ansvarsområden.

## Köra programmet

Installera biblioteken med `python -m pip install -r requirements.txt`.

Starta med `python main.py`. Tryck Enter för 1990.

Nätåtkomst behövs när data hämtas från externa källor.

## AI-stöd

AI-stöd används för struktur, felsökning och förklaringar.
