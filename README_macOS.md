# Spielanleitung für macOS

Diese Anleitung hilft dir, das Spiel "Chronicle of the Idle Hero" auf deinem Mac Schritt für Schritt zum Laufen zu bringen. Es sind keine Vorkenntnisse nötig!

## Schritt 1: Python 3 überprüfen und installieren

macOS wird oft mit einer älteren Python-Version ausgeliefert. Wir brauchen aber Python 3.

1.  **Terminal öffnen:**
    *   Öffne den Finder, gehe zu `Programme` -> `Dienstprogramme` und starte die `Terminal`-App.

2.  **Python-Version prüfen:**
    *   Tippe den folgenden Befehl in das Terminal ein und drücke `Enter`:
      ```bash
      python3 --version
      ```
    *   Wenn eine Versionsnummer angezeigt wird (z.B. `Python 3.9.6`), ist alles super, und du kannst diesen Schritt überspringen.
    *   Wenn eine Fehlermeldung erscheint, musst du Python 3 installieren.

3.  **Python 3 installieren (falls nötig):**
    *   **Download:** Gehe auf die offizielle Python-Webseite:
        [https://www.python.org/downloads/](https://www.python.org/downloads/)
    *   **Installer ausführen:** Klicke auf den "Download Python"-Button. Es wird automatisch die richtige Version für den Mac heruntergeladen. Führe die heruntergeladene `.pkg`-Datei aus und folge den Installationsanweisungen.

## Schritt 2: Spieldateien herunterladen

Lade den Ordner mit den Spieldateien herunter und entpacke ihn an einem Ort, den du leicht wiederfindest, zum Beispiel auf deinem Schreibtisch. Der Ordner heißt `ZeroPlay`.

## Schritt 3: Notwendige Erweiterung installieren

1.  **Zum Spielordner navigieren:**
    *   Öffne das `Terminal` (falls es noch nicht offen ist).
    *   Du musst dem Terminal sagen, wo sich der Spielordner befindet. Wenn du den Ordner `ZeroPlay` zum Beispiel auf dem Schreibtisch hast, tippe folgenden Befehl ein und drücke `Enter`:
      ```bash
      cd Desktop/ZeroPlay
      ```
    *   *Hinweis: `cd` steht für "change directory" (wechsle Verzeichnis).*

2.  **Bibliothek installieren:**
    *   Das Spiel benötigt eine Erweiterung zur Bilddarstellung. Tippe folgenden Befehl in dasselbe Fenster ein und drücke `Enter`:
      ```bash
      pip3 install Pillow
      ```
    *   Warte kurz, bis die Installation abgeschlossen ist.

## Schritt 4: Das Spiel starten

Du bist fast am Ziel! Da du dich bereits im richtigen Ordner befindest, musst du nur noch den folgenden Befehl eingeben und mit `Enter` bestätigen:

```bash
python3 main.py
```

Das Spiel sollte nun starten. Viel Spaß!
