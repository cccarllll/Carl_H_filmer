# os används för att kontrollera om en JSON-fil redan finns sparad lokalt.
import os

# json används för att spara och läsa filmdata i JSON-format.
import json

# csv används för att spara filmdata i tabellformat som kan öppnas i Excel.
import csv


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


# Kontrollerar om filmdata finns i data-mappen.
def movie_data_exists(decade):
    # Returnerar True om sökvägen finns, annars False. f-strängen sätter in årtiondet.
    return os.path.exists(f"data/{decade}.json")
