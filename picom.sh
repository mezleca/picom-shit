#!/usr/bin/env bash

# notes:
# idk if my daemon method sucks but when i try to start this with i3
# it simply doenst work at all
# so i have to start it manually

# toggle-picom.sh — disable picom on fullscreen,
# deps: xprop, pgrep, pkill, picom

picom_disabled=false

is_fullscreen() {

  raw=$(xprop -root _NET_CLIENT_LIST 2>/dev/null) || return 1
  ids=$(echo "$raw" | sed -e 's/^.*# //' -e 's/,/ /g')
  
  for id in $ids; do
    if xprop -id "$id" _NET_WM_STATE 2>/dev/null \
       | grep -q "_NET_WM_STATE_FULLSCREEN"; then
      return 0
    fi
    
  done
  return 1
}

while true; do

  if is_fullscreen; then
  	# disable picom on fullscreen
    if pgrep -x picom >/dev/null; then
    
      pkill picom
      picom_disabled=true
      echo "$(date +'%T'): disabled picom"
    fi
  else
  	# if the script disabled picom before and picom is not active
  	# enabled it again?
  	# prob wont work for custom configs btw
    if $picom_disabled && ! pgrep -x picom >/dev/null; then
      picom &>/dev/null &
      picom_disabled=false
      echo "$(date +'%T'): enabled picom again"
    fi
  fi

  # 2ms? 2seconds? idk too lazy to serach  
  sleep 2
done
