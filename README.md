# Kirpputori

## Sovelluksen Toiminnot

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan myynti-ilmoituksia.
- Käyttäjä näkee sovellukseen lisätyt myynti-ilmoitukset. Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät myynti-ilmoituksia.
- Käyttäjä pystyy etsimään myynti-ilmoituksia hakusanalla.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät jokaisesta käyttäjästä tilastoja ja käyttäjän lisäämät ilmoitukset.
- Käyttäjä pystyy valitsemaan ilmoitukselle yhden tai useamman luokittelun (esim. huonekalut, elektroniset laitteet, vaatteet)
- Käyttäjä pystyy lisäämään kommentteja sekä omien että muiden käyttäjien ilmoituksiin liittyen.

## Sovelluksen asennus

Asenna 'flask'-kirjasto:

```
$ pip install flask
```
Luo tietokannan taulut:
```
$ python init_db.py
```

Kännistää sovelluksen näin:
```
$ flask run
```