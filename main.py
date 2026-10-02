import os
import requests
import json
import csv
import gzip


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



# Hämtar svenska filmer från Wikidata för hela det valda årtiondet.
# Frågan hämtar bland annat originaltitel, regissör, genre, speltid och IMDb-id.
# OPTIONAL gör att en film tas med även när något extra fält saknas.
def get_swedish_movies_by_decade(decade):
    end_year = decade + 9

    query = f"""
    SELECT ?filmLabel ?releaseDate
           (GROUP_CONCAT(DISTINCT ?directorLabel; separator=", ") AS ?directors)
           (GROUP_CONCAT(DISTINCT ?genreLabel; separator=", ") AS ?genres)
           (SAMPLE(?duration) AS ?duration)
           (SAMPLE(?imdbId) AS ?imdbId)
           (SAMPLE(?description) AS ?description)
           (SAMPLE(?originalTitle) AS ?originalTitle)
           (GROUP_CONCAT(DISTINCT ?originalLanguageLabel; separator=", ") AS ?originalLanguages)
    WHERE {{
      ?film wdt:P31/wdt:P279* wd:Q11424;
            wdt:P495 wd:Q34;
            wdt:P577 ?releaseDate.
      FILTER(YEAR(?releaseDate) >= {decade} && YEAR(?releaseDate) <= {end_year})

      OPTIONAL {{
        ?film wdt:P57 ?director.
        ?director rdfs:label ?directorLabel.
        FILTER(LANG(?directorLabel) = "sv")
      }}
      OPTIONAL {{
        ?film wdt:P136 ?genre.
        ?genre rdfs:label ?genreLabel.
        FILTER(LANG(?genreLabel) = "sv")
      }}
      OPTIONAL {{ ?film wdt:P2047 ?duration. }}
      OPTIONAL {{ ?film wdt:P345 ?imdbId. }}
      OPTIONAL {{ ?film schema:description ?description. FILTER(LANG(?description) = "sv") }}
      OPTIONAL {{ ?film wdt:P1476 ?originalTitle. }}
      OPTIONAL {{
        ?film wdt:P364 ?originalLanguage.
        ?originalLanguage rdfs:label ?originalLanguageLabel.
        FILTER(LANG(?originalLanguageLabel) = "sv")
      }}

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "sv,en". }}
    }}
    GROUP BY ?filmLabel ?releaseDate
    ORDER BY ?releaseDate ?filmLabel
    """

    try:
        response = requests.get(
            "https://query.wikidata.org/sparql",
            params={"query": query, "format": "json"},
            headers={"User-Agent": "ExamenCarlH/0.2"},
            timeout=60,
        )

        # Skriver ut HTTP-statuskoden så att det syns om API-anropet lyckades.
        print(f"Wikidata svarade med statuskod: {response.status_code}")
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        print(f"Fel: Wikidata kunde inte svara just nu. Försök igen senare. {error}")
        raise SystemExit(1)

    return data["results"]["bindings"]


# Kontrollerar hur mycket av den viktigaste informationen som finns om en film.
def get_information_level(movie):
    # En lista med nycklarna till de fyra fält som används för informationsnivån.
    required_fields = ["directors", "genres", "duration", "imdb_id"]
    # bool blir False för tom text och True för innehåll. sum räknar True som 1.
    filled_fields = sum(bool(movie[field]) for field in required_fields)

    # len ger antalet fält. == jämför värden; = används för att tilldela ett värde.
    if filled_fields == len(required_fields):
        return "Fullständig"
    # Kontrolleras om föregående villkor var falskt. Här finns minst ett ifyllt fält.
    elif filled_fields > 0:
        return "Delvis"

    # Denna rad nås bara om inget av de tidigare villkoren redan har returnerat.
    return "Grundläggande"


# Tar bort filmer med samma titel och bygger en ren lista från Wikidatas råa API-svar.
# Originaltiteln används när den finns och varje film får en informationsnivå.
def clean_movies(movies):
    # En tom lista som ska innehålla de rensade filmerna.
    cleaned_movies = []
    # set() skapar en tom mängd med unika värden. Samma titel kan bara finnas en gång.
    # Mängden används för snabba medlemskontroller med in. Den har ingen bestämd ordning.
    seen_titles = set()

    # Går igenom listan. movie syftar på en films dictionary under varje varv.
    for movie in movies:
        # Läser en dictionary inuti en annan: först filmLabel, sedan dess value.
        title = movie["filmLabel"]["value"]

        # Tar bara med filmen om titeln ännu inte finns i mängden.
        if title not in seen_titles:
            # get ger ett standardvärde om nyckeln saknas. Här används {} och sedan tom text.
            original_title = movie.get("originalTitle", {}).get("value", "")

            # Skapar en dictionary med nyckel–värde-par för en film.
            cleaned_movie = {
                # or väljer originaltiteln om den är ifylld, annars används Wikidata-titeln.
                "title": original_title or title,
                # Nyckeln till vänster är fältnamnet; värdet till höger hämtas från variabeln.
                "original_title": original_title,
                "wikidata_title": title,
                # [:4] tar textens första fyra tecken, alltså årtalet i datumet.
                "year": movie["releaseDate"]["value"][:4],
                # Om directors saknas används en tom dictionary. Om value saknas används tom text.
                "directors": movie.get("directors", {}).get("value", ""),
                "genres": movie.get("genres", {}).get("value", ""),
                "duration": movie.get("duration", {}).get("value", ""),
                "imdb_id": movie.get("imdbId", {}).get("value", ""),
                "imdb_rating": movie.get("imdbRating", {}).get("value", ""),
                "imdb_votes": movie.get("imdbVotes", {}).get("value", ""),
                "description": movie.get("description", {}).get("value", ""),
                "original_languages": movie.get("originalLanguages", {}).get("value", ""),
            }
            # Anropar funktionen och sparar dess resultat under en ny nyckel.
            cleaned_movie["information_level"] = get_information_level(cleaned_movie)

            # Lägger den rensade filmen sist i listan.
            cleaned_movies.append(cleaned_movie)
            # add lägger titeln i mängden. Nästa träff med samma titel hoppas då över.
            # Två olika filmer med samma titel räknas också som dubletter med denna enkla metod.
            seen_titles.add(title)

    # Returnerar den nya listan efter att loopen gått igenom alla träffar.
    return cleaned_movies


# Sparar den rensade filmlistan i både CSV- och JSON-format.
# CSV kan öppnas i exempelvis Excel och JSON kan användas direkt av programmet.
def save_movies(movies, decade, imdb_matched):
    csv_filename = f"data/{decade}.csv"
    json_filename = f"data/{decade}.json"

    # w skapar eller skriver över filen. newline undviker extra tomrader i CSV.
    with open(csv_filename, "w", encoding="utf-8", newline="") as file:
        # Skriver dictionaries som tabellrader med kolumnerna som anges i fieldnames.
        writer = csv.DictWriter(
            file,
            # Namnen bestämmer både vilka fält CSV-filen får och deras kolumnordning.
            fieldnames=[
                "year",
                "title",
                "original_title",
                "wikidata_title",
                "original_languages",
                "directors",
                "genres",
                "duration",
                "imdb_id",
                "imdb_rating",
                "imdb_votes",
                "description",
                "information_level",
            ],
        )
        # Skriver kolumnnamnen på tabellens första rad.
        writer.writeheader()
        # Skriver en rad för varje film i listan.
        writer.writerows(movies)

    # Öppnar JSON-filen för skrivning. En befintlig fil med samma namn skrivs över.
    with open(json_filename, "w", encoding="utf-8") as file:
        # Sparar både filmlistan och om IMDb-matchningen har körts.
        # Python använder True/False; i JSON skrivs de som true/false.
        data = {"imdb_matched": imdb_matched, "movies": movies}
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"\nFilmerna sparades i {csv_filename} och {json_filename}")


# Läser den sparade JSON-filen när data för årtiondet redan finns lokalt.
def load_movies(decade):
    filename = f"data/{decade}.json"

    # Använder medföljande Wikidata-exempel om ingen lokal arbetsfil finns.
    if not os.path.exists(filename):
        filename = f"examples/{decade}.json"

    # Läser JSON-objektet som innehåller markeringen och filmlistan.
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Fel: filen {filename} saknas. Lägg den i data-mappen och försök igen.")
        raise SystemExit(1)
    except (json.JSONDecodeError, UnicodeError):
        print(f"Fel: {filename} innehåller inte läsbar JSON. Kontrollera filen.")
        raise SystemExit(1)
    except OSError as error:
        print(f"Fel: {filename} kunde inte läsas. {error}")
        raise SystemExit(1)

    # Accepterar bara vårt nya format med en boolesk markering och en lista.
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("imdb_matched"), bool)
        or not isinstance(data.get("movies"), list)
    ):
        print(f"Fel: {filename} måste innehålla imdb_matched och movies i det nya formatet.")
        raise SystemExit(1)

    movies = data["movies"]
    # Kontrollerar att listan innehåller film-dictionaries med titel och år.
    if any(
        not isinstance(movie, dict) or not {"title", "year"}.issubset(movie)
        for movie in movies
    ):
        print(f"Fel: {filename} måste innehålla en filmlista med titel och år.")
        raise SystemExit(1)

    # Två returvärden tas emot som movies, imdb_matched i huvudprogrammet.
    return movies, data["imdb_matched"]


# Kontrollerar om lokal filmdata eller medföljande exempeldata finns.
def movie_data_exists(decade):
    # Returnerar True om sökvägen finns, annars False. f-strängen sätter in årtiondet.
    return os.path.exists(f"data/{decade}.json") or os.path.exists(f"examples/{decade}.json")


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


def main():
    os.makedirs("data", exist_ok=True)
    decade = get_decade_from_user()
    if movie_data_exists(decade):
        print("Läser sparad filmdata...")
        movies, imdb_matched = load_movies(decade)
    else:
        raw_movies = get_swedish_movies_by_decade(decade)
        movies = clean_movies(raw_movies)
        imdb_matched = False
        save_movies(movies, decade, imdb_matched)
    if not imdb_matched:
        imdb_filename = download_imdb_ratings()
        add_imdb_ratings(movies, imdb_filename)
        imdb_matched = True
        save_movies(movies, decade, imdb_matched)
    print(f"Antal filmer: {len(movies)}")


if __name__ == "__main__":
    main()
