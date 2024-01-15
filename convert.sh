#!/bin/bash

for i in *.mp3;
  do name=`echo "$i" | cut -d'.' -f1`
  echo "$name"
  ffmpeg -i "$i" -ac 2 -f wav "${name}.wav"
done