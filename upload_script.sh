#!/bin/bash

# ==============================================================================
#  Ein Skript, um ein lokales Verzeichnis in ein leeres GitHub-Repository hochzuladen.
# ==============================================================================

# --- KONFIGURATION ---
# Bitte fügen Sie hier die URL Ihres GitHub-Repositories ein.
# Sie finden sie auf der GitHub-Seite Ihres Repositories (z.B. https://github.com/user/repo.git)
REPO_URL="[IHRE_REPOSITORY_URL_HIER_EINFUEGEN]"


# --- SKRIPT-LOGIK (bitte nichts hierunter ändern) ---

# Überprüfen, ob eine URL eingegeben wurde
if [ "$REPO_URL" == "[IHRE_REPOSITORY_URL_HIER_EINFUEGEN]" ]; then
    echo "FEHLER: Bitte öffnen Sie das Skript 'upload_script.sh' in einem Texteditor und ersetzen Sie '[IHRE_REPOSITORY_URL_HIER_EINFUEGEN]' durch die tatsächliche URL Ihres Repositories."
    exit 1
fi

# Überprüfen, ob Git installiert ist
if ! command -v git &> /dev/null
then
    echo "Git ist nicht installiert. Bitte installieren Sie es zuerst von https://git-scm.com/"
    exit 1
fi

echo "Git-Repository wird initialisiert..."
git init

echo "Alle Dateien werden zum Commit hinzugefügt..."
git add .

echo "Ein erster Commit wird erstellt..."
git commit -m "Initial commit: Upload des ZeroPlaySystem-Projekts"

echo "Der Hauptbranch wird auf 'main' gesetzt..."
git branch -M main

echo "Das Remote-Repository wird hinzugefügt..."
# Überprüfen, ob der Remote "origin" bereits existiert.
if git remote get-url origin > /dev/null 2>&1; then
    git remote set-url origin $REPO_URL
else
    git remote add origin $REPO_URL
fi

echo "Dateien werden in das GitHub-Repository hochgeladen..."
git push -u origin main

echo ""
echo "=============================================================================="
echo " Fertig! Ihre Dateien wurden erfolgreich zu GitHub hochgeladen."
echo " Sie können sie unter der folgenden URL einsehen (ohne .git am Ende):"
echo " ${REPO_URL%.git}"
echo "=============================================================================="
