import os
import requests


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


# Tar bort filmer med samma titel och bygger en ren lista från Wikidatas råa API-svar.
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

            # Lägger den rensade filmen sist i listan.
            cleaned_movies.append(cleaned_movie)
            # add lägger titeln i mängden. Nästa träff med samma titel hoppas då över.
            # Två olika filmer med samma titel räknas också som dubletter med denna enkla metod.
            seen_titles.add(title)

    # Returnerar den nya listan efter att loopen gått igenom alla träffar.
    return cleaned_movies


def main():
    os.makedirs("data", exist_ok=True)
    decade = get_decade_from_user()
    raw_movies = get_swedish_movies_by_decade(decade)
    movies = clean_movies(raw_movies)
    print(f"Antal filmer: {len(movies)}")


if __name__ == "__main__":
    main()
