[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

# gdr
A program for playing background music of your choice offline on your PC.<br>
**Only supports .mp3!**

## Quick Start

### Requirements

- [Pygame](https://pygame.org/) (`pip3 install pygame --pre`)
> --pre is recommended for installing a newer version of SDL to fix the broken rewinding of some .mp3 files.
- [mutagen](https://github.com/quodlibet/mutagen) (`pip3 install mutagen`)
- [easing-functions](https://github.com/semitable/easing-functions) (`pip3 install easing-functions`)
- [pywin32](https://pypi.org/project/pywin32/) (`pip3 install pywin32`)
- [PyAutoGUI](https://github.com/asweigart/pyautogui) (`pip3 install pyautogui`)
- [pypresence](https://github.com/qwertyquerty/pypresence) (`pip3 install pypresence`)
- [NumPy](https://numpy.org/) (`pip3 install numpy`)


### Running

Download the project and run the `main.pyw` file
```bash
git clone https://github.com/moontr3/gdr.git
cd gdr
python3 main.pyw
```

Note that the program won't run if there is no songs in your folder or the folder is missing.


### Configuring

*Almost* every property needs to be configured in the `data.json` file, which will appear automatically when the app is first ran.

| Key | Description |
|-----|-----|
| `folder` | Path to the folder with your song files. To load subtitles, create a `subtitles` folder inside of the songs folder and put your `json` files there. |
| `client_id` | Required when `discord_presence` is `true`. Name of the chosen Discord app will be displayed as a title of the presence in your profile. |
| `discord_presence` | Used for enabling or disabling Discord Rich Presence function. |
| `presence_image` | A link to the image that will appear on your profile. Leave blank to remove the image. |
| `presence_description` | Text that will appear on your profile. Leave blank to remove the text. |
| `fav_boost` | How more often your favorite songs will be chosen. Set to 0 for no boosting. |
| `remember_last_song` | **Can be edited through the app.** <br> Used for choosing whether the currently playing song will be chosen after restart. |
| `song` | **Doesn't need to be configured.** <br> Currently playing song. Used for remembering the last played song. |
| `next_song` | **Doesn't need to be configured** <br> The song that was supposed to be played next. |
| `boosted` | **Can be edited through the app.** <br> A list of your favorite song names. Song names correspond to their filenames. |


### Navigating

> In order to press the buttons the program must be focused. The buttons will appear darker when the program is unfocused.

#### Showing interface
Hover your mouse over the bottom of the screen to reveal the bar with current song info and buttons to navigate the program.

#### Saving last played song
Press the first button from the left (save icon) to disable or enable restoring last played song when you quit the program.

#### Pinning bar
Press the second button from the left (pushpin) to pin or unpin the bar.

#### Choosing songs
Press the third button from the left (file icon) to open or close the song selector.
- To favorite or unfavorite a song, press the heart icon next to your song.
- To change the song that will be played next, press the arrow icon next to your song.
- To play the song, click on the name of your song.
- You can close this menu by unfocusing the window.

#### Playing next song
Press the fourth button from the left (arrow) to play next randomized song.

#### Quitting app
Press `Alt+F4` while focused or the fifth button from the left (cross) to close the app.

#### Rewinding
Move your mouse to the bottom of the bar and click to rewind the song.


## Subtitles

### Syntax
Subtitles are stored in `.json` files with an array of dictionaries that contain two values: `text` is the text that will be displayed and `duration` is the duration of the element. You can leave `text` blank to create a pause.

In the following example, text `Test 1` will appear for 3 seconds, and after a 1 second pause, text `Test 2` will appear for 2 seconds.
```json
[
    {
        "text": "Test 1",
        "duration": 3.0
    },
    {
        "text": "",
        "duration": 1.0
    },
    {
        "text": "Test 2",
        "duration": 2.0
    },
]
```


### Creating your own

There will be a tool (gdr-se) to easily create and edit subtitles. While I'm working on it, you still can write `.json` files by yourself.


### Loading files

To load subtitles, you need to create a folder called `subtitles` in your songs folder and paste `.json` files there. Names of these files should correspond to the name of the song file, for example to load subtitles for the song called `song.mp3`, you would need to rename your `.json` file to `song.json`.