---
layout: default
title: IcePaperlessAI
parent: Data & Tools
nav_order: 20
---

# IcePaperlessAI

[View on GitHub](https://github.com/icepaule/IcePaperlessAI){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

**IcePaperlessAI**

{% raw %}
Betriebsdokumentation und Fixes für eine selbstgehostete Dokumenten-Pipeline aus
**Netzwerkscanner → Paperless-ngx → paperless-ai → lokales LLM (Ollama)**.

Dieses Repository entstand aus einer Fehlersuche, bei der die Pipeline scheinbar lief,
aber seit Monaten keine Scans mehr verarbeitete und Dokumente falsch verschlagwortete.
Es waren **sechs voneinander unabhängige Fehler** auf drei Hosts — jeder für sich harmlos
aussehend, zusammen ein Totalausfall.

Der Inhalt ist bewusst so geschrieben, dass er auch für andere Betreiber dieses Stacks
nützlich ist. Zwei der Befunde sind Bugs in Upstream-Software, nicht Fehlkonfigurationen.

---

## Inhaltsverzeichnis

- [Architektur](#architektur)
- [Zusammenfassung der Befunde](#zusammenfassung-der-befunde)
- [Befund 1 — Der Scanner war nie angeschlossen](#befund-1--der-scanner-war-nie-angeschlossen)
- [Befund 2 — OCR lief auf Englisch](#befund-2--ocr-lief-auf-englisch)
- [Befund 3 — RESTRICT_TO_EXISTING_TAGS war wirkungslos (Upstream-Bug)](#befund-3--restrict_to_existing_tags-war-wirkungslos-upstream-bug)
- [Befund 4 — TOKEN_LIMIT über dem Modellkontext](#befund-4--token_limit-über-dem-modellkontext)
- [Befund 5 — Ollama-Blockade ohne Timeout](#befund-5--ollama-blockade-ohne-timeout)
- [Befund 6 — Paperless' eigenes Tag-Matching war abgeschaltet](#befund-6--paperless-eigenes-tag-matching-war-abgeschaltet)
- [Härtung des LLM-Hosts](#härtung-des-llm-hosts)
- [Verifikation](#verifikation)
- [Repository-Inhalt](#repository-inhalt)
- [Betriebs-Runbook](#betriebs-runbook)
- [Fallstricke](#fallstricke)
- [Upstream-Meldungen](#upstream-meldungen)

---

## Architektur

```
  Brother MFC (Scan-to-Folder, SMB)
             │
             ▼
  /srv/scanner                    ← Samba-Share auf dem Docker/K3s-Host
             │
             │  scan-mover.timer (systemd, 60 s)      ◀── Befund 1: fehlte komplett
             ▼
  <consume-dir>                   ← hostPath, in den Paperless-Pod gemountet
             │
             │  Paperless-Consumer (Polling 30 s)
             │  OCRmyPDF / Tesseract                  ◀── Befund 2: Sprache "eng"
             ▼
  Paperless-ngx  ──────────────┐
   (PostgreSQL, Redis, Tika)   │  REST-API
                               ▼
                        paperless-ai
                               │  Prompt + Tag-/Korrespondentenliste
                               │                      ◀── Befund 3: Liste immer leer
                               │                      ◀── Befund 4: num_ctx > Modell
                               ▼
                        Ollama (eigener GPU-Host)     ◀── Befund 5: Blockade + OOM

  Quer dazu: Paperless' eigenes Tag-Matching          ◀── Befund 6: faktisch abgeschaltet
```

Alle Komponenten laufen im LAN. Paperless-ngx und paperless-ai liegen als Deployments
in einem K3s-Cluster, Ollama auf einem separaten Rechner mit zwei GPUs.

---

## Zusammenfassung der Befunde

| # | Komponente | Fehler | Auswirkung | Art |
|---|---|---|---|---|
| 1 | scan-mover | Bei Migration `docker-compose` → K3s nicht mit übernommen | Scans erreichten Paperless nie; Backlog von Monaten | Migrationsfehler |
| 2 | Paperless-ngx | `PAPERLESS_OCR_LANGUAGE` nicht gesetzt → Default `eng` | Deutsche Belege ohne Umlaute; kaputte Namen | Fehlkonfiguration |
| 3 | paperless-ai | `_formatTagsList()` verwirft String-Arrays | `RESTRICT_TO_EXISTING_TAGS` wirkungslos; Modell sah nie die Tags | **Upstream-Bug** |
| 4 | paperless-ai | `TOKEN_LIMIT` (128000) > Modellkontext (32768) | `num_ctx` jenseits des trainierten Fensters | Fehlkonfiguration |
| 5 | paperless-ai / Ollama | `validateOllamaConfig()` ruft `axios.post` **ohne Timeout** | Ein blockierendes Ollama verhindert den Start jedes Scans | **Upstream-Bug** |
| 6 | Paperless-ngx | Tag-Regeln leer bzw. doppelt escaped | Deterministische Zuordnungen dem LLM überlassen — es riet | Fehlkonfiguration |

Zusätzlich: Der LLM-Host hatte kein Speicherlimit für Ollama und ging zweimal an einem
globalen OOM in die Knie (siehe [Härtung](#härtung-des-llm-hosts)).

---

## Befund 1 — Der Scanner war nie angeschlossen

### Symptom

Dutzende PDFs lagen unberührt im Samba-Share, das älteste Monate alt. Paperless kannte
keines davon.

### Ursache

Die ursprüngliche `docker-compose.yml` enthielt einen kleinen Hilfscontainer:

```yaml
  scan-mover:
    image: alpine:3.19
    volumes:
      - /srv/scanner:/scan-inbox
      - ./data/inbox:/paperless-consume
    command: >
      sh -c 'apk add --no-cache inotify-tools &&
        inotifywait -m -e close_write -e moved_to --format "%f" /scan-inbox |
        while read FILE; do ... mv "/scan-inbox/$$FILE" "/paperless-consume/$$FILE"; done'
```

Beim Umzug nach Kubernetes wurden Paperless und paperless-ai als Deployments neu gebaut —
der `scan-mover` fiel dabei ersatzlos weg. Niemandem fiel es auf, weil Paperless
weiterhin Dokumente aus anderen Quellen (E-Mail-Import) erhielt.

### Zweiter, subtilerer Fehler im Original

`inotifywait -m` reagiert ausschließlich auf **neu eintreffende** Dateien. Selbst wenn der
Container weitergelaufen wäre, hätte er einen einmal entstandenen Rückstand **nie**
abgearbeitet. Ein Neustart des Containers hätte den Backlog dauerhaft liegen lassen.

### Lösung

Ein systemd-Timer statt eines Watch-Containers. Er ist zustandslos, räumt bestehende
Dateien mit ab und übersteht Neustarts:

```bash
# scripts/nuc-ha/scan-mover.sh (Auszug)
find "$SRC" -maxdepth 1 -type f -mmin +0.5 \
     \( -iname '*.pdf' -o -iname '*.jpg' -o ... \) -print0 |
while IFS= read -r -d '' f; do
    # Noch von smbd geöffnet? Dann später nochmal.
    if command -v fuser >/dev/null 2>&1 && fuser -s "$f" 2>/dev/null; then
        continue
    fi
    ...
    mv -n "$f" "$tgt"
done
```

Zwei Schutzmechanismen gegen halb geschriebene Uploads:

- `-mmin +0.5` — nur Dateien, die seit 30 s nicht mehr verändert wurden.
- `fuser -s` — überspringt Dateien, die `smbd` noch offen hält.

`mv -n` verhindert stilles Überschreiben; bei Namenskollision wird ein Zeitstempel
angehängt.

**Deployment:** `systemd/nuc-ha/scan-mover.{service,timer}`, Intervall 60 s.

---

## Befund 2 — OCR lief auf Englisch

### Symptom

Auffällig war eine Zeile im Paperless-Log:

```
[DEBUG] [paperless.parsing.tesseract] Calling OCRmyPDF with args: {..., 'language': 'eng', ...}
```

`PAPERLESS_OCR_LANGUAGE` war nirgends gesetzt. Paperless-ngx fällt dann auf `eng` zurück —
auch wenn `deu` im Image vorhanden ist (`tesseract --list-langs` zeigte
`deu eng fra ita osd spa`).

### Auswirkung

Deutsche Belege wurden ohne Umlaute erkannt. Der Schaden reicht weiter als Kosmetik: Er
trifft jede nachgelagerte Stufe, weil das LLM auf diesem Text arbeitet und Paperless
darauf sucht.

Ein reales Beispiel — derselbe Doppelname, vor und nach der Umstellung (anonymisiert;
Tesseract las `i` als `l`):

```
eng:  ... Mueller-Schmldt , <Vorname> , ...      ← Volltextsuche findet den Namen nicht
deu:  ... Müller-Schmidt , <Vorname> , ...
```

Ein weiteres, an einem Behördenformular:

```
eng:  Anschrift der inlandischen juristischen Person
deu:  Anschrift der inländischen juristischen Person
```

### Nachweis

Der sauberste Beleg ergab sich aus den 25 nachgeholten Scans: Sie wurden nacheinander
konsumiert, während mitten im Lauf die OCR-Sprache umgestellt wurde. Die Dokument-IDs
folgen der Konsum-Reihenfolge, gezählt wurden die Umlaute im erkannten Text:

```
   ID  Zeichen  Umlaute
 1496     1382        0   ┐
 1497    16987        0   │ OCR-Sprache: eng
 1500     9038        0   │
 1501     3880        0   ┘
 1502     5237       43   ┐
 1503     2519       17   │ OCR-Sprache: deu
 1505    15607      235   │
 1513    15716      156   ┘
```

Der Umschaltpunkt ist exakt an der erwarteten Stelle sichtbar. Das ist kein Indiz,
sondern ein Beweis.

### Lösung

```bash
kubectl -n <ns> set env deploy/paperless PAPERLESS_OCR_LANGUAGE=deu
```

Bei gemischtsprachigen Beständen ist `deu+eng` sinnvoll — dann zuerst die häufigste
Sprache nennen. Mehrere Sprachen kosten OCR-Laufzeit.

### Bestehende Dokumente nachträglich neu erkennen

Paperless-ngx bringt dafür ein Management-Kommando mit. Es erzeugt die Archivfassung neu
**und aktualisiert den Textinhalt**:

```bash
python manage.py document_archiver -f -d <DOCUMENT_ID> --no-progress-bar
```

Ohne `-d` läuft es über den gesamten Bestand — bei großen Archiven sehr teuer, deshalb
besser gezielt auf betroffene IDs.

> **Grenze:** Dokumente ohne maschinenlesbaren Text (Unterschriften, Fotos, handschriftliche
> Notizen) bleiben auch nach der Neu-OCR leer. paperless-ai überspringt sie mit
> `has no content, skipping analysis` — das ist korrekt und kein Fehler.

---

## Befund 3 — `RESTRICT_TO_EXISTING_TAGS` war wirkungslos (Upstream-Bug)

Dies ist der interessanteste Befund, weil die Konfiguration korrekt aussah und die
Software keinerlei Fehler meldete.

### Symptom

Trotz `RESTRICT_TO_EXISTING_TAGS=yes` vergab das Modell Tags erkennbar „aus dem Bauch":
Es traf vorhandene Tags nur zufällig, und die Trefferquote war schlecht. Gleichzeitig
wuchsen Korrespondenten und Dokumenttypen ungebremst (im untersuchten Bestand
617 Korrespondenten und 389 Dokumenttypen auf 1445 Dokumente).

### Analyse

paperless-ai spielt die Bestandslisten **nur über Platzhalter** in den System-Prompt ein.
Ohne `%RESTRICTED_TAGS%` im eigenen Prompt sieht das Modell nie eine Tag-Liste:

```js
// services/ollamaService.js — _buildPrompt()
systemPrompt = RestrictionPromptService.processRestrictionsInPrompt(
    systemPrompt, existingTags, correspondentList, existingDocumentTypes, config
);
```

Das allein ist bereits eine Falle: Wer den mitgelieferten Prompt durch einen eigenen
ersetzt, verliert die Platzhalter — und damit die Funktion — **ohne Warnung**.

Doch das Einsetzen des Platzhalters genügt nicht. Der Aufrufer übergibt ein
**String-Array**:

```js
// server.js
const existingTagNames = existingTags.map(tag => tag.name);   // ← Strings
...
const result = await processDocument(doc, existingTagNames, ...);
```

Der Formatierer erwartet dagegen **Objekte**:

```js
// services/restrictionPromptService.js — Original
static _formatTagsList(existingTags) {
    if (!Array.isArray(existingTags) || existingTags.length === 0) return '';
    return existingTags
      .filter(tag => tag && tag.name)   // ← wirft jeden String weg
      .map(tag => tag.name)
      .join(', ');
}
```

`"Rechnung".name` ist `undefined`, der Filter entfernt also **jeden** Eintrag.
`_formatTagsList` liefert den Leerstring, `%RESTRICTED_TAGS%` wird durch nichts ersetzt.

Dass es sich um einen Bug und nicht um Absicht handelt, zeigt die Schwesterfunktion
in derselben Datei — sie behandelt beide Formen korrekt:

```js
static _formatCorrespondentsList(existingCorrespondentList) {
    ...
    return existingCorrespondentList
      .filter(Boolean)
      .map(correspondent => {
        if (typeof correspondent === 'string') return correspondent;   // ← hier schon richtig
        return correspondent?.name || '';
      })
      .filter(name => name.length > 0)
      .join(', ');
}
```

### Warnung

Wer `%RESTRICTED_TAGS%` in den Prompt schreibt, ohne den Bug zu beheben, erhält eine
Anweisung der Form:

```
ERLAUBTE TAGS - vergib ausschliesslich Tags aus dieser Liste:
```

— gefolgt von **nichts**. Das ist schlechter als der Ausgangszustand, weil das Modell
angewiesen wird, aus einer leeren Menge zu wählen. Beide Änderungen gehören zusammen.

### Lösung

`patches/restrictionPromptService.js` spiegelt die Logik der Korrespondenten-Funktion.
Der Patch wird als ConfigMap über die Originaldatei gemountet, überlebt damit
Container-Neustarts und `imagePullPolicy: Always`:

```bash
kubectl -n <ns> create configmap paperless-ai-patch \
  --from-file=restrictionPromptService.js=patches/restrictionPromptService.js
```

```yaml
volumeMounts:
  - name: patch
    mountPath: /app/services/restrictionPromptService.js
    subPath: restrictionPromptService.js
    readOnly: true
```

### Wirkungsnachweis

`ollamaService` protokolliert die Prompt-Größe. Vor und nach dem Patch, gleicher Bestand
(444 Tags ≈ 2360 Tokens):

```
vorher:   Prompt Token Count: 1321      Dynamic calculated num_ctx: 2367
nachher:  Prompt Token Count: 3696      Dynamic calculated num_ctx: 4720
```

Zusätzlich direkt gegen die gepatchte Funktion geprüft:

```
$ node -e 'const R=require("/app/services/restrictionPromptService.js");
           console.log(R.processRestrictionsInPrompt("Tags: %RESTRICTED_TAGS%",
                       ["Rechnung","Vertrag","steuerjahr:2025"], [], {}))'
Tags: Rechnung, Vertrag, steuerjahr:2025
```

### Nebenbefund

Die Signatur passt nicht zum Aufruf — fünf Argumente, vier Parameter:

```js
static processRestrictionsInPrompt(prompt, existingTags, existingCorrespondentList, config)
```

`config` erhält damit die Dokumenttypen-Liste. Folgenlos, weil `config` im Rumpf ungenutzt
ist, aber ein Hinweis darauf, dass dieser Codepfad wenig Aufmerksamkeit bekommen hat.

---

## Befund 4 — `TOKEN_LIMIT` über dem Modellkontext

`TOKEN_LIMIT` steuert bei paperless-ai zweierlei: die Kürzung des Dokumentinhalts **und**
die Obergrenze für das an Ollama gesendete `num_ctx`:

```js
_calculateNumCtx(promptTokenCount, expectedResponseTokens) {
    const totalTokenUsage = promptTokenCount + expectedResponseTokens;
    const maxCtxLimit = Number(config.tokenLimit);
    return Math.min(totalTokenUsage, maxCtxLimit);
}
```

Konfiguriert war `TOKEN_LIMIT=128000`. Das verwendete Modell kann 32768:

```bash
$ curl -s http://<ollama>:11434/api/show -d '{"model":"<modell>"}' | jq '.model_info | with_entries(select(.key|test("context_length")))'
{ "qwen2.context_length": 32768 }
```

Bei langen Dokumenten wird damit ein `num_ctx` jenseits des trainierten Fensters
angefordert. Ollama alloziert den KV-Cache trotzdem — das kostet Speicher und die
Ausgabequalität bricht ein.

**Regel:** `TOKEN_LIMIT` ≤ `context_length` des Modells. Hier auf `32000` gesetzt.

---

## Befund 5 — Ollama-Blockade ohne Timeout

### Symptom

paperless-ai lief, antwortete auf HTTP, aber es tauchte nie wieder ein
`Starting scheduled scan` im Log auf. Die letzte Zeile war stets:

```
Validating Paperless config for: http://.../api/documents/
AI provider: ollama
                                    ← und dann nichts mehr
```

### Analyse

Der Cron wird erst **nach** einer erfolgreichen Validierung registriert:

```js
async function startScanning() {
    const isConfigured = await setupService.isConfigured();   // ← validiert u. a. Ollama
    ...
    if (config.disableAutomaticProcessing != 'yes') {
        await scanInitial();
        cron.schedule(config.scanInterval, async () => { ... });   // ← erst hier
    }
}
```

Und die Validierung ruft Ollama **ohne Timeout**:

```js
async validateOllamaConfig(url, model) {
    try {
        const response = await axios.post(`${url}/api/generate`, {
            model: model || 'llama3.2', prompt: 'Test', stream: false
        });                       // ← kein timeout, kein AbortSignal
        return response.data && response.data.response;
    } catch (error) { ... }
}
```

Antwortet Ollama nicht, wartet paperless-ai **unbegrenzt**. Es gibt keinen Fehler, keinen
Neustart, keinen Scan. Der Prozess wirkt gesund: Der Express-Server läuft, ein HTTP-Health-Check
ist grün. Eine Kubernetes-`livenessProbe` auf `/` hätte diesen Zustand nicht erkannt.

### Warum Ollama blockierte

Zwei Ursachen, die sich gegenseitig verstärkten:

1. **Modell-Karussell.** Eine andere Anwendung auf demselben Ollama hielt ein 14B-Modell
   mit `keep_alive=30m` im VRAM (22 GB von 24 GB). paperless-ai forderte ein anderes
   Modell an. Ollama kann es nicht daneben laden und stellt die Anfrage in eine Warteschlange —
   ohne Rückmeldung. Innerhalb von 30 Minuten zählte das Log **72 Modell-Ladevorgänge**:
   die Clients warfen sich gegenseitig aus dem Speicher.

2. **Speichernot.** Modelle, die nicht ins VRAM passen, laufen teilweise im System-RAM.
   Auf einem Host mit 15 GB RAM und `OLLAMA_MAX_LOADED_MODELS=3` genügte das für zwei
   globale OOM-Ereignisse an einem Tag:

   ```
   oom-kill:constraint=CONSTRAINT_NONE,...,global_oom,task_memcg=/system.slice/ollama.service,task=llama-server
   Out of memory: Killed process (llama-server) total-vm:110887672kB, anon-rss:7218084kB
   ```

   Danach war der Host in einem tückischen Zustand: Er antwortete auf Ping, TCP-Handshakes
   kamen zustande (der Kernel lebte), aber **kein einziger Userspace-Prozess** reagierte —
   weder SSH noch Ollama. Ein Reboot war nur über die Stromversorgung möglich.

### Lösung

Der eleganteste Fix kostet keine Zeile Code: **dasselbe Modell verwenden wie der andere
Client.** Dann entfällt der Modellwechsel, das Modell bleibt geladen, es gibt keine
Verdrängung und keinen RAM-Überlauf. Als angenehme Nebenwirkung folgt das größere Modell
den Prompt-Anweisungen zuverlässiger.

```bash
kubectl -n <ns> set env deploy/paperless-ai OLLAMA_MODEL=<gemeinsames-modell>
```

> **Fallstrick:** paperless-ai lädt seine `.env` mit `dotenv.config({ path })` — **ohne**
> `override`. Steht `OLLAMA_MODEL` bereits in der Container-Umgebung (z. B. über
> `envFrom.secretRef`), gewinnt diese und die `.env`-Änderung bleibt wirkungslos.
> In Kubernetes hat ein explizites `env` Vorrang vor `envFrom` — dort ansetzen.
> Kontrolle: `kubectl exec <pod> -- printenv OLLAMA_MODEL`

Ergänzend wurde der LLM-Host abgesichert (nächster Abschnitt), damit ein einzelner
Modelllauf nicht mehr die ganze Maschine mitreißt.

---

## Befund 6 — Paperless' eigenes Tag-Matching war abgeschaltet

### Symptom

Ein Kontoauszug, der den Namen der betreffenden Person **fünfmal wörtlich** enthält,
bekam den zugehörigen Personen-Tag nicht. Der System-Prompt beschrieb die Regel
unmissverständlich („Tag X nur, wenn einer dieser Begriffe wörtlich vorkommt").
Das Modell hielt sich trotzdem nicht daran.

### Analyse

Zwei getrennte Ursachen — und beide zeigen, dass hier auf das falsche Werkzeug gesetzt wurde.

**a) 442 von 444 Tags hatten `matching_algorithm = "any word"` mit leerem `match`-Feld.**
Ohne Suchbegriffe trifft dieses Verfahren nie. Paperless' eingebautes, deterministisches
Matching war damit faktisch deaktiviert.

**b) Die beiden verbliebenen Regex-Regeln waren doppelt escaped** und trafen ebenfalls nichts:

```python
>>> gespeichert = r'(?i)(\\bsteuer(?:jahr)?[_\\-\\s]*2025\\b|...)'
>>> re.search(gespeichert, "Rechnung 2025")
None                                  # \\b = Backslash gefolgt von 'b', nicht Wortgrenze
>>> re.search(gespeichert.replace('\\\\','\\'), "Rechnung 2025")
<re.Match ...>                        # einfach escaped: Treffer
```

Solche Regeln scheitern **stumm**. In der Oberfläche sieht die Regex korrekt aus, es gibt
keine Fehlermeldung, und der Tag wird trotzdem nie automatisch vergeben. Wer nicht misst,
merkt es nie.

### Lösung — die richtige Aufgabenteilung

Ein LLM ist ein schlechter Regel-Interpreter. Es *kann* „vergib Tag X nur bei Begriff Y"
befolgen, aber es tut es nicht zuverlässig — und Zuverlässigkeit ist bei einer
deterministischen Regel der ganze Punkt.

> **Deterministisches gehört in Paperless-Regeln. Das LLM ist für das Unscharfe da.**

Konkret: Tags, die an einem wörtlichen Merkmal hängen (Namen, Kontonummern, Jahreszahlen,
Absender), werden als Regex-Regel hinterlegt. Paperless wendet sie **bei jeder
Konsumierung automatisch** an — ohne Modell, ohne Token, ohne Zufall.

```bash
curl -X PATCH -H "Authorization: Token $TOKEN" -H 'Content-Type: application/json' \
  -d '{"matching_algorithm":4,"match":"(Nachname-A|Vorname\\s+Nachname-B|Strassenname)","is_insensitive":true}' \
  http://<paperless>/api/tags/<id>/
```

`matching_algorithm`: `0` keine · `1` any word · `2` all words · `3` literal · `4` regex ·
`5` fuzzy · `6` auto (ML-Klassifizierer)

**Rückwirkend auf den Bestand anwenden:**

```bash
python manage.py document_retagger -T --suggest --no-progress-bar   # Trockenlauf
python manage.py document_retagger -T --no-progress-bar             # anwenden
```

> **`-f`/`--overwrite` nicht verwenden**, solange die meisten Tags keine Regeln haben:
> Das Flag **entfernt** alle Tags, die nicht mehr auf eine Regel passen — also praktisch
> den gesamten manuell oder per Import vergebenen Bestand. Ohne `-f` wird nur hinzugefügt.

### Greift die Regel neben paperless-ai?

Ja. `paperlessService.updateDocument()` mischt die Tags, statt sie zu ersetzen:

```js
const combinedTags = [...new Set([...currentDoc.tags, ...updates.tags])];
```

Reihenfolge im Betrieb: Paperless setzt beim Konsumieren die Regel-Tags, paperless-ai
ergänzt später seine eigenen. Nichts geht verloren.

### Nachweis

Ein erzeugtes Test-PDF mit dem Trigger-Begriff im Text wurde in den Scanner-Share gelegt
und durchlief die komplette Kette. Ergebnis nach der Konsumierung, **bevor** paperless-ai
das Dokument überhaupt gesehen hatte:

```
#1516  REGELTEST   Tags: ['<Personen-Tag>']
```

Rückwirkend fügte `document_retagger -T` den Tag auf 23 weiteren Bestandsdokumenten hinzu.

### Ergänzend: Nützt die Tag-Liste im Prompt überhaupt?

Der Patch aus [Befund 3](#befund-3--restrict_to_existing_tags-war-wirkungslos-upstream-bug)
macht die Bestandsliste für das Modell sichtbar. Ob das die Qualität hebt, wurde nicht
geglaubt, sondern gemessen — identischer Inhalt, identische Sampling-Parameter, einmal mit
und einmal ohne Liste im System-Prompt:

```
--- Dokument A (Aufhebungsvertrag)
   ohne Liste: ['steuerjahr:2026']                     → 1 gültig
   mit  Liste: ['steuerjahr:2026', 'PersonA']           → 2 gültig
--- Dokument B (Mitteilung Finanzverwaltung)
   ohne Liste: ['PersonA']                             → 1 gültig
   mit  Liste: ['PersonA', 'steuerjahr:2025']           → 2 gültig
--- Dokument C (Jahresbericht)
   ohne Liste: ['PersonA']                             → 1 gültig
   mit  Liste: ['PersonA', 'ordner/.../Behörden']       → 2 gültig

Summe: ohne Liste 3/3 gültig · mit Liste 6/6 gültig
```

Die Liste verdoppelt die Zahl brauchbarer Vorschläge, ohne Ausschuss zu erzeugen — sie
bleibt aktiv. **Bemerkenswert:** In *keinem* der Läufe vergab das Modell den Personen-Tag,
obwohl der Name im Text stand. Das ist kein Argument gegen die Liste, sondern für die
Regel — und die beste Begründung für die Aufgabenteilung oben.

---

## Härtung des LLM-Hosts

### 1. Speichergrenze für Ollama (cgroup)

Ohne Limit kann ein ins RAM ausgelagertes Modell den gesamten Host in einen globalen OOM
treiben. Mit Limit stirbt nur der Dienst und wird neu gestartet.

```ini
# systemd/ki02/ollama-10-memory-guard.conf
[Service]
MemoryHigh=11G
MemoryMax=12G
OOMPolicy=continue     # llama-server darf sterben, ohne den Dienst zu stoppen
Restart=always
RestartSec=5
```

> **Wichtig:** `memory.current` eines cgroups zählt auch den **Page-Cache** der
> Modell-Blobs mit. Ein zu knappes `MemoryHigh` führt daher zu ständigem Cache-Reclaim
> und damit zu wiederholtem Nachladen der Modelldateien von der Platte. Genügend Luft
> lassen und live gegenprüfen:
>
> ```bash
> cat /sys/fs/cgroup/system.slice/ollama.service/memory.{max,high,current}
> ```

### 2. `earlyoom` als Netz für alles Übrige

Greift, bevor der Kernel-OOM den Host ins Thrashing schickt.

```
EARLYOOM_ARGS="-m 6,3 -s 100,50 -r 60
               --avoid '(^|/)(systemd|sshd|dbus-daemon|nvidia-persistenced)$'
               --prefer '(^|/)(llama-server|ollama)$'"
```

`--avoid` schützt den Weg zurück auf die Maschine (`sshd`!), `--prefer` opfert zuerst die
LLM-Prozesse.

### 3. Auto-Reboot bei totalem Freeze

Der Board-Watchdog wäre die saubere Lösung, ist auf dieser Hardware aber vom BIOS gesperrt:

```
iTCO_wdt iTCO_wdt.1.auto: unable to reset NO_REBOOT flag, device disabled by hardware/BIOS
```

Ersatz ist `softdog`. Er genügt für den beobachteten Fehlerfall — der Kernel lebte, nur
der Userspace stand.

```ini
# systemd/ki02/systemd-10-watchdog.conf
[Manager]
RuntimeWatchdogSec=120     # 120 s statt 60 s: keine Fehlalarme bei Lastspitzen
RebootWatchdogSec=5min
```

```bash
echo softdog > /etc/modules-load.d/softdog.conf
systemctl daemon-reexec
# Kontrolle: journalctl -b | grep -i watchdog
#   systemd[1]: Using hardware watchdog 'Software Watchdog', device /dev/watchdog0
```

> `softdog` schützt **nicht** gegen einen echten Kernel-Hänger — dafür braucht es einen
> Hardware-Watchdog. Wenn das BIOS ihn erlaubt, ist `iTCO_wdt` vorzuziehen.

### 4. Dienst-Watchdog für Ollama

Für den häufigeren Fall, dass nur Ollama klemmt und der Host gesund ist. Als Sonde dient
`/api/ps`: billig, lädt kein Modell — und hing im Störfall genauso wie `/api/generate`.

```bash
# scripts/ki02/ollama-watchdog.sh (Auszug)
if curl -sf -m 20 -o /dev/null http://127.0.0.1:11434/api/ps; then
    rm -f "$STATE"; exit 0
fi
fails=$(( $(cat "$STATE" 2>/dev/null || echo 0) + 1 ))
echo "$fails" > "$STATE"
[ "$fails" -ge 3 ] && { systemctl restart ollama.service; rm -f "$STATE"; }
```

Timer alle 2 Minuten, Auslösung nach 3 aufeinanderfolgenden Fehlschlägen (≈ 6 Minuten),
damit ein einzelner langer Modell-Ladevorgang keinen Neustart provoziert.

---

## Verifikation

Jede Änderung wurde am laufenden System gegengeprüft, nicht nur ausgerollt.

**Scanner-Strecke, end-to-end.** Eine erzeugte Test-PDF wurde in den Samba-Share gelegt,
vom Timer verschoben, von Paperless konsumiert und anschließend wieder gelöscht:

```
/srv/scanner: 1 → 0    consume: 0 → 1 → 0    Dokumente: 1444 → 1445 → 1444
```

**Rückstand.** Alle 25 liegengebliebenen Scans wurden konsumiert (1420 → 1445 Dokumente),
`/srv/scanner` ist leer.

**OCR-Sprache.** Im laufenden Betrieb gegengelesen:

```bash
$ kubectl exec <paperless-pod> -- tail -n 200 .../paperless.log | grep -oE "'language': '[a-z+]+'"
'language': 'deu'
```

**Tag-Injektion.** Prompt-Größe von 1321 auf 3696 Tokens gestiegen (siehe Befund 3).

**Modellwahl.** `kubectl exec <pod> -- printenv OLLAMA_MODEL` gegen die Pod-Spec geprüft —
nicht gegen die `.env`, die hier bewusst nicht maßgeblich ist.

**Ollama stabil.** `/api/ps` zeigt dauerhaft ein einziges geladenes Modell; die
Ladevorgänge im Log sind versiegt.

### Eine Warnung zur Methodik

Zwei plausible Hypothesen hielten der Messung **nicht** stand:

- *„Die vielen Tags aus dem Altsystem-Import sind Müll und verwirren das Modell."*
  Falsch — sie waren fachlich gewollt.

- *„Die literalen `\n` im System-Prompt verschlechtern die Anweisungsbefolgung."*
  Sie sind Upstream-Absicht (`routes/setup.js` escaped Zeilenumbrüche beim Speichern) und
  richteten messbar keinen Schaden an.

Ebenso hielt der Verdacht der **Über**vergabe eines Personen-Tags nicht: Eine Auszählung
gegen die im Prompt definierten Trigger-Begriffe ergab 110 von 116 Zuweisungen regelkonform.
Das tatsächliche Problem war die Gegenrichtung — 92 Dokumente, die einen Trigger-Begriff
wörtlich enthielten, trugen den Tag **nicht**. Genau diese Trefferquote adressiert der
Patch aus Befund 3.

**Erst messen, dann reparieren.** Eine überzeugende Erklärung ist kein Beweis.

---

## Repository-Inhalt

```
scripts/nuc-ha/scan-mover.sh              Scanner-Share → Paperless-Consume (Ersatz für scan-mover-Container)
scripts/ki02/ollama-watchdog.sh           Health-Check + Neustart von Ollama
scripts/ki02/earlyoom.default             earlyoom-Konfiguration
systemd/nuc-ha/scan-mover.{service,timer} Timer-Einheit, 60 s
systemd/ki02/ollama-10-memory-guard.conf  cgroup-Speichergrenzen für Ollama
systemd/ki02/systemd-10-watchdog.conf     softdog + RuntimeWatchdogSec
systemd/ki02/ollama-watchdog.{service,timer}
patches/restrictionPromptService.js       Fix für den leeren %RESTRICTED_TAGS%-Platzhalter
manifests/paperless.yaml                  Deployment inkl. PAPERLESS_OCR_LANGUAGE
manifests/paperless-ai.yaml               Deployment inkl. Modell-Override und Patch-Mount
manifests/paperless-ai-patch-configmap.yaml
```

Namespaces, Hostnamen und IP-Adressen in den Manifesten sind an die eigene Umgebung
anzupassen. Zugangsdaten enthält dieses Repository nicht — sie liegen in einem Secret,
auf das die Deployments per `envFrom` verweisen.

---

## Betriebs-Runbook

**Scans kommen nicht an**

```bash
systemctl status scan-mover.timer
journalctl -t scan-mover --since -1h
ls -1 <scanner-share> <consume-dir>
```

Liegen Dateien im Consume-Verzeichnis und verschwinden nicht, prüft man den Consumer:

```bash
kubectl exec <paperless-pod> -- tail -n 200 /usr/src/paperless/data/log/paperless.log \
  | grep -iE 'consum|duplicate|error'
```

Bleiben Dateien mit `It is a duplicate of …` liegen, ist das erwartetes Verhalten —
Paperless löscht sie nicht. Sie müssen von Hand weggeräumt werden, sonst laufen sie bei
jedem Poll erneut in den Fehler.

**paperless-ai verarbeitet nichts**

Zuerst prüfen, ob der Scan überhaupt startet:

```bash
kubectl logs <paperless-ai-pod> | grep -E 'Configured scan interval|Starting (initial|scheduled) scan'
```

Fehlt `Configured scan interval`, hängt der Start in der Ollama-Validierung. Gegenprobe —
und zwar mit `/api/generate`, nicht mit `/api/version`, denn letzteres antwortet auch bei
blockierter Inferenz:

```bash
curl -m 30 -X POST http://<ollama>:11434/api/generate \
     -d '{"model":"<modell>","prompt":"Test","stream":false}'
```

**Ollama blockiert**

```bash
curl -s http://<ollama>:11434/api/ps                 # welches Modell hält das VRAM?
journalctl -u ollama --since -30min | grep -c 'loaded model'   # Modell-Karussell?
journalctl -b -1 -k | grep -iE 'oom|killed process'            # OOM im letzten Boot?
```

Viele `loaded model`-Einträge bedeuten, dass sich mehrere Clients gegenseitig aus dem
Speicher werfen. Abhilfe: gemeinsames Modell, `OLLAMA_MAX_LOADED_MODELS` an die reale
VRAM-Kapazität anpassen, `keep_alive` senken.

**Ein Tag wird nicht vergeben, obwohl der Begriff im Dokument steht**

Prüfen, ob der Tag überhaupt eine Regel hat und ob sie greift:

```bash
curl -s -H "Authorization: Token $TOKEN" http://<paperless>/api/tags/<id>/ \
  | python3 -c 'import sys,json;t=json.load(sys.stdin);print(t["matching_algorithm"], repr(t["match"]))'
```

`1` mit leerem `match` bedeutet: kein Matching. `4` mit `\\b` statt `\b`: doppelt escaped,
trifft nichts. Regel setzen, dann `document_retagger -T --suggest` zum Trockenlauf.

**Nach Konfigurationsänderung an paperless-ai**

`.env` und Container-Umgebung können sich widersprechen. Maßgeblich ist immer:

```bash
kubectl exec <pod> -- printenv | grep -E 'OLLAMA_|TOKEN_LIMIT|RESTRICT_'
```

---

## Fallstricke

- **`kubectl exec` direkt nach einem Rollout** trifft womöglich noch den alten Pod. Immer
  gegen `.status.startTime` oder den Pod-Namen gegenprüfen — sonst misst man den Zustand
  vor der eigenen Änderung. (Genau das ist während dieser Fehlersuche passiert.)
- **`dotenv` überschreibt keine bestehenden Umgebungsvariablen.** Was aus `envFrom` kommt,
  gewinnt gegen die `.env`.
- **`TOKEN_LIMIT` ist kein reiner Kürzungsparameter**, sondern auch die Obergrenze für
  `num_ctx`.
- **Ein eigener `SYSTEM_PROMPT` deaktiviert stillschweigend die Restriktionsfunktion**,
  wenn die Platzhalter fehlen.
- **`/api/version` ist kein Health-Check für Ollama.** Es antwortet auch dann noch, wenn
  keine einzige Inferenz mehr durchgeht.
- **Ein HTTP-200 des paperless-ai-Servers bedeutet nicht, dass der Scan-Cron läuft.**
- **`document_archiver` ohne `-d` läuft über den gesamten Bestand.** Bei großen Archiven
  gezielt einzelne IDs angeben.
- **Verwaiste Prozesse tarnen sich als Systemlast.** Auf dem Cluster-Host lief ein
  vergessener `ugrep` seit elf Tagen mit über 500 % CPU und trug maßgeblich zu einem
  node-weiten OOM bei. `ps -eo pcpu,etime,args --sort=-pcpu | head` gehört in jede
  Erstdiagnose.
- **Ein Tag mit `matching_algorithm: any word` und leerem `match` matcht nie.** Das ist
  der Auslieferungszustand vieler importierter Tags und sieht in der Oberfläche unauffällig aus.
- **Doppelt escapte Regex-Regeln scheitern stumm.** `\\b` ist keine Wortgrenze, sondern ein
  Backslash gefolgt von `b`. Immer gegen einen echten Dokumenttext gegenprüfen, nie gegen
  die Anzeige vertrauen.
- **`document_retagger -f` entfernt Tags**, die auf keine Regel mehr passen. Bei Beständen
  mit überwiegend regellosen Tags ist das ein Datenverlust.
- **Ein LLM ist kein Regel-Interpreter.** Was sich als Regex ausdrücken lässt, gehört als
  Paperless-Regel hinterlegt — nicht in den System-Prompt.

---

## Upstream-Meldungen

Zwei Befunde betreffen [`clusterzx/paperless-ai`](https://github.com/clusterzx/paperless-ai)
und sollten dort gemeldet werden:

1. **`_formatTagsList()` verwirft String-Arrays** (`services/restrictionPromptService.js`).
   `server.js` übergibt `existingTagNames` (Strings), der Filter `tag => tag && tag.name`
   entfernt sie alle. Folge: `%RESTRICTED_TAGS%` bleibt leer, `RESTRICT_TO_EXISTING_TAGS`
   ist wirkungslos. Die Schwesterfunktion `_formatCorrespondentsList()` behandelt beide
   Formen bereits korrekt und dient als Vorlage. Betrifft alle AI-Provider, die
   `RestrictionPromptService` nutzen. Fix: `patches/restrictionPromptService.js`.

2. **`validateOllamaConfig()` setzt kein Timeout** (`services/setupService.js`).
   `axios.post(...)` ohne `timeout`/`AbortSignal` blockiert `startScanning()` unbegrenzt,
   wenn Ollama nicht antwortet. Der Cron wird nie registriert, der Prozess wirkt gesund.
   Ein `timeout` von einigen Sekunden plus aussagekräftige Log-Meldung würde genügen.

Kleinerer Nebenbefund: `processRestrictionsInPrompt()` wird mit fünf Argumenten bei vier
Parametern aufgerufen (`ollamaService.js`); der Parameter `config` empfängt dadurch die
Dokumenttypen-Liste. Derzeit folgenlos, da im Rumpf ungenutzt.

---

## Lizenz

Die Skripte und der Patch stehen unter der MIT-Lizenz. `patches/restrictionPromptService.js`
ist eine abgeleitete Fassung einer Datei aus `clusterzx/paperless-ai` und unterliegt der
Lizenz des Ursprungsprojekts.
{% endraw %}
