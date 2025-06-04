import re
from datetime import datetime, timedelta
import shutil

log_file = "log.txt"
backup_file = f"log_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
tmp_file = "log_neu.txt"

# Backup erstellen
shutil.copyfile(log_file, backup_file)

cutoff = datetime.now() - timedelta(days=14)
pattern = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]")

keep = False
block = []
output = []

with open(log_file, "r", encoding="utf-8") as f:
    for line in f:
        match = pattern.match(line)
        if match:
            if keep and block:
                output.extend(block)
            timestamp = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
            keep = timestamp >= cutoff
            block = [line]
        else:
            block.append(line)

# Letzten Block prüfen
if keep and block:
    output.extend(block)

# Neue Datei schreiben
with open(log_file, "w", encoding="utf-8") as f:
    f.writelines(output)
