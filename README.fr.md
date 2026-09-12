# Video Clip Compressor

[![lang - EN](https://img.shields.io/badge/lang-EN-d5372d?style=for-the-badge)](README.md)
[![lang - FR](https://img.shields.io/badge/lang-FR-2d3181?style=for-the-badge)](README.fr.md)

Ce programme sert a compresser vers une taille spécifique des vidéos courtes pour les envoyer sur *certaines* plateformes. 

## Dépendances
- [pymediainfo](https://github.com/sbraz/pymediainfo)
- [FFMPEG](https://ffmpeg.org/) (voir [NOTICE](./NOTICE))
- [PySide6](https://wiki.qt.io/Qt_for_Python) (voir [NOTICE](./NOTICE))

# Utilisation
## CLI
| Paramètre              | Valeur par défaut | Valeurs possibles                           | Explication                                  |
| ---------------------- | ----------------- | ------------------------------------------- | -------------------------------------------- |
| `-i` `--input`         |                   |                                             | Chemin de fichier de la vidéo d'entrée       |
| `-o` `--output`        |                   |                                             | Chemin de fichier de la vidéo de sortie      |
| `-t` `--target`        | `20`              | `0 < Any`                                   | Taille cible en Mo                           |
| `-f` `--framerate`     | Pas utilisé       |                                             | Utiliser une plus haute fréquence d'images   |
| `-r` `--resolution`    | `1280:720`        | `Any` (voir la doc libx264 et/ou libsvtav1) | Définir la résolution de sortie              |
| `-c` `--compatibility` | Pas utilisé       |                                             | Utiliser des codecs plus anciens (h264, aac) |
| `-p` `--preview`       | Pas utilisé       |                                             | Prévisualise les paramètres                  |
| `-y` `--overwrite`     | Pas utilisé       |                                             | Écrase le fichier de sortie si il existe     |


### Examples
Encoder une vidéo `source.mov` vers une vidéo `compressee.mkv` en 720p60 avec de la vidéo h264 et de l'audio aac, ciblant la taille de sortie par défaut.
```bash
$ uv run .\src\cli.py -i source.mov -o compressee.mkv -f -c
```
---

Encoder une vidéo `clip.mp4` vers une vidéo `clip_compresse.mkv` en 1080p30 avec de la vidéo AV1 et de l'audio opus, ciblant 50Mo.
```bash
$ uv run .\src\cli.py -i clip.mp4 -o clip_compresse.mkv -r 1920:1080 -t 50
```
---

Prévisualisation des paramètres d'encodage d'une vidéo `clip.mp4` vers une vidéo `clip_compressed.mkv` en 540p30 avec de la vidéo AV1 et de l'audio opus, ciblant 50Mo.
```bash
$ uv run .\src\cli.py -i clip.mp4 -o clip_compressed.mkv -r 960:540 -t 50 
==================== Preview =====================
File paths
    Input path           : clip.mp4
    Output path          : clip_compressed.mkv
Video settings
    Resolution           : 960:540
    Duration             : 10 s
    Framerate            : 30 fps
    Target size          : 50 MB
    Enable compatibility : False
FFMPEG Commands
    First pass           : ffmpeg -y -i clip.mp4 -c:v libsvtav1 -preset 6 -svtav1-params rc=2:pred-struct=1:tbr=16220k -passlogfile . -r 30 -vf scale=960:540 -pass 1 -an -f null NUL
    Second pass          : ffmpeg -y -i clip.mp4 -c:v libsvtav1 -preset 6 -svtav1-params rc=2:pred-struct=1:tbr=16220k -passlogfile . -r 30 -vf scale=960:540 -pass 2 clip_compressed.mkv
==================================================
```

### GUI
Je suis sur que tu peux t'en sortir sans aide..\
![Interface sur windows 10](./win10_interface.png)