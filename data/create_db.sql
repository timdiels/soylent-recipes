-- PRAGMA synchronous=OFF, PRAGMA count_changes=OFF, PRAGMA journal_mode=OFF, PRAGMA locking_mode = EXCLUSIVE

create table nutrient (
-- Nutrient definition; TODO will also contain more general attributes like price, so will wnat to rename
  id integer primary key not null, -- starts at zero
  name varchar(255) not null,
  unit varchar(10) not null
);

create table source (
-- Source of a food
  id integer primary key autoincrement not null,
  name varchar(255) not null
);

create table recipe (
-- A list of food combinations, and their attainable completeness value
  id integer primary key autoincrement not null,
  completeness double not null  -- completeness, ranging from 0.0 to 1.0
);

create table recipe_food (
-- Food is part of recipe
  recipe_id integer not null,
  food_id integer not null,
  PRIMARY KEY(recipe_id, food_id)
);

create table recipe_cluster (
-- Food is part of recipe
  recipe_id integer not null,
  cluster_id integer not null,
  PRIMARY KEY(recipe_id, cluster_id)
);

create table food (
-- Food and the nutrients it contains
  id integer primary key autoincrement not null,
  name varchar(255) not null,
  source_id int not null references source(id),
  cluster_id int references cluster_(id)
);

create table food_attribute (
-- Maps food to attributes; most attributes are nutrient values (currently all of them are)
  food_id integer not null references food(id), 
  attribute_id integer not null,
  value double not null,  -- for a nutrient attrib: contained amount of nutrient.unit per 100g of food
  PRIMARY KEY(food_id, attribute_id)
);

create table profile (
-- A profile that describes a target daily dose of nutrients (and extrema)
  id integer primary key autoincrement not null,
  name varchar(255) not null
);

create table profile_attribute (
-- Maps profile to attributes
  profile_id integer not null references profile(id), 
  attribute_id integer not null,
  target_value double not null,  -- target amount of nutrient.unit per day
  max_value double not null,  -- max amount of nutrient.unit per day
  PRIMARY KEY(profile_id, attribute_id)
);

create table cluster_ (
-- A cluster of foods
  id integer primary key autoincrement not null
);

create table cluster_attribute (
-- Maps cluster to attributes
  cluster_id integer not null references cluster_(id), 
  attribute_id integer not null,
  value double not null,  -- average nutrient value of cluster
  PRIMARY KEY(cluster_id, attribute_id)
);

INSERT INTO nutrient
VALUES
(1, "Calories", "kcal"),
(2, "Carbohydrates", "g"),
(3, "Protein", "g"),
(4, "Total Fat", "g"),
(5, "Omega-3 Fatty Acids", "g"),
(6, "Omega-6 Fatty Acids", "g"),
(7, "Total Fiber", "g"),
(8, "Cholesterol", "mg"),
(9, "Vitamin A", "IU"),
(10, "Vitamin B6", "mg"),
(11, "Vitamin B12", "ug"),
(12, "Vitamin C", "mg"),
(13, "Vitamin D", "IU"),
(14, "Vitamin E", "IU"),
(15, "Vitamin K", "ug"),
(16, "Thiamin", "mg"),
(17, "Riboflavin", "mg"),
(18, "Niacin", "mg"),
(19, "Folate", "ug"),
(20, "Pantothenic Acid", "mg"),
(21, "Biotin", "ug"),
(22, "Choline", "mg"),
(23, "Calcium", "g"),
(24, "Chloride", "g"),
(25, "Chromium", "ug"),
(26, "Copper", "mg"),
(27, "Iodine", "ug"),
(28, "Iron", "mg"),
(29, "Magnesium", "mg"),
(30, "Manganese", "mg"),
(31, "Molybdenum", "ug"),
(32, "Phosphorus", "g"),
(33, "Potassium", "g"),
(34, "Selenium", "ug"),
(35, "Sodium", "g"),
(36, "Sulfur", "g"),
(37, "Zinc", "mg");

-- using 9e999 as Infinity (didn't find a literal for infinity in sqlite3)
INSERT INTO profile
VALUES (1, "My custom profile");

INSERT INTO profile_attribute
VALUES
(1, 1, 2500, 9e999),
(1, 2, 400, 9e999),
(1, 3, 120, 9e999),
(1, 4, 65, 9e999),
(1, 5, 0.75, 3.0),
(1, 6, 1.5, 17),
(1, 7, 40, 9e999),
(1, 8, 0, 300),
(1, 9, 5000, 10000),
(1, 10, 2, 100),
(1, 11, 6, 9e999),
(1, 12, 60, 2000),
(1, 13, 400, 4000),
(1, 14, 30, 1500),
(1, 15, 80, 9e999),
(1, 16, 1.5, 9e999),
(1, 17, 1.7, 9e999),
(1, 18, 20, 35),
(1, 19, 400, 1000),
(1, 20, 10, 9e999),
(1, 21, 300, 9e999),
(1, 22, 550, 3500),
(1, 23, 1, 2.5),
(1, 24, 3.4, 9e999),
(1, 25, 120, 600),
(1, 26, 2, 10),
(1, 27, 150, 1100),
(1, 28, 18, 45),
(1, 29, 400, 9e999),
(1, 30, 2, 11),
(1, 31, 75, 2000),
(1, 32, 1, 4),
(1, 33, 3.5, 6),
(1, 34, 70, 400),
(1, 35, 2.4, 2.4),
(1, 36, 2, 9e999),
(1, 37, 15, 40);
