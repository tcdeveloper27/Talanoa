# Talanoa

*Talanoa* (tah-lah-NOH-ah) is Tongan for talking together.

A tap-to-speak picture board (AAC). Tap a tile and it says the phrase out loud in a natural voice.

**Open it:** https://tcdeveloper27.github.io/Talanoa/

On an Android tablet, open the link in Chrome, then **⋮ → Add to Home screen** (or **Install app**). It opens full screen like an app and keeps working with no internet.

## Using it

- **Top row** (Yes, No, More, All done, Help, Stop) is on every page and never moves.
- **◀ ▶ arrows** flip between pages, like a Stream Deck. Each arrow shows the picture of the page it goes to, and they wrap around at the ends.
- **Tap the page name** in the middle to jump straight to any page.
- **Settings:** hold the ⚙ in the top banner for 1 second. Choose the voice (Michael is the default; also Fenrir, Heart, Bella, Sarah, George, Emma, or the tablet's own voice), speed and volume, and pick which pages to show.

12 pages: I want, I feel, Ouch, People, Mom & Dad, Fun, Toy Story, Food, My day, Places, Questions, Things.

## Changing the words

All words are in `library.js`, with one line per tile:

```js
{"icon": "🍕", "label": "Pizza", "say": "I want pizza"},
```

Then run `python3 tools/build.py` to make the 3D picture and natural-voice recordings for any new or changed tiles. A new tile works even before that, using the emoji and the tablet's voice.

To use a real photo instead of a picture, add `"img": "photos/dad.jpg"` to the tile and put the photo in a `photos` folder.

## Files

| File | What it is |
|---|---|
| `index.html` | The app |
| `library.js` | Every page, tile and phrase |
| `assets.js`, `sw.js` | Made by the build: picture/voice lists and the offline cache |
| `img/` | 3D pictures |
| `voices/<name>/` | Natural-voice recordings, one MP3 per tile |
| `tools/build.py` | Makes the pictures, voices and offline cache |

## Credits

- Pictures: [Fluent Emoji](https://github.com/microsoft/fluentui-emoji) © Microsoft, MIT licence (see `img/LICENSE-fluent-emoji.txt`).
- Voices: made with [Kokoro](https://github.com/hexgrad/kokoro) (Apache 2.0), an open-source speech model, so the tablet doesn't need to download a voice.
