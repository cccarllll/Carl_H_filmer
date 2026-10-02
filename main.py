# os används för att skapa mappen data där programmet sparar filer.
import os

# Importerar funktionen som visar stapeldiagrammet.
from chart import show_movie_chart

# Importerar barnklassen som används i topplistan.
from film import RatedFilm

# Importerar funktionerna som laddar ner och matchar IMDb-betyg.
from imdb_data import add_imdb_ratings, download_imdb_ratings

# Importerar funktionerna som hämtar och rensar data från Wikidata.
from wikidata_api import clean_movies, get_swedish_movies_by_decade

# Importerar funktionerna som sparar och läser filmdata lokalt.
from data_handler import load_movies, movie_data_exists, save_movies

# Rensar terminalfönstret när programmet startar.
# Windows använder kommandot cls och andra system använder clear.
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# Skapar mappen data där programmets CSV- och JSON-filer sparas.
# exist_ok=True gör att programmet fortsätter även om mappen redan finns.
os.makedirs("data", exist_ok=True)


# Skriver ut filmens årtal, titel, IMDb-betyg och antal IMDb-röster i terminalen.
# Saknas betyg eller röster i IMDb-filen visas texten Saknas i stället.
def print_movies(movies):
    # Går igenom listan. movie syftar på en films dictionary under varje varv.
    for movie in movies:
        title = movie["title"]
        # Hakparenteser läser värdet för en nyckel. Om nyckeln saknas uppstår KeyError.
        year = movie["year"]
        # get undviker fel om nyckeln saknas. or ger reservtext om värdet är tomt.
        rating = movie.get("imdb_rating") or "Saknas"
        # Samma reservtext används när antal röster saknas eller är tomt.
        votes = movie.get("imdb_votes") or "Saknas"

        print(f"{year} - {title} | IMDb: {rating} | Röster: {votes}")


# Räknar hur många filmer som finns för varje år i den aktuella filmlistan.
# Resultatet skrivs ut efter listan så att det blir lätt att se fördelningen per år.
def print_movie_count_by_year(movies):
    # {} skapar en tom dictionary. År blir nyckel och antal filmer blir värde.
    movies_per_year = {}

    # Går igenom listan. movie syftar på en films dictionary under varje varv.
    for movie in movies:
        # Hakparenteser läser värdet för en nyckel. Om nyckeln saknas uppstår KeyError.
        year = movie["year"]

        # Kontrollerar om året ännu saknas bland dictionaryns nycklar.
        if year not in movies_per_year:
            # Startar räknaren på noll första gången året förekommer.
            movies_per_year[year] = 0

        # Ökar årets räknare med ett. += 1 betyder lägg till 1 till det gamla värdet.
        movies_per_year[year] += 1

    print("\nAntal filmer per år:")

    # sorted ger en sorterad lista med dictionaryns nycklar, alltså åren.
    for year in sorted(movies_per_year):
        print(f"{year}: {movies_per_year[year]} filmer")


# Returnerar IMDb-betyget som används när RatedFilm-objekt ska sorteras.
def get_imdb_rating(movie):
    # Här är movie ett RatedFilm-objekt, så attributet läses med punktnotation.
    return movie.imdb_rating


# Sorterar filmer med IMDb-betyg från högst till lägst och visar de tio första.
# En film behöver minst 500 IMDb-röster för att vara med, så att ett fåtal röster
# inte får för stor påverkan på topplistan.
def print_top_rated_movies(movies):
    # En lista för RatedFilm-objekt som klarar topplistans krav.
    rated_movies = []

    # Går igenom listan. movie syftar på en films dictionary under varje varv.
    for movie in movies:
        # and kräver att både betyg och röster har ett värde.
        if movie.get("imdb_rating") and movie.get("imdb_votes"):
            # Skapar ett objekt från filmens dictionary. Konstruktorn omvandlar betyg och röster.
            rated_movie = RatedFilm(
                movie["title"],
                movie["year"],
                movie["imdb_rating"],
                movie["imdb_votes"],
            )

            # Anropar objektets metod som kontrollerar gränsen på 500 röster.
            if rated_movie.has_enough_votes():
                # Lägger till objektet i listan över godkända filmer.
                rated_movies.append(rated_movie)

    # key anger funktionen som hämtar sorteringsvärdet för varje objekt.
    # Inga parenteser efter funktionsnamnet: sort anropar den. reverse=True ger högst först.
    rated_movies.sort(key=get_imdb_rating, reverse=True)

    print("\nTopplista: högst IMDb-betyg (minst 500 röster)")

    # [:10] väljer högst tio filmer. enumerate ger både platsnummer och objekt.
    # start=1 gör att numreringen börjar på 1 i stället för 0.
    for position, movie in enumerate(rated_movies[:10], start=1):
        print(
            f"{position}. {movie.get_title_with_year()} | "
            f"IMDb: {movie.imdb_rating} | Röster: {movie.imdb_votes}"
        )


# Visar programmets enkla meny tills användaren väljer att avsluta.
# Val 1 visar filmlistan, val 2 räknar filmer per år, val 3 visar en topplista
# och val 4 visar ett stapeldiagram.
def show_menu(movies, decade):
    # Upprepar blocket tills break avslutar loopen eller return lämnar funktionen.
    while True:
        # print visar text för användaren; den lämnar inte tillbaka ett menyval.
        print("\nMeny")
        print("1. Visa alla filmer")
        print("2. Visa antal filmer per år")
        print("3. Visa topplista efter IMDb-betyg")
        print("4. Visa stapeldiagram över antal filmer per år")
        print("0. Avsluta")

        # input väntar på användaren och returnerar svaret som text.
        choice = input("Välj ett alternativ: ")

        if choice == "1":
            print(f"\n{decade}-talet")
            print_movies(movies)
        elif choice == "2":
            print_movie_count_by_year(movies)
        elif choice == "3":
            print_top_rated_movies(movies)
        elif choice == "4":
            show_movie_chart(movies, decade)
        elif choice == "0":
            print("Programmet avslutas.")
            # Avslutar den närmaste loopen.
            break
        # Körs när de föregående villkoren i samma if/elif-kedja inte stämde.
        else:
            print("Fel: välj 1, 2, 3, 4 eller 0.")


# Frågar användaren efter ett giltigt årtionde mellan 1920 och 2020.
# Om användaren bara trycker Enter används 1990 som standard för att underlätta testning.
# Returnerar årtiondet direkt, till exempel 1990.
def get_decade_from_user():
    # Upprepar blocket tills break avslutar loopen eller return lämnar funktionen.
    while True:
        # input ger text. strip tar bort mellanslag i början och slutet.
        decade = input("Ange ett årtionde mellan 1920 och 2020 (Enter för 1990): ").strip()

        # Tom text betyder att användaren tryckte Enter utan att skriva ett värde.
        if decade == "":
            # Returnerar ett heltal som standardvärde; loopen fortsätter inte efter return.
            return 1990

        # Kontrollerar om texten består av siffror innan omvandlingen till heltal.
        if decade.isdigit():
            # Omvandlar texten till ett heltal så att den kan jämföras och användas i beräkningar.
            decade = int(decade)

            # Kontrollerar intervallet och att resten vid division med 10 är noll.
            # Därför godkänns 1990 men inte 1995.
            if 1920 <= decade <= 2020 and decade % 10 == 0:
                # Lämnar tillbaka det godkända årtiondet och avslutar funktionen.
                return decade

        print("Fel: ange ett årtionde mellan 1920 och 2020, till exempel 1990.")

# Samlar programmets körning i en funktion så att flödet blir lätt att följa.
def main():
    # Startar programmet med en tom terminal.
    clear_screen()

    # Hämtar årtiondet som användaren vill söka i.
    decade = get_decade_from_user()

    # Kontrollerar en gång om årtiondets data redan finns sparad lokalt.
    data_exists = movie_data_exists(decade)

    # Läser lokal arbetsdata eller medföljande exempeldata för årtiondet.
    if data_exists:
        print("Läser sparad filmdata...")
        movies, imdb_matched = load_movies(decade)

    # Hämtar och rensar filmer från Wikidata när data saknas lokalt.
    else:
        print("Hämtar filmdata från Wikidata. Det kan ta någon minut...")
        raw_movies = get_swedish_movies_by_decade(decade)

        print("Rensar och förbereder filmdata...")
        movies = clean_movies(raw_movies)

        # Nya Wikidata-filmer har ännu inte matchats mot IMDb.
        imdb_matched = False
        # Behåller de rensade filmerna även om IMDb-steget senare misslyckas.
        save_movies(movies, decade, imdb_matched)

    # Gäller både nya filmer och lokala filer som ännu inte matchats.
    if not imdb_matched:
        # Hämtar IMDbs betygsfil bara om den saknas lokalt.
        print("Läser IMDb-betyg och antal röster...")
        imdb_filename = download_imdb_ratings()

        # Fyller på den nya filmlistan med IMDb-betyg och antal röster.
        add_imdb_ratings(movies, imdb_filename)

        # Sparar den kompletta nya filmlistan med IMDb-data lokalt.
        # True betyder att matchningen är gjord, inte att varje film fått betyg.
        imdb_matched = True
        save_movies(movies, decade, imdb_matched)

    # Visar menyn när filmlistan är klar att användas.
    show_menu(movies, decade)


# Kör main-funktionen när filen startas direkt från terminalen.
if __name__ == "__main__":
    main()
