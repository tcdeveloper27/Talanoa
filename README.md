# Talanoa

*Talanoa* (tah-lah-NOH-ah) is Tongan for talking together.

Made for the residents of Faleofaz.

A tap-to-speak picture board (AAC). Tap a tile and it says the phrase out loud in a natural voice. Brenton uses it on his Android phone.

**Open it:** https://tcdeveloper27.github.io/Talanoa/

On an Android phone (or tablet), open the link in Chrome, then **⋮ → Add to Home screen** (or **Install app**). It opens full screen like an app, stays upright, and keeps working with no internet.

**Staff guide:** https://tcdeveloper27.github.io/Talanoa/manual/ (printable PDF: [manual/Talanoa-Staff-Guide.pdf](manual/Talanoa-Staff-Guide.pdf)). Also in the app: hold ⚙ → **Staff guide**.

## Using it

- **Top row** (Yes, No, More, Hi I'm Brenton, Help, Stop) is on every page and never moves.
- **Swipe** sideways across the tiles to turn the page; the page follows the finger and springs back if let go early. A swipe never speaks.
- **◀ ▶ arrows** flip between pages too, like a Stream Deck. Each arrow shows the picture of the page it goes to, and they wrap around at the ends.
- **Tap the page name** in the middle to jump straight to any page.
- **The last tile tapped glows** (a slow, soft pulse) for 30 seconds, and its words stay in the banner, so he can lift the phone and show someone. Tapping another tile moves the glow straight away.
- **Every tap counts:** a tile speaks when the finger lifts, even if it slid a little or was held down (the browser's own click would silently drop those). Fast taps all count.
- **Android's Back gesture** (a swipe in from the screen's edge) doesn't close the app; it closes Settings or the page list if one is open.
- **Settings:** hold the ⚙ in the top banner for 1 second. Choose the voice (Michael is the default; also Fenrir, Heart, Bella, Sarah, George, Emma, or the phone's built-in voice), speed and volume, pick which pages to show, and turn swiping off if pages turn by accident.

13 pages: I want, I feel, Ouch, People, Mom & Dad, Fun, Toy Story, Food, Maverik, My day, Places, Questions, Things.

## Changing the words

All words are in `library.js`, with one line per tile:

```js
{"icon": "🍕", "label": "Pizza", "say": "I want pizza"},
```

Then run `python3 tools/build.py` to make the 3D picture and natural-voice recordings for any new or changed tiles. A new tile works even before that, using the emoji and the phone's built-in voice.

**Family rule:** every Dad tile must have the same tile for Mom directly underneath it. All parent tiles live on the Mom & Dad page, and the build stops with a message if the rule is ever broken.

- The same label can say different things on different pages (Drink is "I want a drink" on I want and "I would like a drink" on Maverik). Every different sentence gets its own recording; tiles that say the same thing share one.
- To leave a spot empty so the tiles after it don't move, put `{"empty": true}` in its place (Food has one where Cocoa used to be).
- A tile can have a `"short"` label for small screens: `"short": "Brenton"` is shown only if the full label won't fit. It still says the whole sentence.
- To use a real photo instead of a picture, upload it to a `photos` folder, then add `"img": "photos/dad.jpg"` to the tile (a page can have one too). The build stops with a message if a photo is missing, so upload the photo first.

## Updating the board

**To change words or add tiles:** edit `library.js` on GitHub (open the file, click the ✏️ pencil, make the change, then **Commit changes**). That's all.

1. GitHub automatically makes the 3D pictures and natural voices for anything new (the **Build pictures and voices** run under the **Actions** tab, a few minutes; the first run takes longer).
2. It publishes the update to the website.
3. Phones pick it up by themselves: they check when the app opens, when the screen comes back on, and every 30 minutes. The new version downloads in the background and only switches on when nobody has tapped for 2 minutes (or the screen is off), coming back to the same page, so the board never changes mid-sentence.
4. To update a phone right away: hold ⚙ → **Check for updates now**. Settings also shows the version and when it last checked.

If there's a mistake in `library.js` (a missing comma or quote, a Dad tile without its Mom tile underneath, or a photo that isn't uploaded), the Actions run turns red with a message saying what and where, GitHub emails you, and phones stay on the last good version until it's fixed.

## Files

| File | What it is |
|---|---|
| `index.html` | The app |
| `library.js` | Every page, tile and phrase |
| `assets.js`, `sw.js` | Made by the build: picture/voice lists and the offline cache |
| `img/` | 3D pictures |
| `voices/<name>/` | Natural-voice recordings, one MP3 per tile |
| `tools/build.py` | Makes the pictures, voices and offline cache |
| `manual/` | Staff guide (made by `tools/manual.py` from `tools/manual-template.html`; screenshots in `manual/img/`) |
| `tools/guide-pictures.js` | Retakes the guide's screenshots on a phone screen and prints its PDF (`node tools/guide-pictures.js`, needs Chromium + playwright-core) |
| `.github/workflows/build.yml` | Runs `tools/build.py` on GitHub whenever the words change |

## Credits

Tim Broussard, Brenton Broussard, Legion, and Faleofaz ([contact](https://faleofaz.org/#contact)). In the app: hold ⚙ → **About & credits**.

- Pictures: [Fluent Emoji](https://github.com/microsoft/fluentui-emoji) © Microsoft, MIT licence (see `img/LICENSE-fluent-emoji.txt`).
- Voices: made with [Kokoro](https://github.com/hexgrad/kokoro) (Apache 2.0), an open-source speech model, so the phone doesn't need to download a voice.
