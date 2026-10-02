# Basklass för en film med information som alla filmer har.
class Film:
    # __init__ körs när objektet skapas. self syftar på just det objektet.
    def __init__(self, title, year):
        # Sparar parametern title som ett attribut i objektet.
        self.title = title
        # Sparar parametern year som ett attribut i objektet.
        self.year = year

    # Returnerar filmens år och titel i samma format som används vid utskrift.
    def get_title_with_year(self):
        # f-strängen sätter in attributens värden i texten. return lämnar tillbaka texten.
        return f"{self.year} - {self.title}"


# Barnklass som ärver titel och år från Film.
# Den lägger till IMDb-betyg och antal röster för filmer som kan vara med i topplistan.
class RatedFilm(Film):
    def __init__(self, title, year, imdb_rating, imdb_votes):
        # Anropar Films konstruktor för att spara titel och år i samma objekt.
        super().__init__(title, year)
        # float omvandlar exempelvis texten '7.5' till decimaltalet 7.5.
        self.imdb_rating = float(imdb_rating)
        # int omvandlar exempelvis texten '600' till heltalet 600.
        self.imdb_votes = int(imdb_votes)

    # Kontrollerar om filmen har tillräckligt många röster för topplistan.
    def has_enough_votes(self):
        # Jämförelsen ger True vid minst 500 röster, annars False.
        return self.imdb_votes >= 500

