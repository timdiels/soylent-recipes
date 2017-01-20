Ideas
=====

Ideas for the future

Link food data to shop products
-------------------------------
For the resulting recipe to be practical, the foods should correspond to
products you can buy in a few stores near to you. To enable this, another input
data file could be added to allow you to specify a mapping from foods in the
nutrition database to products available in the stores you would consider
buying from. It would also be a good idea to leave out any products you simply
would never buy as you make this mapping.

Then, the output could list actual products to buy in stores. Additionally, you
could specify the price of each product such that the algorithm can minimize
the total price of the recipe as well.

Expiration dates
----------------
When wanting to buy in bulk, expiration dates become important. If this data is
somehow provided for shop products, a minimum constraint could be added on
expiration date. This is under the assumption that combining foods does not
affect expiration date (if it does, you could try keeping them separate).

Improving taste of recipes
--------------------------
Allow inputting a recipes from a previous search with some foods marked.
Marked foods will be replaced with random different foods that also make for a
solved recipe. This may help in getting recipes that don't taste too bad.

More food databases
-------------------
The USDA database probably mostly covers food that Americans eat. For food
specific to your country, you may want to use a different food database or a
combination of databases. Support for other food databases could be added.

EU food databases can be found at:
http://www.eurofir.org/food-information/food-composition-databases-2/
