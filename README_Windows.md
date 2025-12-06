# Spielanleitung für Windows

Diese Anleitung hilft dir, das Spiel "Chronicle of the Idle Hero" auf deinem Windows-Computer Schritt für Schritt zum Laufen zu bringen. Es sind keine Vorkenntnisse nötig!

## Schritt 1: Python installieren

Das Spiel benötigt Python, eine einfache Programmiersprache.

1.  **Download:** Gehe auf die offizielle Python-Webseite:
    [https://www.python.org/downloads/](https://www.python.org/downloads/)

2.  **Installer ausführen:** Klicke auf den großen "Download Python"-Button, um die Installationsdatei herunterzuladen. Führe die heruntergeladene `.exe`-Datei aus.

3.  **Wichtiger Haken:** Im ersten Fenster der Installation siehst du ganz unten eine Option namens **"Add Python to PATH"**. Setze hier unbedingt einen Haken! Das ist sehr wichtig.
    ![Python Installer](https://i.imgur.com/f6vLA2J.png)

4.  **Installation:** Klicke danach auf **"Install Now"** und folge den Anweisungen.

## Schritt 2: Spieldateien herunterladen

Lade den Ordner mit den Spieldateien herunter und entpacke ihn an einem Ort, den du leicht wiederfindest, zum Beispiel auf deinem Desktop. Der Ordner heißt `ZeroPlay`.

## Schritt 3: Notwendige Erweiterung installieren

1.  **Kommandozeile öffnen:**
    *   Drücke die `Windows-Taste` auf deiner Tastatur.
    *   Tippe `cmd` ein und drücke `Enter`. Es öffnet sich ein schwarzes Fenster, die Kommandozeile.

2.  **Zum Spielordner navigieren:**
    *   Du musst der Kommandozeile sagen, wo sich der Spielordner befindet. Wenn du den Ordner `ZeroPlay` zum Beispiel auf dem Desktop hast, tippe folgenden Befehl ein und drücke `Enter`:
      ```bash
      cd Desktop/ZeroPlay
      ```
    *   *Hinweis: Der Pfad kann bei dir anders sein. `cd` steht für "change directory" (wechsle Verzeichnis).*

3.  **Bibliothek installieren:**
    *   Das Spiel benötigt eine Erweiterung zur Bilddarstellung. Tippe folgenden Befehl in dasselbe Fenster ein und drücke `Enter`:
      ```bash
      pip install Pillow
      ```
    *   Warte kurz, bis die Installation abgeschlossen ist.

## Schritt 4: Das Spiel starten

Du bist fast am Ziel! Da du dich bereits im richtigen Ordner befindest, musst du nur noch den folgenden Befehl eingeben und mit `Enter` bestätigen:

```bash
python main.py
```

Das Spiel sollte nun starten. Viel Spaß!

---
*Bei Problemen: Stelle sicher, dass du bei der Python-Installation den Haken bei "Add Python to PATH" gesetzt hast.*
