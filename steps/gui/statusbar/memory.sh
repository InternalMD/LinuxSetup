#!/bin/sh

[ "$BUTTON" = "1" ] && notify-send "🧠 Memory intensive processes" "$(ps axch -o cmd:15,%mem --sort=-%mem | head -10 | xargs -I{} printf "%s%%\n" "{}")"

free  | awk 'NR == 2 { printf(" %dMiB used", ($3/1024)) }'
