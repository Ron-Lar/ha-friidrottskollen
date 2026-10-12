# Friidrottskollen för Home Assistant
Använd på egen risk, denna är Beta!!!

Visar när och var en svensk friidrottare tävlar, med TV-kanal och sändningstid.
Data hämtas från Svenska Friidrottsförbundets sidor *Friidrottskollen* och *TV-tablå* på friidrott.se.

## Installation

**HACS:** Lägg till repot som custom repository (typ *Integration*), installera och starta om HA.
**Manuellt:** Kopiera `custom_components/friidrottskollen` till `/config/custom_components/` och starta om HA.

Lägg sedan till integrationen under *Inställningar → Enheter och tjänster → Lägg till integration → Friidrottskollen*
och ange idrottarens namn, t.ex. `Daniel Ståhl`. Integrationen kan läggas till flera gånger för olika idrottare.

## Entiteter

| Entitet | Innehåll |
|---|---|
| `sensor.<namn>_nasta_tavling` | Nästa tävling. Attributet `tavlingar` innehåller alla kommande tävlingar. |
| `sensor.<namn>_nasta_tavlingsdag` | Datum för nästa tävling. |
| `calendar.<namn>_tavlingar` | Alla tävlingar som heldagshändelser, med plats, TV och länkar. |

Varje tävling i `tavlingar` har fälten `datum`, `slut`, `namn`, `plats`, `tid` (sändningens starttid), `tv`, `tvLank` och `lank`.

## Begränsningar

- Friidrottskollen är preliminär och uppdateras för hand av förbundet.
- `tid` är när TV-sändningen börjar, inte när grenen startar.
- Integrationen läser HTML-sidor. Om friidrott.se byter utseende kan tolkningen behöva justeras.
