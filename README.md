## Planet Conqueror - try this game [here](https://gitmanik.github.io/PlanetConqueror/)!

<p align=center>
<table>
<tr>
<td>
<img src="Screenshots/Screenshot2.png" height=700px>
</td>
<td>
<img src="Screenshots/Screenshot1.png" height=700px>
</td>
</tr></table>
</p>

**Planet Conqueror** is a Python game built using **Pygame**, inspired by the mobile game *Cell Expansion Wars*.  
The action takes place in outer space, where players conquer planets, launch satellites, and send units between worlds using upgradeable rockets.

The gameplay blends both **real-time** and **turn-based** mechanics, creating a unique and strategic experience.  
Levels are **procedurally generated**, ensuring a fresh challenge every time you play.

## How to play

- **Click on your planet** (green), then **click on an enemy or neutral (gray) planet** to create a connection and send units.
- **Drag a card** onto one of your planets to activate its effect.

Use quick thinking and tactical moves to outmaneuver your opponent and take over the galaxy!


## Used graphics
- [Kenney Planets](https://kenney.nl/assets/planets)
- [Kenney Space Shooter Extension](https://kenney.nl/assets/space-shooter-extension)
- [Kenney Future Narrow Font](https://kenney.nl/assets/kenney-fonts)
- [Kenney Playing Cards Pack](https://kenney.nl/assets/playing-cards-pack)

## Used libraries
- Pygame
- Pygbag
- Pygbag.net

## Building and packaging via Pygbag
```bash
pip install -r requirements.txt
pygbag --ume_block 0 --build ExpansionWar/ 
```

## Building and running locally
``` bash
pip install -r requirements.txt
cd ExpansionWar
python3 main.py
```
