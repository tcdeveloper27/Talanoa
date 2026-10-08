/* ============================================================
   Talanoa library: every word on the board lives here.

   CORE  = the 6 buttons along the top. They NEVER move and are on
           every page, so they can be found without looking.
   PAGES = the screens you flip through with the ◀ ▶ arrows, in order.
           Each page is a fixed 4 × 3 grid: up to 12 tiles, always in
           the same spots. A page with fewer than 12 keeps blank spaces
           so nothing shifts.

   Each tile:  {"icon": "🍕", "label": "Pizza", "say": "I want pizza"}
   Names and words go in double quotes, with a comma after each tile
   except the last one on a page (the build stops if one is missing).
     icon  = the picture (an emoji; a matching 3D image is used)
     label = the word under the picture
     say   = what is spoken (leave out to speak the label)
     img   = optional real photo instead, e.g. "img": "photos/dad.jpg"
             (a page can have one too, for its picture on the arrows).
             A drawn picture in pictures/ ("pictures/knee.webp") shows
             like the emoji pictures instead of being cropped like a photo
     color = the colour of a page, or of a top-row button ("#D89412")
     short = optional shorter label for when the full one won't fit
             on a small phone (the tile still says its whole sentence)
     fx    = what a tap throws, for fun: "sparkle" (the usual),
             "confetti", "hearts", "stars", "bubbles", "soft" (a few
             gentle sparkles), or "ring" (no sparkles). A page can set
             one for all its tiles; a tile can override it. Settings
             can turn the fun down or off.
     answer = true: a word he answers with (Yes, No, ʻIo, ʻIkai,
             feelings, the Talk page; a page can set it for all its tiles). Only
             matters when Settings → "Calm answers" is switched on:
             then every answer gets the same gentle "soft", so no
             answer is more fun to pick than another. Off, they keep
             their own fx, just as before.
     words = true (on a page): single words (the Words page). Each
             tile is said with the ABC page's recording of its word,
             which tools/abc-voices.py makes several ways and checks
             by ear; the tile's own recording is the fallback.
     show  = true: also shows the words full screen, big enough to
             hand the phone to someone
     card  = true: printed as the cut-out "About me" card on the
             cover of the paper board (print.html)
     means = a translation, shown small under the label and in the
             banner (the Tongan page)
     sound = how the computer voice should pronounce it, if the
             spelling would trip it up ("Mah-loh" for Mālō). Between
             slashes it's the exact sounds, in IPA ("/mˈɑːloʊ/").
             Only the computer voice uses it; a recording made in
             Settings (Photos and voices) always wins.

   The same label can say different things on different pages
   (Drink is "I want a drink" on I want, "I would like a drink" at
   Maverik). Each different sentence gets its own recording.

   To leave a spot empty so the tiles after it don't move, put
   {"empty": true} in its place. New pages go at the end, just above
   ABC (the letter board is always the last page; the build stops if
   it isn't), so the pages he already knows stay the same number of
   swipes away. Only move a page if the family asks (2026-10-06: Body
   and Sick went right after Ouch).

   A page with "keyboard": true and no tiles is an alphabet board:
   tap letters to spell, then Speak. It talks in the board's own
   voice: the letters and every word on the board are recorded by
   tools/abc-voices.py (run it after changing words: GitHub doesn't),
   and Michael also says about 9,000 everyday words (LIST_VOICES in
   that file); any other word is spelled out, letter by letter, in
   that same voice.

   After changing words, run  python3 tools/build.py  (or let GitHub
   run it: it does whenever library.js changes) so the natural voices
   and pictures are made for the new tiles. Until then a new tile
   still works: it uses the phone's own voice and the plain emoji.
   ============================================================ */
window.TT_LIBRARY = {
  "core": [
    {"icon": "👍", "label": "Yes",      "say": "Yes",           "color": "#3F8A34", "fx": "confetti", "answer": true},
    {"icon": "👎", "label": "No",       "say": "No",            "color": "#C8342B", "fx": "soft", "answer": true},
    {"icon": "➕", "label": "More",     "say": "I want more",   "color": "#3C6E9F"},
    {"icon": "👋", "label": "Hi, I'm Brenton", "short": "Brenton", "color": "#8B5A2B", "fx": "confetti", "card": true,
     "say": "Hi, I'm Brenton. I can't talk with my mouth, so I talk with this phone. Please be patient and give me time. My emergency contacts are in this phone's Emergency information."},
    {"icon": "🙋", "label": "Help",     "say": "I need help",   "color": "#7B5AA6"},
    {"icon": "✋", "label": "Stop",     "say": "Stop please",   "color": "#C8342B", "fx": "soft"}
  ],

  "pages": [

    {"name": "I want", "icon": "🤲", "color": "#D89412", "tiles": [
      {"icon": "🥕", "label": "Snack",      "say": "I want a snack"},
      {"icon": "🥤", "label": "Drink",      "say": "I want a drink", "fx": "bubbles"},
      {"icon": "🚽", "label": "Bathroom",   "say": "I need the bathroom"},
      {"icon": "🛏️", "label": "Rest",       "say": "I want to lie down"},
      {"icon": "🌳", "label": "Outside",    "say": "I want to go outside"},
      {"icon": "🚗", "label": "Go ride",    "say": "I want to go for a ride"},
      {"icon": "🤗", "label": "Hug",        "say": "I want a hug", "fx": "hearts"},
      {"icon": "🤫", "label": "Quiet",      "say": "I need quiet, please"},
      {"icon": "✅", "label": "All done",   "say": "I am all done"},
      {"icon": "🧘", "label": "Break",      "say": "I need a break, please"},
      {"icon": "👀", "label": "Look",       "say": "Look at this!"},
      {"icon": "🔄", "label": "Something else", "say": "I want something else"}
    ]},

    {"name": "I feel", "icon": "😊", "color": "#3C6E9F", "answer": true, "tiles": [
      {"icon": "😀", "label": "Happy",      "say": "I feel happy", "fx": "confetti"},
      {"icon": "🤩", "label": "Excited",    "say": "I am excited!", "fx": "confetti"},
      {"icon": "😢", "label": "Sad",        "say": "I feel sad", "fx": "soft"},
      {"icon": "😤", "label": "Frustrated", "say": "I am frustrated", "fx": "soft"},
      {"icon": "😠", "label": "Angry",      "say": "I am angry", "fx": "soft"},
      {"icon": "😨", "label": "Scared",     "say": "I feel scared", "fx": "soft"},
      {"icon": "🤒", "label": "Hurt",       "say": "I do not feel good. It hurts.", "fx": "soft"},
      {"icon": "😴", "label": "Tired",      "say": "I am tired"},
      {"icon": "🥱", "label": "Bored",      "say": "I am bored"},
      {"icon": "😖", "label": "Too loud",   "say": "It is too loud for me", "fx": "soft"},
      {"icon": "🥶", "label": "Cold",       "say": "I am cold"},
      {"icon": "🥵", "label": "Hot",        "say": "I am too hot"}
    ]},

    {"name": "Ouch", "icon": "🤕", "color": "#C8342B", "fx": "soft", "tiles": [
      {"icon": "🤕", "label": "Head",       "say": "My head hurts"},
      {"icon": "🤢", "label": "Tummy",      "say": "My tummy hurts"},
      {"icon": "🤮", "label": "Throw up",   "say": "I think I am going to throw up"},
      {"icon": "🦷", "label": "Tooth",      "say": "My tooth hurts"},
      {"icon": "👂", "label": "Ear",        "say": "My ear hurts"},
      {"icon": "👁️", "label": "Eyes",       "say": "My eyes hurt"},
      {"icon": "💪", "label": "Arm",        "say": "My arm hurts"},
      {"icon": "🦵", "label": "Leg",        "say": "My leg hurts"},
      {"icon": "🦶", "label": "Foot",       "say": "My foot hurts"},
      {"icon": "🩹", "label": "Band-aid",   "say": "I need a band-aid"},
      {"icon": "💊", "label": "Medicine",   "say": "I think I need medicine"},
      {"icon": "🩺", "label": "Doctor",     "say": "I need to see a doctor"}
    ]},

    {"name": "Body", "icon": "🧍", "img": "pictures/body.webp", "color": "#B03050", "fx": "soft", "tiles": [
      {"icon": "🧍", "img": "pictures/back.webp",     "label": "Back",       "say": "My back hurts"},
      {"icon": "🧍", "img": "pictures/chest.webp",    "label": "Chest",      "say": "My chest hurts"},
      {"icon": "🧍", "img": "pictures/throat.webp",   "label": "Throat",     "say": "My throat hurts"},
      {"icon": "🧍", "img": "pictures/neck.webp",     "label": "Neck",       "say": "My neck hurts"},
      {"icon": "🧍", "img": "pictures/shoulder.webp", "label": "Shoulder",   "say": "My shoulder hurts"},
      {"icon": "🧍", "img": "pictures/hand.webp",     "label": "Hand",       "say": "My hand hurts"},
      {"icon": "🧍", "img": "pictures/knee.webp",     "label": "Knee",       "say": "My knee hurts"},
      {"icon": "🧍", "img": "pictures/bottom.webp",   "label": "Bottom",     "say": "My bottom hurts"},
      {"icon": "🧍", "img": "pictures/privates.webp", "label": "Privates",   "say": "My private parts hurt"},
      {"icon": "🙁", "label": "A little",   "say": "It hurts a little"},
      {"icon": "😣", "label": "A lot",      "say": "It hurts a lot"},
      {"icon": "😭", "label": "Really bad", "say": "It hurts really bad"}
    ]},

    {"name": "Sick", "icon": "😷", "color": "#4E7A2E", "fx": "soft", "tiles": [
      {"icon": "😵‍💫", "label": "Dizzy",         "say": "I feel dizzy"},
      {"icon": "🫁", "label": "Can't breathe", "say": "I can't breathe well"},
      {"icon": "🩸", "label": "Bleeding",      "say": "I am bleeding"},
      {"icon": "🧍", "img": "pictures/fell.webp",      "label": "Fell",       "say": "I fell down"},
      {"icon": "🌡️", "label": "Fever",         "say": "I have a fever"},
      {"icon": "🤧", "label": "Cough",         "say": "I have a cough"},
      {"icon": "🧍", "img": "pictures/itchy.webp",     "label": "Itchy",      "say": "My skin is itchy"},
      {"icon": "🚽", "img": "pictures/pee-hurts.webp", "label": "Pee hurts",  "say": "It hurts to pee"},
      {"icon": "🚽", "img": "pictures/cant-poop.webp", "label": "Can't poop", "say": "I can't poop"},
      {"icon": "⏱️", "label": "Just now",      "say": "It just started"},
      {"icon": "🗓️", "label": "Yesterday",     "say": "It started yesterday"},
      {"icon": "😌", "label": "Better",        "say": "I feel better now"}
    ]},

    {"name": "People", "icon": "🧑‍🤝‍🧑", "color": "#7B5AA6", "tiles": [
      {"icon": "👪", "label": "Family",     "say": "I want my family", "fx": "hearts"},
      {"icon": "🧑‍⚕️", "label": "Staff",    "say": "I need someone to help me"},
      {"icon": "🧑‍🤝‍🧑", "label": "Friend", "say": "I want to see my friend"},
      {"icon": "👋", "label": "Hi",         "say": "Hi!"},
      {"icon": "🤝", "label": "Bye",        "say": "Bye! See you later"},
      {"icon": "🙏", "label": "Please",     "say": "Please"},
      {"icon": "💛", "label": "Thanks",     "say": "Thank you"},
      {"icon": "😔", "label": "Sorry",      "say": "I am sorry"},
      {"icon": "❤️", "label": "Love you",   "say": "I love you", "fx": "hearts"},
      {"icon": "☝️", "label": "My turn",    "say": "It's my turn"},
      {"icon": "💻", "label": "GCB Computers", "say": "I want to go to GCB Computers"},
      {"icon": "👋", "label": "Hi, I'm Brenton", "short": "Brenton", "say": "Hi, I'm Brenton", "fx": "confetti"}
    ]},

    {"name": "Mom & Dad", "icon": "👪", "color": "#C2507E", "fx": "hearts", "tiles": [
      {"icon": "👨", "label": "Dad",        "say": "I want my dad"},
      {"icon": "📞", "label": "Call Dad",   "say": "Can I call my dad, please?"},
      {"icon": "🏡", "label": "Dad's house", "say": "I want to go to Dad's house"},
      {"icon": "📅", "label": "Dad coming?", "say": "Is Dad coming today?"},
      {"icon": "👩", "label": "Mom",        "say": "I want my mom"},
      {"icon": "📞", "label": "Call Mom",   "say": "Can I call my mom, please?"},
      {"icon": "🏘️", "label": "Mom's house", "say": "I want to go to Mom's house"},
      {"icon": "📅", "label": "Mom coming?", "say": "Is Mom coming today?"},
      {"icon": "👵", "label": "Grandma",    "say": "I want my grandma"},
      {"icon": "👴", "label": "Grandpa",    "say": "I want my grandpa"},
      {"icon": "👵", "label": "Nana",       "say": "I want my nana"},
      {"icon": "👴", "label": "Papa",       "say": "I want my papa"}
    ]},

    {"name": "Fun", "icon": "🎉", "color": "#3F8A34", "fx": "confetti", "tiles": [
      {"icon": "🤠", "label": "Toy Story",  "say": "I want to watch Toy Story"},
      {"icon": "📺", "label": "Cartoons",   "say": "I want to watch cartoons"},
      {"icon": "🍿", "label": "Movie",      "say": "Let's watch a movie"},
      {"icon": "🎭", "label": "Costume",    "say": "I want to put on my costume"},
      {"icon": "🎵", "label": "Music",      "say": "I want music, please"},
      {"icon": "🕺", "label": "Dance",      "say": "Let's dance!"},
      {"icon": "🧸", "label": "Toys",       "say": "I want to play with my toys"},
      {"icon": "🎮", "label": "Game",       "say": "I want to play a game"},
      {"icon": "📖", "label": "Book",       "say": "I want a book"},
      {"icon": "🎨", "label": "Draw",       "say": "I want to draw"},
      {"icon": "🏀", "label": "Ball",       "say": "Let's play ball"},
      {"icon": "🚶", "label": "Walk",       "say": "I want to go for a walk"}
    ]},

    {"name": "Toy Story", "icon": "🤠", "color": "#8B5A2B", "fx": "stars", "tiles": [
      {"icon": "🤠", "label": "Howdy",      "say": "Howdy, partner!"},
      {"icon": "🐴", "label": "Bullseye",   "say": "Ride like the wind, Bullseye!"},
      {"icon": "🚀", "label": "Infinity",   "say": "To infinity and beyond!"},
      {"icon": "⭐", "label": "Sky",        "say": "Reach for the sky!"},
      {"icon": "🐍", "label": "Snake",      "say": "There's a snake in my boot!"},
      {"icon": "🫶", "label": "Friend in me", "say": "You've got a friend in me!"},
      {"icon": "👢", "label": "Jessie",     "say": "Jessie, the yodeling cowgirl!"},
      {"icon": "🦖", "label": "Rex",        "say": "Rex! Roar!"},
      {"icon": "🐷", "label": "Hamm",       "say": "Hamm the piggy bank!"},
      {"icon": "👽", "label": "Aliens",     "say": "The claw is our master!"},
      {"icon": "🥔", "label": "Potato Head", "say": "Mister Potato Head!"},
      {"icon": "🐕", "label": "Slinky",     "say": "Slinky Dog!"}
    ]},

    {"name": "Food", "icon": "🍕", "color": "#D2691E", "tiles": [
      {"icon": "😋", "label": "Hungry",     "say": "I am hungry"},
      {"icon": "💧", "label": "Water",      "say": "I want water, please", "fx": "bubbles"},
      {"icon": "🧃", "label": "Juice",      "say": "I want juice, please", "fx": "bubbles"},
      {"icon": "🥛", "label": "Milk",       "say": "I want milk, please", "fx": "bubbles"},
      {"icon": "🥗", "label": "Salad",      "say": "I want a salad"},
      {"icon": "🍕", "label": "Pizza",      "say": "I want pizza"},
      {"icon": "🍔", "label": "Burger",     "say": "I want a hamburger"},
      {"icon": "🍗", "label": "Chicken",    "say": "I want chicken"},
      {"icon": "🍟", "label": "Fries",      "say": "I want fries"},
      {"icon": "🥪", "label": "Sandwich",   "say": "I want a sandwich"},
      {"icon": "🍎", "label": "Fruit",      "say": "I want some fruit"},
      {"icon": "🍦", "label": "Ice cream",  "say": "I want ice cream"}
    ]},

    {"name": "Maverik", "icon": "🏪", "color": "#2A5DA8", "tiles": [
      {"icon": "🥤", "label": "Drink",      "say": "I would like a drink", "fx": "bubbles"},
      {"icon": "🥨", "label": "Chips",      "say": "I would like some chips"},
      {"icon": "💧", "label": "Water",      "say": "I would like some water", "fx": "bubbles"},
      {"icon": "☕", "label": "Hot cocoa",  "say": "I would like a hot cocoa"},
      {"icon": "🙏", "label": "Please",     "say": "Please"},
      {"icon": "💛", "label": "Thank you",  "say": "Thank you"},
      {"icon": "🙇", "label": "Excuse me",  "say": "Excuse me"},
      {"icon": "💁", "label": "Help me?",   "say": "Could you help me?"},
      {"icon": "🧾", "label": "Receipt",    "say": "I would like the receipt"},
      {"icon": "🌳", "label": "Sit outside", "say": "I would like to sit outside"},
      {"icon": "🪑", "label": "Sit inside", "say": "I would like to sit inside"},
      {"icon": "🧼", "label": "Wash hands", "say": "I need to wash my hands"}
    ]},

    {"name": "My day", "icon": "☀️", "color": "#1F7F86", "tiles": [
      {"icon": "⏰", "label": "Wake up",    "say": "I am awake"},
      {"icon": "🍳", "label": "Breakfast",  "say": "I am ready for breakfast"},
      {"icon": "🍽️", "label": "Lunch",      "say": "I am ready for lunch"},
      {"icon": "🍝", "label": "Dinner",     "say": "I am ready for dinner"},
      {"icon": "🚿", "label": "Shower",     "say": "I want to take a shower", "fx": "bubbles"},
      {"icon": "🛁", "label": "Bath",       "say": "I want a bath", "fx": "bubbles"},
      {"icon": "🪥", "label": "Teeth",      "say": "Time to brush my teeth"},
      {"icon": "👕", "label": "Clothes",    "say": "I want to get dressed"},
      {"icon": "👟", "label": "Shoes",      "say": "I need my shoes"},
      {"icon": "💈", "label": "Haircut",    "say": "I need a haircut"},
      {"icon": "🧺", "label": "Laundry",    "say": "My clothes need washing"},
      {"icon": "🌙", "label": "Bed",        "say": "I am ready for bed"}
    ]},

    {"name": "Places", "icon": "🗺️", "color": "#2E7D5B", "tiles": [
      {"icon": "🏠", "label": "Home",       "say": "I want to go home"},
      {"icon": "🚪", "label": "My room",    "say": "I want to go to my room"},
      {"icon": "🛒", "label": "Store",      "say": "I want to go to the store"},
      {"icon": "🏞️", "label": "Park",       "say": "I want to go to the park"},
      {"icon": "🥡", "label": "Eat out",    "say": "Can we go out to eat?"},
      {"icon": "🎟️", "label": "Movies",     "say": "I want to go to the movies"},
      {"icon": "🏊", "label": "Swimming",   "say": "I want to go swimming", "fx": "bubbles"},
      {"icon": "🎳", "label": "Bowling",    "say": "Can we go bowling?"},
      {"icon": "📚", "label": "Library",    "say": "I want to go to the library"},
      {"icon": "🦁", "label": "Zoo",        "say": "I want to go to the zoo"},
      {"icon": "🏔️", "label": "Mountains",  "say": "I want to go to the mountains"},
      {"icon": "🏪", "label": "Maverik",    "say": "I want to go to Maverik"}
    ]},

    {"name": "Questions", "icon": "❓", "color": "#A23B72", "tiles": [
      {"icon": "❓", "label": "What now?",  "say": "What are we doing now?"},
      {"icon": "⏭️", "label": "What's next?", "say": "What are we doing next?"},
      {"icon": "🧭", "label": "Where to?",  "say": "Where are we going?"},
      {"icon": "👤", "label": "Who?",       "say": "Who is coming?"},
      {"icon": "⏳", "label": "How long?",  "say": "How long do I have to wait?"},
      {"icon": "🍲", "label": "What's for dinner?", "say": "What is for dinner?"},
      {"icon": "👉", "label": "What's that?", "say": "What is that?"},
      {"icon": "🔍", "label": "Where is it?", "say": "Where is it?"},
      {"icon": "🤔", "label": "Why?",       "say": "Why?"},
      {"icon": "🤲", "label": "Can I have it?", "say": "Can I have that, please?"},
      {"icon": "🤷", "label": "Don't know", "say": "I don't know"},
      {"icon": "🕒", "label": "When?",        "say": "When?"}
    ]},

    {"name": "Things", "icon": "🎒", "color": "#56657A", "tiles": [
      {"icon": "🎧", "label": "Headphones", "say": "I want my headphones"},
      {"icon": "🧢", "label": "Hat",        "say": "I want my hat"},
      {"icon": "🧥", "label": "Jacket",     "say": "I want my jacket"},
      {"icon": "🕶️", "label": "Sunglasses", "say": "I want my sunglasses"},
      {"icon": "🎒", "label": "Backpack",   "say": "I want my backpack"},
      {"icon": "💵", "label": "Money",      "say": "I want to buy something"},
      {"icon": "🔌", "label": "Charge",     "say": "My phone needs charging"},
      {"icon": "💡", "label": "Light on",   "say": "Turn on the light, please"},
      {"icon": "🧻", "label": "Tissue",     "say": "I need a tissue, please"},
      {"icon": "🖼️", "label": "Photos",     "say": "I want to look at my photos"},
      {"icon": "📷", "label": "Picture",    "say": "Take a picture!"},
      {"icon": "🌀", "label": "Fan",        "say": "Turn on the fan, please"}
    ]},

    {"name": "Talk", "icon": "💬", "color": "#4A3B9E", "answer": true, "tiles": [
      {"icon": "😍", "label": "I like it",  "say": "I like it!"},
      {"icon": "😒", "label": "Don't like", "say": "I don't like it"},
      {"icon": "🔁", "label": "Again",      "say": "Again! One more time"},
      {"icon": "⏸️", "label": "Wait",       "say": "Wait, please"},
      {"icon": "😂", "label": "Funny",      "say": "That's funny!"},
      {"icon": "😮", "label": "Wow",        "say": "Wow!"},
      {"icon": "😬", "label": "Oh no",      "say": "Oh no!"},
      {"icon": "🏷️", "label": "Mine",       "say": "That's mine"},
      {"icon": "🫵", "label": "Your turn",  "say": "Your turn"},
      {"icon": "🫴", "label": "Come here",  "say": "Come here, please"},
      {"icon": "⌚", "label": "Not now",    "say": "Not now. Maybe later"},
      {"icon": "🫷", "label": "Leave me alone", "say": "Please leave me alone"}
    ]},

    {"name": "Tongan", "icon": "🇹🇴", "color": "#8E1B3A", "tiles": [
      {"icon": "👋", "label": "Mālō e lelei", "means": "Hello",      "say": "Mālō e lelei", "sound": "Mah-loh, eh leh-lay"},
      {"icon": "💛", "label": "Mālō",         "means": "Thank you",  "say": "Mālō",         "sound": "Mah-loh"},
      {"icon": "💖", "label": "Mālō ʻaupito", "means": "Thank you very much", "say": "Mālō ʻaupito", "sound": "Mah-loh, ow-pee-toh"},
      {"icon": "❤️", "label": "ʻOfa atu",     "means": "Love you",   "say": "ʻOfa atu",     "sound": "Oh-fah, ah-too", "fx": "hearts"},
      {"icon": "👍", "label": "ʻIo",          "means": "Yes",        "say": "ʻIo",          "sound": "Ee-oh", "fx": "soft", "answer": true},
      {"icon": "👎", "label": "ʻIkai",        "means": "No",         "say": "ʻIkai",        "sound": "Ee-kai", "fx": "soft", "answer": true},
      {"icon": "🙂", "label": "Fēfē hake?",   "means": "How are you?",      "say": "Fēfē hake?",   "sound": "Feh-feh, hah-keh!"},
      {"icon": "👌", "label": "Sai pē",       "means": "I'm fine",          "say": "Sai pē",       "sound": "Sigh, peh"},
      {"icon": "🙏", "label": "Kātaki",       "means": "Please",            "say": "Kātaki",       "sound": "Kah-tah-kee"},
      {"icon": "😔", "label": "Fakamolemole", "means": "Sorry",             "say": "Fakamolemole", "sound": "Fah-kah-moh-lay-moh-lay", "short": "Faka-molemole"},
      {"icon": "🤝", "label": "ʻAlu ā",       "means": "Goodbye, go well", "say": "ʻAlu ā",       "sound": "Ah-loo-ah"},
      {"icon": "🌙", "label": "Mohe ā",       "means": "Good night",        "say": "Mohe ā",       "sound": "/mˈoʊhɛ ɑː/"}
    ]},

    {"name": "Words", "icon": "🧩", "color": "#6A1B9A", "words": true, "tiles": [
      {"icon": "🙋", "label": "I",         "say": "I"},
      {"icon": "👉", "label": "You",       "say": "You"},
      {"icon": "🤲", "label": "Want",      "say": "Want"},
      {"icon": "👍", "label": "Like",      "say": "Like"},
      {"icon": "🚶", "label": "Go",        "say": "Go"},
      {"icon": "🫴", "label": "Get",       "say": "Get"},
      {"icon": "🛠️", "label": "Do",        "say": "Do"},
      {"icon": "👀", "label": "Look",      "say": "Look"},
      {"icon": "➕", "label": "More",      "say": "More"},
      {"icon": "🚫", "label": "Not",       "say": "Not"},
      {"icon": "🔀", "label": "Different", "say": "Different"},
      {"icon": "✅", "label": "Finished",  "say": "Finished"}
    ]},

    {"name": "ABC", "icon": "🔤", "color": "#3A3A3A", "keyboard": true, "tiles": []}
  ]
};
