# Talanoa

*Talanoa* (tah-lah-NOH-ah) is Tongan for talking together.

Made for the residents of Faleofaz.

A tap-to-speak picture board (AAC). Tap a tile and it says the phrase out loud in a natural voice. Brenton uses it on his Android phone.

**Open it:** https://tcdeveloper27.github.io/Talanoa/

On an Android phone (or tablet), open the link in Chrome, then **⋮ → Add to Home screen** (or **Install app**). It opens full screen like an app, stays upright, and keeps working with no internet.

**Staff guide:** https://tcdeveloper27.github.io/Talanoa/manual/ (printable PDF: [manual/Talanoa-Staff-Guide.pdf](manual/Talanoa-Staff-Guide.pdf)). Also in the app: hold ⚙ → **Staff guide**.

## Using it

- **Top row** (Yes, No, More, "Hi, I'm Brenton", Help, Stop) is on every page and never moves.
- **Swipe** sideways across the tiles to turn the page; the page follows the finger and springs back if let go early. A swipe never speaks.
- **◀ ▶ arrows** flip between pages too, like a Stream Deck. Each arrow shows the picture of the page it goes to, and they wrap around at the ends.
- **Tap the page name** in the middle to jump straight to any page.
- **The last tile tapped glows** (a slow, soft pulse) for 30 seconds, and its words stay in the banner, so he can lift the phone and show someone. Tapping another tile moves the glow straight away.
- **Every tap counts:** a tile speaks when the finger lifts, even if it slid a little or was held down (the browser's own click would silently drop those). Fast taps all count.
- **Quick sound:** the clips of the page on screen, the top row and the ABC letters are decoded ahead of time and played with Web Audio, starting just past each clip's quiet lead-in, so a tap is heard sooner: on an Android 16 emulator about 70 ms from the finger lifting to the voice, where an `<audio>` player took about 240 ms (2026-10-07). The `<audio>` players are the fallback (a clip not decoded yet). At a speed other than normal, each decoded clip gets a slowed (or sped-up) copy that keeps its pitch (WSOLA, as Chrome does it), made in the background, so those taps are just as quick. The sound sleeps after 20 s of quiet and wakes as soon as a finger touches the screen. The sparkles wait until the voice has started (0.15 s at most), so they don't hold it up. (Browsers only allow sound after the first touch, so the very first tap after opening is a little slower.)
- **Android's Back gesture** (a swipe in from the screen's edge) doesn't close the app; it closes Settings or the page list if one is open.
- **It's fun:** every tap makes the tile bounce, ripples rings out of it and throws sparkles in the page's colour: confetti for happy words, hearts for hugs, stars on the Toy Story page, bubbles for drinks. Tapping the same tile again and again builds up to a shower over the whole screen. Sad and hurt words get a few gentle sparkles instead. Tiles pop in when the arrows or the page list turn the page, and every page turn sends a streak across. Rings and sparkles are drawn on a see-through canvas that ignores touches, so they can never block a tap; they wait for the voice to start, and the drawing loop only runs while something is on screen.
- **Show it big:** tap the words in the banner and they fill the screen, for a cashier, a noisy room or someone across the table ("Say it again", Close, or Back; it closes itself after a minute). The top row's **Hi, I'm Brenton** says who he is and that he talks with this phone (the People page keeps a short "Hi, I'm Brenton"). It tells people his emergency contacts are in the phone's own Emergency information (medical details belong there too); none of that is on this public site.
- **Talk page:** comments and opinions, not just requests: I like it, Don't like, Again, Wait, Funny, Wow, Oh no, Mine, Your turn, Come here, Not now, Leave me alone.
- **Tongan page:** Mālō e lelei, Mālō, Mālō ʻaupito, ʻOfa atu, ʻIo, ʻIkai, Fēfē hake? (How are you?), Sai pē (I'm fine), Kātaki (Please), Fakamolemole (Sorry), ʻAlu ā (Goodbye, go well: said to someone leaving), Mohe ā (Good night), each with its meaning underneath. The computer voice only approximates Tongan, so the Faleofaz families can record them in their own voices (below).
- **ABC page:** an alphabet board: tap letters, then Speak, all in the board's own voice. Every letter and every word on the board are pre-recorded in each voice by `tools/abc-voices.py`, and Michael (the default voice) also says about 9,000 everyday words (`tools/abc-common-words.txt`, picked by `tools/abc-vocab.py`; names and words of your own go in `tools/abc-added-words.txt`; `LIST_VOICES` in `tools/abc-voices.py` says which voices get them, about 45 minutes and 54 MB each). Run with a speech recognizer (`TALANOA_WHISPER` or `TALANOA_ASR`), it keeps a version that is heard right, because Kokoro garbles very short words that start with a vowel. Any other word is spelled out in that same voice. Re-run it after changing words (GitHub doesn't run it); until then a new word is spelled out.
- **Fits above the navigation bar:** newer Android (e.g. a Pixel on Android 16) draws installed web apps behind the ◀ ● ■ bar. The installed app switches `viewport-fit=cover` on, keeps it only if Chrome then reports the bar's height (and pads by it), and otherwise switches straight back (on Brenton's phone Chrome reports 0). Settings → Screen shows what it found and has a manual "move up" switch.
- **Photos and voices (Settings):** give any tile a photo (taken with the camera or chosen from the phone), or record a voice for it. They're kept only on that phone (IndexedDB), never on the website, so photos of people stay private; **Save a backup** / **Restore a backup** move them as one file.
- **Most-used pictures (Settings):** per-tile tap counts for the last 7, 30 or 90 days, plus which tiles weren't used. Counted on the phone only, never sent anywhere; repeated taps within 3 seconds count once; can be turned off and cleared.
- **Body and Sick pages (health):** where it hurts (back, chest, throat, neck, shoulder, hand, knee, bottom, privates), then A little / A lot / Really bad; and dizzy, can't breathe, bleeding, fell, fever, cough, itchy, pee hurts, can't poop, just now, yesterday, better. Body parts with no emoji use drawn pictures: one figure, the same on every tile, with the sore spot glowing red (`pictures/`, drawn by `tools/body-pictures.py`). They sit right after Ouch (pages 4 and 5).
- **Paper board:** `print.html` (Settings → Paper board to print) lays every page out on US Letter, same colours and spots, with each tile's words underneath and an About me card on the cover. Ready-made PDF: [manual/Talanoa-Paper-Board.pdf](manual/Talanoa-Paper-Board.pdf). **Health pages to print** (Settings) prints just Ouch, Body and Sick for doctor visits (`print.html?pages=Ouch,Body,Sick`; PDF: [manual/Talanoa-Health-Pages.pdf](manual/Talanoa-Health-Pages.pdf)).
- **Words page** (2026-10-08, just above ABC): 12 single core words (I, You, Want, Like, Go, Get, Do, Look, More, Not, Different, Finished). The page is marked `"words": true` in `library.js`, so each tile uses the ABC page's recording of its word (made several ways and checked by a speech recogniser, which suits single words best); its own clip is the fallback.
- **Talking in sentences (Settings, each off unless chosen, 2026-10-08):** **Build sentences** (each tap still speaks; its words also line up in the banner; 🔊 says the whole sentence piece by piece, ✕ clears; ABC words join in), **Word suggestions** on the ABC page (3 words finishing the one being typed: words he has spoken first, then by frequency from `abc-rank.txt`, made by `tools/abc-rank.py`; only words the chosen voice says whole), **Numbers** on the ABC page (0-9, said as words: 15 "fifteen"; every voice has the number words), **Recent sentences** with the big words.
- **Bigger pictures (Settings → Screen, off unless chosen):** 6 on a screen; each page becomes two screens ("Food", "Food 2"), empty halves left out; one page dot per page.
- **Find a word (Settings):** type part of a word; tap a result to turn to its page with the picture outlined (nothing is said). **This week** (Settings → Most-used pictures): taps per day for 7 days and pictures used for the first time; on the phone only.
- **Settings:** hold the ⚙ in the top banner for 1 second. Choose the voice (Michael is the default; also Fenrir, Heart, Bella, Sarah, George, Emma, or the phone's built-in voice), speed and volume, pick which pages to show, turn swiping off if pages turn by accident, and set **Fun effects** to Lots, A little (bounces and rings only) or Off. A phone set to "reduce motion" starts on A little. Options that change something he already knows start **off**: **Calm answers** (Yes, No, feelings and the Talk page all get the same gentle sparkles, so no answer is more fun to pick) and **Darker page names** (the lighter page and top-row colours darkened just enough for white text to reach 4.6 : 1, a little over the 4.5 : 1 that WCAG asks for). **Tap the words to show them big** starts on.

19 pages: I want, I feel, Ouch, Body, Sick, People, Mom & Dad, Fun, Toy Story, Food, Maverik, My day, Places, Questions, Things, Talk, Tongan, Words, ABC. New pages go at the end, just above ABC (the letter board is always the last page; the build stops if it isn't), so the pages he knows stay the same number of swipes away. Tim moved Body and Sick next to Ouch on 2026-10-06, so all three health pages sit together.

## Changing the words

All words are in `library.js`, with one line per tile:

```js
{"icon": "🍕", "label": "Pizza", "say": "I want pizza"},
```

Then run `python3 tools/build.py` (or let GitHub run it: see *Updating the board*) to make the 3D picture and natural-voice recordings for any new or changed tiles. A new tile works even before that, using the emoji and the phone's built-in voice.

**Family rule:** every Dad tile must have the same tile for Mom directly underneath it. All parent tiles live on the Mom & Dad page, and the build stops with a message if the rule is ever broken.

- The same label can say different things on different pages (Drink is "I want a drink" on I want and "I would like a drink" on Maverik). Every different sentence gets its own recording; tiles that say the same thing share one.
- To leave a spot empty so the tiles after it don't move, put `{"empty": true}` in its place. Never move a tile he knows: fill empty spots, or add a page at the end (just above ABC, which stays last).
- `"fx"` chooses what a tap throws: `"sparkle"` (the default), `"confetti"`, `"hearts"`, `"stars"`, `"bubbles"`, `"soft"` (a few gentle sparkles, for sad or hurt words) or `"ring"` (no sparkles). Set it on a page for all its tiles, or on a tile.
- `"answer": true` marks words he answers with (Yes, No, ʻIo, ʻIkai, the I feel and Talk pages). Only used when Settings → Calm answers is on: then they all get `"soft"`.
- `"show": true` also opens the words full screen. `"card": true` marks the tile printed as the About me card on the paper board's cover. `"means"` is a translation shown under the label and in the banner (the Tongan page).
- `"sound"` tells the computer voice how to pronounce a tricky word (`"Mah-loh"` for Mālō); between slashes it's exact IPA sounds (`"/mˈɑːloʊ/"`). A recording made on the phone always wins.
- A page has a `"name"`, an `"icon"`, a `"color"` (`"#D89412"`; top-row buttons have one too) and its `"tiles"`. A page with `"keyboard": true` and no tiles is the ABC page.
- A tile can have a `"short"` label for small screens: `"short": "Brenton"` is shown only if the full label won't fit. It still says the whole sentence.
- To use a real photo instead of a picture, upload it to a `photos` folder, then add `"img": "photos/dad.jpg"` to the tile (a page can have one too). The build stops with a message if a photo is missing, so upload the photo first. Drawn pictures go in `pictures/` (`"img": "pictures/knee.webp"`); they show like the emoji pictures instead of being cropped like a photo.

## Updating the board

**To change words or add tiles:** edit `library.js` on GitHub (open the file, click the ✏️ pencil, make the change, then **Commit changes**). That's all.

1. GitHub automatically makes the 3D pictures and natural voices for anything new (the **Build pictures and voices** run under the **Actions** tab, a few minutes; the first run takes longer). The ABC page's word recordings aren't made there: run `tools/abc-voices.py`.
2. It publishes the update to the website.
3. Phones pick it up by themselves: they check when the app opens, when the screen comes back on, and every 30 minutes. The new version downloads in the background and only switches on when nobody has tapped for 2 minutes (or the screen is off), coming back to the same page, so the board never changes mid-sentence.
4. To update a phone right away: hold ⚙ → **Check for updates now**. Settings also shows the version and when it last checked.

If there's a mistake in `library.js` (a missing comma or quote, a Dad tile without its Mom tile underneath, a photo that isn't uploaded, or ABC not the last page), the Actions run turns red with a message saying what and where, GitHub emails you, and phones stay on the last good version until it's fixed.

## Files

| File | What it is |
|---|---|
| `index.html` | The app |
| `library.js` | Every page, tile and phrase |
| `assets.js`, `sw.js` | Made by the build: picture/voice lists and the offline cache |
| `img/` | 3D pictures |
| `pictures/` | Drawn pictures for the Body and Sick pages (made by `tools/body-pictures.py`: `python3 tools/body-pictures.py`, needs rsvg-convert, Pillow and the emoji pictures `tools/build.py` downloads, so run the build once first) |
| `voices/<name>/` | Natural-voice recordings: one MP3 per different sentence (tiles that say the same thing share one), the Settings samples, and the ABC page's letters and words in `abc/` (made by `tools/abc-voices.py`) |
| `tools/build.py` | Checks `library.js` (it stops with a message if something is wrong), then makes the pictures, voices, home-screen icons, the staff guide page and the offline cache (the app, its pictures and the staff guide; `--offline-list` remakes just that) |
| `manual/` | Staff guide (made by `tools/manual.py` from `tools/manual-template.html`; screenshots in `manual/img/`) |
| `print.html` | The paper board (every page as a printable sheet, made from `library.js`; `?pages=Ouch,Body,Sick` prints just those) |
| `tools/guide-pictures.js` | Retakes the guide's screenshots on a phone screen and prints its PDF, the paper-board PDF and the health-pages PDF (`node tools/guide-pictures.js` from the repo folder; needs Chromium, playwright-core, and Python with qrcode) |
| `.github/workflows/build.yml` | Runs `tools/build.py` on GitHub whenever the words change |

## Credits

Tim Broussard, Brenton Broussard, Legion, and Faleofaz ([contact](https://faleofaz.org/#contact)). In the app: hold ⚙ → **About & credits**.

- Pictures: [Fluent Emoji](https://github.com/microsoft/fluentui-emoji) © Microsoft, MIT licence (see `img/LICENSE-fluent-emoji.txt`).
- Voices: recorded ahead of time with [Kokoro](https://github.com/hexgrad/kokoro) (Apache 2.0), an open-source speech model, so the phone plays recordings instead of needing a speech engine (it saves the chosen voice for offline use).
- ABC page words: chosen with wordfreq by Robyn Speer (data CC BY-SA 4.0, so `tools/abc-common-words.txt` is too) and WordNet 3.0 © 2006 Princeton University.
- Drawn health pictures (`pictures/`): made by `tools/body-pictures.py`; Pee hurts and Can't poop include Fluent Emoji (MIT).
