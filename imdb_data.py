# os används för att kontrollera om IMDb-filen redan finns sparad lokalt.
import os

# csv används för att läsa raderna i IMDbs TSV-fil.
import csv

# gzip används för att läsa IMDbs komprimerade betygsfil utan att packa upp den.
import gzip

# requests används för att ladda ned IMDbs betygsfil.
import requests


# Hämtar IMDbs officiella fil med betyg och antal röster till mappen data.
# Filen laddas bara ned om den saknas.
# Om nedladdningen misslyckas skrivs ett fel ut och programmet avslutas.
def download_imdb_ratings():
    filename = "data/imdb_ratings.tsv.gz"

    # Kontrollerar om filen redan finns så att den kan återanvändas.
    if os.path.exists(filename):
        # Lämnar tillbaka sökvägen och avslutar funktionen.
        return filename

    url = "https://datasets.imdbws.com/title.ratings.tsv.gz"

    # Försöker köra blocket. Om ett passande fel uppstår går körningen till except.
    try:
        response = requests.get(url, timeout=60)
        # Visar serverns statuskod och kontrollerar sedan om svaret är ett HTTP-fel.
        print(f"IMDb svarade med statuskod: {response.status_code}")
        response.raise_for_status()

        # with stänger filen automatiskt. wb betyder skrivning av binära data.
        with open(filename, "wb") as file:
            # Sparar svarets råa bytes i filen, här den komprimerade IMDb-filen.
            file.write(response.content)
    # Fångar nätverksfel eller filfel och sparar felinformationen i error.
    except (requests.RequestException, OSError) as error:
        print(f"Fel: IMDb-filen kunde inte laddas ner. {error}")
        # Avslutar körningen med felkod 1. I Jupyter visas detta som ett undantag.
        raise SystemExit(1)

    # Lämnar tillbaka sökvägen och avslutar funktionen.
    return filename


# Matchar våra filmer mot IMDbs betygsfil med hjälp av varje films IMDb-id.
# Funktionen läser filen rad för rad och uppdaterar bara filmer som har ett IMDb-id.
# Returnerar True om minst ett betyg eller antal röster ändrades.
def add_imdb_ratings(movies, filename):
    # Bygger en dictionary där IMDb-id är nyckel och filmens dictionary är värde.
    movies_by_imdb_id = {
        # Tar bara med filmer med IMDb-id. Samma id kan ha ett värde i dictionaryn.
        movie["imdb_id"]: movie for movie in movies if movie.get("imdb_id")
    }
    # En boolesk variabel som håller reda på om något värde har ändrats.
    ratings_updated = False

    # Öppnar gzip-filen som läsbar text (rt). UTF-8 anger textens teckenkodning.
    with gzip.open(filename, "rt", encoding="utf-8") as file:
        # Varje rad blir en dictionary. \t betyder tabulator, som skiljer TSV-kolumnerna.
        reader = csv.DictReader(file, delimiter="\t")

        # Läser en rad i taget så att hela IMDb-tabellen inte behöver läggas i en lista.
        for row in reader:
            # tconst är IMDb-id. in kontrollerar om id:t finns bland dictionaryns nycklar.
            if row["tconst"] in movies_by_imdb_id:
                # Hämtar samma film-dictionary som ligger i movies. Ändringar syns därför där också.
                movie = movies_by_imdb_id[row["tconst"]]

                if movie.get("imdb_rating") != row["averageRating"]:
                    movie["imdb_rating"] = row["averageRating"]
                    # Markerar att minst ett värde har ändrats.
                    ratings_updated = True

                if movie.get("imdb_votes") != row["numVotes"]:
                    movie["imdb_votes"] = row["numVotes"]
                    # Markerar att minst ett värde har ändrats.
                    ratings_updated = True

    # Returnerar True om något ändrades, annars False.
    return ratings_updated
