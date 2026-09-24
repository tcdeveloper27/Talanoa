/* ============================================================
   Talanoa library: every word on the board lives here.

   CORE  = the 6 buttons along the top. They NEVER move and are on
           every page, so they can be found without looking.
   PAGES = the screens you flip through with the ◀ ▶ arrows, in order.
           Each page is a fixed 4 × 3 grid: up to 12 tiles, always in
           the same spots. A page with fewer than 12 keeps blank spaces
           so nothing shifts.

   Each tile:  { icon:"🍕", label:"Pizza", say:"I want pizza" }
     icon  = the picture (an emoji; a matching 3D image is used)
     label = the word under the picture
     say   = what is spoken (leave out to speak the label)
     img   = optional real photo instead, e.g. img:"photos/dad.jpg"

   After changing words, run  python3 tools/build.py  so the natural
   voices and pictures are regenerated for the new tiles. Until then
   a new tile still works: it uses the tablet's own voice and emoji.
   ============================================================ */
window.TT_LIBRARY = {
  "core": [
    {"icon": "👍", "label": "Yes",      "say": "Yes",           "color": "#3F8A34"},
    {"icon": "👎", "label": "No",       "say": "No",            "color": "#C8342B"},
    {"icon": "➕", "label": "More",     "say": "I want more",   "color": "#3C6E9F"},
    {"icon": "✅", "label": "All done", "say": "I am all done", "color": "#8B5A2B"},
    {"icon": "🙋", "label": "Help",     "say": "I need help",   "color": "#7B5AA6"},
    {"icon": "✋", "label": "Stop",     "say": "Stop please",   "color": "#C8342B"}
  ],

  "pages": [
    {"name": "I want", "icon": "🤲", "color": "#D89412", "tiles": [
      {"icon": "🍪", "label": "Snack",      "say": "I want a snack"},
      {"icon": "🥤", "label": "Drink",      "say": "I want a drink"},
      {"icon": "🚽", "label": "Bathroom",   "say": "I need the bathroom"},
      {"icon": "🛏️", "label": "Rest",       "say": "I want to lie down"},
      {"icon": "🌳", "label": "Outside",    "say": "I want to go outside"},
      {"icon": "🚗", "label": "Go ride",    "say": "I want to go for a ride"},
      {"icon": "🤗", "label": "Hug",        "say": "I want a hug"},
      {"icon": "🤫", "label": "Quiet",      "say": "I need quiet, please"},
      {"icon": "📱", "label": "Tablet",     "say": "I want my tablet"},
      {"icon": "🧘", "label": "Break",      "say": "I need a break, please"},
      {"icon": "👀", "label": "Look",       "say": "Look at this!"},
      {"icon": "🔄", "label": "Something else", "say": "I want something else"}
    ]},

    {"name": "I feel", "icon": "😊", "color": "#3C6E9F", "tiles": [
      {"icon": "😀", "label": "Happy",      "say": "I feel happy"},
      {"icon": "🤩", "label": "Excited",    "say": "I am excited!"},
      {"icon": "😢", "label": "Sad",        "say": "I feel sad"},
      {"icon": "😤", "label": "Frustrated", "say": "I am frustrated"},
      {"icon": "😠", "label": "Angry",      "say": "I am angry"},
      {"icon": "😨", "label": "Scared",     "say": "I feel scared"},
      {"icon": "🤒", "label": "Hurt",       "say": "I do not feel good. It hurts."},
      {"icon": "😴", "label": "Tired",      "say": "I am tired"},
      {"icon": "🥱", "label": "Bored",      "say": "I am bored"},
      {"icon": "😖", "label": "Too loud",   "say": "It is too loud for me"},
      {"icon": "🥶", "label": "Cold",       "say": "I am cold"},
      {"icon": "🥵", "label": "Hot",        "say": "I am too hot"}
    ]},

    {"name": "Ouch", "icon": "🤕", "color": "#C8342B", "tiles": [
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

    {"name": "People", "icon": "🧑‍🤝‍🧑", "color": "#7B5AA6", "tiles": [
      {"icon": "👪", "label": "Family",     "say": "I want my family"},
      {"icon": "🧑‍⚕️", "label": "Staff",    "say": "I need someone to help me"},
      {"icon": "🧑‍🤝‍🧑", "label": "Friend", "say": "I want to see my friend"},
      {"icon": "👋", "label": "Hi",         "say": "Hi!"},
      {"icon": "🤝", "label": "Bye",        "say": "Bye! See you later"},
      {"icon": "🙏", "label": "Please",     "say": "Please"},
      {"icon": "💛", "label": "Thanks",     "say": "Thank you"},
      {"icon": "😔", "label": "Sorry",      "say": "I am sorry"},
      {"icon": "❤️", "label": "Love you",   "say": "I love you"},
      {"icon": "☝️", "label": "My turn",    "say": "It's my turn"}
    ]},

    {"name": "Mom & Dad", "icon": "👪", "color": "#C2507E", "tiles": [
      {"icon": "👨", "label": "Dad",        "say": "I want my dad"},
      {"icon": "📞", "label": "Call Dad",   "say": "Can I call my dad, please?"},
      {"icon": "🏡", "label": "Dad's house", "say": "I want to go to Dad's house"},
      {"icon": "📅", "label": "Dad coming?", "say": "Is Dad coming today?"},
      {"icon": "👩", "label": "Mom",        "say": "I want my mom"},
      {"icon": "📞", "label": "Call Mom",   "say": "Can I call my mom, please?"},
      {"icon": "🏘️", "label": "Mom's house", "say": "I want to go to Mom's house"},
      {"icon": "📅", "label": "Mom coming?", "say": "Is Mom coming today?"}
    ]},

    {"name": "Fun", "icon": "🎉", "color": "#3F8A34", "tiles": [
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

    {"name": "Toy Story", "icon": "🤠", "color": "#8B5A2B", "tiles": [
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
      {"icon": "💧", "label": "Water",      "say": "I want water, please"},
      {"icon": "🧃", "label": "Juice",      "say": "I want juice, please"},
      {"icon": "🥛", "label": "Milk",       "say": "I want milk, please"},
      {"icon": "☕", "label": "Cocoa",      "say": "I want hot chocolate, please"},
      {"icon": "🍕", "label": "Pizza",      "say": "I want pizza"},
      {"icon": "🍔", "label": "Burger",     "say": "I want a hamburger"},
      {"icon": "🍗", "label": "Chicken",    "say": "I want chicken"},
      {"icon": "🍟", "label": "Fries",      "say": "I want fries"},
      {"icon": "🥪", "label": "Sandwich",   "say": "I want a sandwich"},
      {"icon": "🍎", "label": "Fruit",      "say": "I want some fruit"},
      {"icon": "🍦", "label": "Ice cream",  "say": "I want ice cream"}
    ]},

    {"name": "My day", "icon": "☀️", "color": "#1F7F86", "tiles": [
      {"icon": "⏰", "label": "Wake up",    "say": "I am awake"},
      {"icon": "🍳", "label": "Breakfast",  "say": "I am ready for breakfast"},
      {"icon": "🍽️", "label": "Lunch",      "say": "I am ready for lunch"},
      {"icon": "🍝", "label": "Dinner",     "say": "I am ready for dinner"},
      {"icon": "🚿", "label": "Shower",     "say": "I want to take a shower"},
      {"icon": "🛁", "label": "Bath",       "say": "I want a bath"},
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
      {"icon": "🏊", "label": "Swimming",   "say": "I want to go swimming"},
      {"icon": "🎳", "label": "Bowling",    "say": "Can we go bowling?"},
      {"icon": "📚", "label": "Library",    "say": "I want to go to the library"},
      {"icon": "🦁", "label": "Zoo",        "say": "I want to go to the zoo"},
      {"icon": "🏔️", "label": "Mountains",  "say": "I want to go to the mountains"}
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
      {"icon": "🤷", "label": "Don't know", "say": "I don't know"}
    ]},

    {"name": "Things", "icon": "🎒", "color": "#56657A", "tiles": [
      {"icon": "🎧", "label": "Headphones", "say": "I want my headphones"},
      {"icon": "🧢", "label": "Hat",        "say": "I want my hat"},
      {"icon": "🧥", "label": "Jacket",     "say": "I want my jacket"},
      {"icon": "🕶️", "label": "Sunglasses", "say": "I want my sunglasses"},
      {"icon": "🎒", "label": "Backpack",   "say": "I want my backpack"},
      {"icon": "💵", "label": "Money",      "say": "I want to buy something"},
      {"icon": "🔌", "label": "Charge",     "say": "My tablet needs charging"},
      {"icon": "💡", "label": "Light on",   "say": "Turn on the light, please"},
      {"icon": "🧻", "label": "Tissue",     "say": "I need a tissue, please"},
      {"icon": "🖼️", "label": "Photos",     "say": "I want to look at my photos"},
      {"icon": "📷", "label": "Picture",    "say": "Take a picture!"},
      {"icon": "🌀", "label": "Fan",        "say": "Turn on the fan, please"}
    ]}
  ]
};
