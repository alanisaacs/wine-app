#!/usr/bin/env python3

"""Populate sample data into the Wine App"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from models import User, Country, Wine
 
# FOR RUNNING LOCALLY
engine = create_engine('sqlite:///wines.db')
# FOR WSGI ON APACHE
#engine = create_engine('postgresql://catalog:catalog@localhost/wines')
DBSession = sessionmaker(bind=engine)
session = DBSession()


user1 = User(
    id = 1,
    name = "Alan Isaacs",
    email = "xtrasenz@gmail.com",
    picture = ""
)
user2 = User(
    id = 2,
    name = "Chiho Martin",
    email = "chihomartin@gmail.com",
    picture = ""
)

country1 = Country(name = "France")
country2 = Country(name = "Italy")
country3 = Country(name = "USA")
country4 = Country(name = "Germany")
country5 = Country(name = "Australia")

session.add(country1)
session.add(country2)
session.add(country3)
session.add(country4)
session.add(country5)
session.commit()


wine1 = Wine(
    country_id = 1, 
    country = country1,
    description = "K&L: Located in St-Loubes and situated on the shoreline of the Dordogne River. The soils are clay and light limestone with a subsoil of red pebbles and clay. The blend is 50% Cabernet Sauvignon, 30% Merlot, and 20% Cabernet Franc. It was aged for 18 months in large vats and then an additional 6 months in oak.", 
    id = 1, 
    name = "Bois-Malot, Bordeaux Sup\u00e9rieur", 
    price = "29.99", 
    rating = 90, 
    year = 2017,
    user_id = 1,
    user = user1
    )
session.add(wine1)
session.commit()

wine2 = Wine(
    country_id = 2, 
    country = country2,
    description = "Wine Spectator: Cherry, leather and iron notes mark this suave, elegant red.", 
    id = 2, 
    name = "Altesino", 
    price = "39.99", 
    rating = 92, 
    year = 2012,
    user_id = 2,
    user = user2
    )
session.add(wine2)
session.commit()

wine3 = Wine(
    country_id = 3,
    country = country3,
    description = "Winemaker: This is a layered and refined expression of our Liparita Cabernet, still powerful, but with an active mid-palate and spacious freshness on the finish.", 
    id = 3, 
    name = "Liparita \\\"V Block\\\" Yountville Cabernet Sauvignon", 
    price = "19.99", 
    rating = 89, 
    year = 2014,
    user_id = 1,
    user = user1
    )
session.add(wine3)
session.commit()

wine4 = Wine(
    country_id = 4,
    country = country4,
    description = "Vinous: Bright straw-yellow. Intensely perfumed aromas of lime, peach, quinine and talc, complicated by notes of lemon verbena and jasmine.", 
    id = 4, 
    name = "Julien Schaal \\\"Schoenenbourg Gypse\\\" Riesling Grand Cru Alsace", 
    price = "19.99", 
    rating = 95, 
    year = 2017,
    user_id = 1,
    user = user1
    )
session.add(wine4)
session.commit()

wine5 = Wine(
    country_id = 3,
    country = country3,
    description = "Jancis Robinson: Big and bold and chewy finish. Very graceful. Not a bruiser. Quite elegant. More intense than the 1991.", 
    id = 5, 
    name = "Opus One Napa Valley Bordeaux Blend", 
    price = "359.99", 
    rating = 94, 
    year = 1994,
    user_id = 1,
    user = user1
    )
session.add(wine5)
session.commit()

wine6 = Wine(
    country_id = 1,
    country = country1, 
    description = "K&L: The Sancerre is consistently delicious, with citrus, chalky mineral and light floral notes. Its dry finish complements seafood and cheese beautifully.", 
    id = 6, 
    name = "Domaine Cherrier P\\u00e8re & Fils Sancerre", 
    price = "17.99", 
    rating = 88, 
    year = 2017,
    user_id = 1,
    user = user1
    )
session.add(wine6)
session.commit()

wine7 = Wine(
    country_id = 5,
    country = country5,
    description = "James Halliday: Deep, dense colour; saturated blackberry, plum and black cherry fruit; ripe tannins and lots of complementary oak. Needs patience.", 
    id = 7, 
    name = "Kalleske \\\"Greenock\\\" Shiraz Barossa Valley South Australia", 
    price = "34.99", 
    rating = 94, 
    year = 2004,
    user_id = 1,
    user = user1
    )
session.add(wine7)
session.commit()

wine8 = Wine(
    country_id = 4,
    country = country4,
    description = "James Suckling: The whiff of smoke gives the cassis nose of this wine an extra dimension. Concentrated and racy with a dangerous amount of energy. So juicy and vibrant with a long and very clean finish.", 
    id = 8, 
    name = "M\u00fcller-Catoir Haardt Scheurebe Trocken", 
    price = "29.99", 
    rating = 93, 
    year = 2017,
    user_id = 1,
    user = user1
    )
session.add(wine8)
session.commit()

wine9 = Wine(
    country_id = 1, 
    country = country1,
    description = "Wine Spectator: Shows the bright, ripe and racy profile of the vintage, with pure raspberry and blackberry fruit streaming through, offering a pretty violet edge and staying light-footed throughout.", 
    id = 9, 
    name = "Malmont C\u00f4tes du Rh\u00f4ne", 
    price = "17.99", 
    rating = 88, 
    year = 2018,
    user_id = 1,
    user = user1
    )
session.add(wine9)
session.commit()
session.close()

print('Wine data added.')