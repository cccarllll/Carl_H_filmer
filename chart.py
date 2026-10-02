# matplotlib används för att skapa stapeldiagram.
import matplotlib.pyplot as plt


# Skapar ett stapeldiagram som visar hur många filmer som finns för varje år.
def show_movie_chart(movies, decade):
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

    # Sorterar åren så att diagrammets staplar kommer i tidsordning.
    years = sorted(movies_per_year)
    # En list comprehension bygger antalslistan i samma ordning som åren.
    number_of_movies = [movies_per_year[year] for year in years]

    # Ritar en stapel per år. Listan med antal bestämmer staplarnas höjd.
    # En ny figur gör att upprepade menyval inte ritar ovanpå gamla staplar.
    plt.figure()
    plt.bar(years, number_of_movies)
    plt.title(f"Antal svenska filmer per år, {decade}-talet")
    # Sätter etiketten under diagrammets vågräta axel.
    plt.xlabel("År")
    # Sätter etiketten vid diagrammets lodräta axel.
    plt.ylabel("Antal filmer")
    # Visar det färdiga diagrammet.
    plt.show()
