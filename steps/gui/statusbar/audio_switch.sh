#!/bin/sh

# LMB - print info
[ "$BUTTON" = "1" ] && {
    notify-send "🎛️ Current sink" "$(pamixer --get-default-sink | grep -oE "\"[^\"]+\"$" | tr -d \")"
    notify-send "🎛️ Available sinks" "$(pamixer --list-sinks | grep -oE "\"[^\"]+\"$" | tr -d \" | sed "s/^/ - /g")"
}

# RMB - switch audio output
[ "$BUTTON" = "3" ] && {
    current_sink="$(pamixer --get-default-sink | grep -oE "^[0-9]+")"
    next=$( (pamixer --list-sinks; pamixer --list-sinks) | # List sinks two times, so the list wraps around after last sink
        grep -vE "Sinks|Built-in|Virtual"                | # Remove unneeded lines
        grep -m1 -A1 -E "^$current_sink"                 | # Find first occurrence of our current sink and also print one line below
        tail -1                                          | # Take only line below, which is our next sink
        cut -d' ' -f1)                                     # Extract index of the sink
    [ -z "$next" ] && next="0"
    pacmd set-default-sink "$next"
}

# Print icon
icon=""
(pamixer --get-default-sink | grep -q  "USB") && icon=""
(pamixer --get-default-sink | grep -qE "HDMI|VGA") && icon=""
printf "$icon"
