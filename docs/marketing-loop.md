# Little Days · Marketing-Betrieb

Ziel: qualifizierte Aufmerksamkeit für Little Days und hilfreiche Ressourcen, mit messbaren
Experimenten und möglichst wenig zusätzlichem Geld. Keine zugesagte AI-Platzierung.

## Zwei tatsächliche Laufwege

1. GitHub Actions arbeitet täglich um 05:23 UTC: letzte Beobachtungen wiederherstellen,
   Messregeln testen, angeschlossene Messquellen abfragen, Live-Seiten prüfen,
   Entscheidung und 90-Tage-Historie als 30 Tage verfügbares Folge-Artefakt speichern.
   Ohne Zugang erscheint missing_credentials. Die nächste erfolgreiche Tagesausführung
   übernimmt die bisherige Historie; längere Ausfälle als die Artefaktaufbewahrung verlieren sie.
2. Die lokale tägliche Codex-Automation in diesem Chat übernimmt Recherche, Einordnung,
   Entwürfe, begründete Website-Änderungen und GitHub-PRs. Sie nutzt den vorhandenen
   Codex-Zugang, benötigt einen verfügbaren Rechner und eine laufende App und verbraucht
   das vorhandene Nutzungskontingent. Ausgefallene Läufe nicht nachträglich als erfolgreich ausweisen.

Der kostenpflichtige API-Codex-Job bleibt ausgeschaltet. Keine zusätzlichen Abos oder Anzeigen.

## Rollen innerhalb eines täglichen Laufs

- **Measurement:** Provider-Verbindung und Aktualität prüfen. Nur aggregierte Daten.
- **Strategy:** maximal eine Hypothese priorisieren; aktive Experimente abwarten.
- **Content:** Fakten kontrollieren, hilfreiche Antwortblöcke und Ressourcen verbessern.
- **Distribution:** eine relevante Fundstelle recherchieren und individuellen Entwurf vorbereiten.
- **Quality:** Tests, behauptete Produktfunktionen, Links, mobile Darstellung und Datenschutz prüfen.
- **Learning:** Baseline, Zeitraum und Ergebnis dokumentieren; unsichere Resultate als unsicher belassen.

Das sind Arbeitsschritte eines koordinierten Agenten. Es sind keine sechs unkontrolliert
parallel schreibenden Agenten und keine sechs zusätzlichen API-Rechnungen.

## Messung

Die Seite sendet nur nach einer aktiven Zustimmung ld_pageview, ld_explore, ld_contact,
ld_resource und ld_download an PostHog EU, Projekt 300977. Kein SDK, keine Wiedererkennung
über Seiten hinweg, keine Aufzeichnungen und keine Personenprofile. Ein Klick ist keine
abgeschickte E-Mail und kein App-Download. Herkunft nur als grobe Kategorie; UTM-Quelle
nur aus linkedin, instagram, eltern, producthunt, partner, sonst unattributed.

Google Search Console: verifizierte URL-Präfix-Property. Sitemap ist eingereicht; der erste
Provider-Abruf meldete am 10. Oktober noch einen Lesefehler. Öffentlicher Abruf ist HTTP 200
mit application/xml und gültigem XML, die hostweite robots.txt ist 404. Nach nächster
Sitemap-Veröffentlichung wurde erneut eingereicht und vom Provider angenommen; der
Abrufstatus blieb zunächst fehlerhaft. Kein Indexierungserfolg aus HTTP 200 ableiten.

PostHog-Lesezugriff ist seit 10. Oktober 2026 als POSTHOG_READ_KEY in GitHub eingerichtet,
auf Query:Read und Projekt 300977 beschränkt. Verifizierter Actions-Durchlauf
38061767221: API connected, alle fünf Ereignissummen für die abgeschlossene
28-Tage-Periode noch 0. Fehlende Search-Console-API-Zugangsdaten und fehlende
GEO-Beobachtungen bleiben ausdrücklich als fehlend markiert.

Die Search-Console-API-Abfrage verwendet abgeschlossene 28 Tage mit 3 Tagen Verzögerung.
Nur Property-Summen, keine Suchbegriffe oder Besucherkennungen. Benötigt bestehenden
OAuth-Zugriff mit webmasters.readonly. Keine OAuth-Credentials aus Browser-Sessions extrahieren.

Lokaler Browser-Ersatz bei fehlender API-Verbindung: tatsächlich sichtbare Provider-Summen
in work/provider-snapshots.json festhalten. Format:

```json
{
  "search_console": {
    "observed_at": "2026-10-10T14:00:00+00:00",
    "status": "processing"
  }
}
```

Für echte verfügbare Werte status=connected mit start/end (YYYY-MM-DD) und metrics:
clicks, impressions, ctr (0..1), position. PostHog-Snapshot entsprechend mit den fünf
erwähnten Eventnamen. Unter 24 Stunden alte UI-Snapshots werden akzeptiert; keine Werte erfinden.
API oder Browser-Verbindung muss nachgewiesen sein, bevor sie als angeschlossen gilt.

GEO: eine feste kleine Prompt-Auswahl in optimization/prompts.json, einmal wöchentlich mit
gleicher Sprache, Engine und Suchmodus prüfen. Tatsächliche Beobachtungen mit
scripts/marketing/observe-geo.py protokollieren. Belege privat in work/ speichern. Keine
Modell-API-Antwort als Sichtbarkeit in der Endnutzer-Suche verbuchen. Der Panel-Anteil ist
weder Marktabdeckung noch ein allgemeines Ranking.

## Veränderung und Rückkehr zum bisherigen Stand

Ein Experiment braucht Hypothese, started_at, Baseline, Kennzahl, mindestens
28 Tage Beobachtung und Rückkehrkriterium. Höchstens ein laufendes Experiment.
Bei weniger als 100 Seitenaufruf-Ereignissen oder 10 Kontaktklicks in einer Vergleichsperiode
kein positives Ergebnis behaupten. Auch darüber ist ein Vorher/Nachher-Vergleich nur
beobachtend: Saison, Traffic-Mix, Einwilligung und Wiederholungsklicks können ihn verzerren.

Codex darf die freigegebenen Content-Seiten und den Experiment-/Entwurfsbestand ändern,
Tests ausführen, eine PR öffnen und eine kleine faktentreue Content-Korrektur nach grünen
Checks selbst zusammenführen. Keine täglichen Vollüberarbeitungen ohne Messgrund.
Rechtstexte, Tracking, Produktstatus, Metadaten und Workflows bleiben für Folge-Läufe geschützt.
Ein Revert erfolgt als nachvollziehbarer neuer Commit/PR, nicht durch Löschen von Historie.

## Distribution

Bereits veröffentlicht: Baby-Tagebuch-Vorlage und Betreuungsübergabe mit Text-Downloads.
Entwürfe für ELTERN, eigene soziale Kanäle und einen späteren Product-Hunt-Start sind in
optimization/distribution/drafts.md. Jede Gelegenheit hat einen Zustand und einen nächsten
Schritt in opportunities.json. Ein Entwurf bedeutet nicht, dass eine Nachricht verschickt wurde.

Externe E-Mails, Beiträge und Verzeichniseinträge werden erst nach einer ausdrücklichen
Freigabe für den konkreten Empfänger/Kanal versandt. Die aktuelle Anweisung aktiviert keine
Massenansprache. Keine erfundenen Bewertungen, bezahlten Platzierungen oder Link-Netzwerke.

Nach jedem erfolgreichen Pages-Deployment meldet IndexNow nur geänderte indexierbare
Seiten. Der Nachweis liegt im Website-Unterpfad, keyLocation begrenzt den URL-Bereich.
HTTP 200/202 bedeutet Empfang bzw. ausstehende Verifizierung – keine bestätigte Indexierung.

## Kosten und Betriebsgrenzen

GitHub Pages und diese öffentlichen Actions benötigen hier kein zusätzliches Abo.
PostHog ist ein bestehendes Projekt; kein kostenpflichtiges Upgrade wird ausgelöst.
Tarif-/Budgeteinstellungen vor höherem Traffic prüfen; ein Ereigniszähler ist keine Kostengarantie.
Keine garantierten Rankings nach 30 Tagen. Nach 30 Tagen bewerten wir echte Beobachtungen,
nicht eine versprochene Position.

## 30 Tage ab 10. Oktober 2026

- Tage 1–3: Indexierungszugänge, freiwillige Statistik, erste Ressourcen, tägliche Läufe prüfen.
- Tage 4–7: vorhandene Kanäle bestimmen; zwei freigegebene Einzelveröffentlichungen vorbereiten.
- Tage 8–14: erste tatsächliche Such-/Referral-Daten prüfen; höchstens eine weitere nützliche Ressource.
- Tage 15–21: reale Rückmeldungen und Zitierungen prüfen; keine künstliche Content-Masse.
- Tage 22–30: erste Baseline auswerten. Bei ausreichend Daten ein einzelnes messbares Experiment
  starten; sonst Datenlage verbessern und das Produkt weiter verständlich erklären.
