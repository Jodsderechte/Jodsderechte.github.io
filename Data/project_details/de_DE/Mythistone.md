Mythistone zeigt Informationen, die Spieler nutzen können, um ihre chancen auf Erfolg im Videospiel **World of Warcraft**, insbesondere in **Mythic+**, zu verbessern.

---

## Was ist ein Videospiel?

Denken Sie an ein Videospiel wie an eine interaktive Fernsehserie kombiniert mit einem Brettspiel: 
 
- **Interaktive Handlung und Herausforderung.** Spieler steuern Charaktere auf dem Bildschirm und treffen in Echtzeit Entscheidungen.  
- **Fähigkeiten & Teamarbeit.** Erfolg hängt oft von schnellem Denken, Strategie und Zusammenarbeit ab.  
- **Wettkampf weltweit.** Millionen Menschen spielen online und vergleichen ihre Leistungen.

---

## Was ist World of Warcraft?

- **Genre & Umfang:** WoW ist ein riesiges Online-Rollenspiel (MMORPG), in dem Hunderttausende von Spielern gleichzeitig verbunden sind.  
- **Charakterentwicklung:** Jeder Spieler erstellt einen _Charakter_ (Avatar), der durch Erfahrungspunkte wächst, neue Fähigkeiten erlernt und bessere Ausrüstung sammelt.  
- **Zusammenarbeit & Wettbewerb:** Spieler schließen sich zusammen, um schwierige Herausforderungen zu meistern, oder treten gegeneinander an – ähnlich wie funktionsübergreifende Teams bei komplexen Projekten.

---

## Was ist Mythic+

- **Dungeon-Herausforderungen:** „Dungeons“ sind instanzierte, mehrstufige Herausforderungen. Man kann sie sich vorstellen wie zeitlich begrenzte Hackathons oder Projekt-Sprints mit steigender Schwierigkeit.  
- **Skalierende Schwierigkeit:** Mythic+ wendet einen Schwierigkeits-„Multiplikator“ auf jeden Dungeon an, sodass Teams schneller koordinieren und jede Fähigkeit optimieren müssen, um strenge Zeitlimits einzuhalten.  
- **Ranglisten & Leistungskennzahlen:** Durchläufe werden zeitlich gemessen und bewertet. Höhere Punktzahlen spiegeln bessere Teamarbeit, Strategie und individuelle Leistung wider.

---

## Was ist Mythistone

- **Zweck:** Mythistone ist eine webbasierte Analyseplattform für WoW-Spieler. Sie sammelt Leistungsdaten aus Tausenden Mythic+-Dungeons und stellt sie in klaren, umsetzbaren Formaten dar.  
- **Hauptfunktionen:**
    - **Empfehlungen für Builds:** Welche Fähigkeiten („Talente“) und Skill-Verteilungen liefern die besten Ergebnisse für eine bestimmte Rolle? Ähnlich wie die Empfehlung eines optimalen Qualifikationsprofils für eine Stelle.  
    - **Ausrüstungsoptimierung:** Welche Ausrüstungsgegenstände bringen die besten Leistungssteigerungen? Vergleichbar mit Ratschlägen zu Zertifizierungen oder Tools, die die Produktivität steigern.  
    - **Talent-Profile & Berichte:** Visuelle Zusammenfassungen der Entscheidungen der Top-Spieler. Wie Benchmark-Berichte, die Best Practices aus der Branche zeigen.

---

## Wie es aufgebaut wurde

1. **Datenquelle:** Blizzard stellt eine offizielle API bereit, die Mythic+-Ranglisten und Charakterprofile (Ausrüstung, Talente, Leistung) zugänglich macht.  
2. **Datenerfassung:**
     - Ein Python-Skript („Runner“) läuft kontinuierlich auf einem Windows-Server und fragt die Blizzard-API nach aktualisierten Ranglisten- und Charakterdaten ab.  
     - Die abgerufenen Daten werden in eine MySQL-Datenbank auf einem Ubuntu-Server eingefügt.  
3. **Seitenerstellung:**
     - GitHub Actions-Workflows lösen Python-Jobs aus, die frische Daten aus MySQL abrufen.  
     - Mithilfe von Jinja-Templates generieren diese Jobs vollstatische HTML-Seiten (Builds, Ausrüstungs-Leitfäden, Ranglisten).  
4. **Deployment:**
     - Die statischen Seiten werden in einen GitHub Pages-Branch gepusht und publiziert, ohne Ausfallzeiten.
