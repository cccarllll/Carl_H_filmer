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


def main():
    os.makedirs("data", exist_ok=True)
    decade = get_decade_from_user()
    raw_movies = get_swedish_movies_by_decade(decade)
    print(f"Antal råa träffar: {len(raw_movies)}")


if __name__ == "__main__":
    main()
