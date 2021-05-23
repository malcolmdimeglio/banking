Groceries = ["iga", "save on foods", "nesters", "t&t", "kiki", "yig", "persia foods", "whole foods",
             "organic acres market", "danial market", "choices", "safeway", "market", "urban fare",
             "nofrills", "costco", "supermarket"]

Restaurant = ["doordash", "skipthedishes", "restau", "a&w", "cuisine",
              "moxie's", "burger", "la belle patate", "pho", "pizza", "bestie",
              "kitchen", "thai", "el camino's", "grill", "ice cream", "japanese",
              "kaori izakaya", "taco", "mexican", "zipang provisions", "mr. steak", "poke", "sushi", "earl",
              "mcdonald's", "diner", "subway sandwiches", "falafel", "donair", "fish", "pizz", "poutine",
              "white spot", "vij's", "the capital", "cactus club", "cantina", "fork", "denny's", "mumbai local",
              "freshii", "captain's boil", "korean", "salade de fruits", "a & w", "ebisu", "mcdonald's", "cuchillo",
              "joe fortes", "the templeton", "freshii", "catering", "mary's", "meat & bread", "church's chicken",
              "rosemary rocksalt", "food", "deli", "red robin", "food", "snack", "banter room", "tap house", "lunch",
              "wings", "dairy queen", "tocador", "keg", "panago", "disco cheetah"]

Coffee = ["cafe", "coffee", "tim hortons", "starbucks", "bean", "birds & the beets", "the mighty oak",
          "le marche st george", "caffe", "coco et olive", "buro", "blenz", "green horn", "bakery", "revolver",
          "cardero bottega", "the anchor eatery", "savary island pie", "pie", "red umbrella",
          "di beppe", "cobs", "thierry", "marutama", "cartems", "faubourg"]

Bar = ["brew", "beer", "pub[^a-z]", "steamworks", "distillery", "bar[^a-z]", "narrow lounge", "rumpus room",
       "five point", "score on davie", "tap & barrel", "the cambie", "colony", "alibi room", "local ",
       "per se social corner", "grapes & soda", "portland craft", "the new oxford", "keefer", "liquor", "wine", "tapshack",
       "fox", "night club", "the pint", "the roxy", "commodore", "high tower management", "browns", "lounge", "mahony",
       "fountainhead"]

Bills = ["fido", "shaw", "fitness", "ymca", "bcaa", "digital ocean", "twilio", "soundcloud"]

TransportCarShare = ["car2go", "c2g", "evo *car *share"]
TransportRental = ["avis", "rentals", "petrocan", "husky", "[^a-z]esso", "super save", "shell"]
TransportCab = ["cab[^a-rt-z]", "taxi", "uber", "lyft"]
TransportTranslink = ["compass"]
TransportMisc = ["poparide", "amtrack", "boltbus"]
TransportCar = ["midas", "impark"]
Transport = TransportCarShare + TransportRental + TransportCab + TransportTranslink + TransportMisc + TransportCar
