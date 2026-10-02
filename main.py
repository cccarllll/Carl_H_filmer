import os
import requests
import json
import csv


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


def main():
    os.makedirs("data", exist_ok=True)
    decade = get_decade_from_user()
    raw_movies = get_swedish_movies_by_decade(decade)
    movies = clean_movies(raw_movies)
    imdb_matched = False
    save_movies(movies, decade, imdb_matched)
    print(f"Antal filmer: {len(movies)}")


if __name__ == "__main__":
    main()
