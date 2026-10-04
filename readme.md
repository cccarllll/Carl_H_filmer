# Svenska filmer per årtionde

Examensarbete i Python grund. Programmet hämtar filmer med svenskt ursprung från ett valt årtionde, lägger till IMDb-betyg och sparar resultatet lokalt.

GitHub: [Carl_H_filmer](https://github.com/cccarllll/Carl_H_filmer)

## Mål

Jag vill använda Python för att hämta, rensa och analysera filmdata. Projektet visar hur information från olika källor kan kombineras och sparas för fortsatt analys.

## Metod

Jag hämtar filminformation från Wikidata med `requests` och en SPARQL-fråga. Efter rensning matchar jag filmernas IMDb-id mot IMDb:s betygsfil. Resultatet sparas som JSON och CSV och kan läsas vid nästa körning.

Klassen `Film` innehåller titel och år. Barnklassen `RatedFilm` lägger till betyg och antal röster. Menyn visar filmlistan, antal filmer per år, en topplista och ett stapeldiagram. Topplistan visar högst tio filmer med minst 500 röster.

Jag använder standardbiblioteken `os`, `json`, `csv` och `gzip`, samt de externa biblioteken `requests` och `matplotlib`.

Notebooken hämtar automatiskt `data/1990.json` från GitHub om filen saknas, så den behöver inte laddas upp separat i Colab. En befintlig datafil behålls. Internet behövs för att hämta exempeldata och IMDb-betyg första gången.

## Resultat

Den sparade listan för 1990-talet innehåller 475 filmer efter rensning. Ett utdrag från programmets utskrift:

```text
Antal filmer per år:
1990: 41 filmer
1991: 46 filmer
1992: 38 filmer
```

Listan innehåller filmer som finns i Wikidata med Sverige angivet som ursprungsland och ett releasedatum inom det valda årtiondet.

## Branschanalys

Att hämta, rensa och kombinera data är vanligt arbete för AI-utvecklare och data engineers. Samma förarbete behövs inför exempelvis ett rekommendationssystem för filmer.

Mitt resultat visar varför datakvalitet spelar roll. Saknade uppgifter och rensning efter titel påverkar urvalet. Gränsen på 500 röster minskar påverkan från små röstunderlag men utesluter också mindre kända filmer. Sådana val skulle även påverka en AI-lösning som bygger på datan.

## Certifikat-koll

AWS står för Amazon Web Services och är en molnplattform där företag kan lagra data och köra program på servrar via internet. Ett relevant yrkescertifikat är [AWS Certified Data Engineer – Associate](https://aws.amazon.com/certification/certified-data-engineer-associate/). Det visar kunskaper i att samla in och omvandla data, bygga automatiserade dataflöden och kontrollera datakvalitet med AWS:s tjänster.

Certifikatet riktar sig främst till personer som arbetar med data engineering. För en AI-utvecklare är kunskaperna relevanta eftersom data behöver samlas in, bearbetas och kontrolleras innan den används i en AI-modell. Certifikatet är därför en möjlig fördjupning för den som vill arbeta med datadelen av AI-system.

## Reflektion

Jag byggde först programmet i en fil och delade sedan upp det i moduler. Det gjorde koden lättare att följa och gav varje modul ett tydligt ansvar.

Det svåraste var Wikidata-anropen, som ibland tog lång tid eller gav serverfel. Jag provade att hämta år för år, men det löste inte problemen. Lokal JSON-lagring gjorde det möjligt att återanvända hämtad data. Timeout och try/except begränsar väntan och ger tydliga felmeddelanden.

IMDb-filen saknar land och årtal, så jag behövde först filmlistan från Wikidata och sedan matcha med IMDb-id. Rensningen efter titel är enkel, men kan slå ihop olika filmer med samma titel. Sparade betyg uppdateras inte automatiskt. Nästa gång skulle jag börja med en liten testmängd och lägga till ett val för att uppdatera sparad data.

## Datakällor

- [Wikidata Query Service](https://query.wikidata.org/) för filminformation. Wikidatas strukturerade data är tillgänglig under [CC0](https://www.wikidata.org/wiki/Wikidata:Licensing).
- [IMDb:s betygsfil](https://datasets.imdbws.com/title.ratings.tsv.gz) för betyg och antal röster, enligt [IMDb:s användningsvillkor](https://help.imdb.com/article/imdb/general-information/can-i-use-imdb-data-in-my-software/G5JTRESSHJBBHTGX). IMDb-filen och kompletterade resultat sparas lokalt i `data/`. Exempelfilen innehåller inga IMDb-betyg.

Information courtesy of IMDb (https://www.imdb.com). Used with permission.

## GDPR

Jag använder filmuppgifter från Wikidata och sammanställda IMDb-betyg för att analysera filmer per årtionde. Programmet sparar inga uppgifter om den som använder det eller om enskilda personer som har röstat på IMDb. Filmdatan innehåller offentliga uppgifter om filmer, bland annat regissörernas namn.

## AI-stöd

Jag har använt Codex för kodförslag, felsökning och förklaringar, särskilt vid Wikidata-frågan och datahämtningen. Jag har provkört programmet och notebooken, även i Colab.
