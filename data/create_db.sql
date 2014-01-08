-- PRAGMA synchronous=OFF, PRAGMA count_changes=OFF, PRAGMA journal_mode=OFF, PRAGMA locking_mode = EXCLUSIVE

create table nutrient (
-- Nutrient definition
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
  foods blob not null,  -- list of food ids (4-byte ints) (notice that using fixed-length char here makes no difference to record size in sqlite3)
  food_count integer not null,  -- the amount of food items in foods
  completeness double not null  -- completeness, ranging from 0.0 to 1.0
);

create table food (
-- Food and the nutrients it contains
  id integer primary key autoincrement not null,
  name varchar(255) not null,
  source_id int not null references source(id),
  price double,
  nutrient0 double,  -- contained amount of nutrient.unit per 100g of food
  nutrient1 double,
  nutrient2 double,
  nutrient3 double,
  nutrient4 double,
  nutrient5 double,
  nutrient6 double,
  nutrient7 double,
  nutrient8 double,
  nutrient9 double,
  nutrient10 double,
  nutrient11 double,
  nutrient12 double,
  nutrient13 double,
  nutrient14 double,
  nutrient15 double,
  nutrient16 double,
  nutrient17 double,
  nutrient18 double,
  nutrient19 double,
  nutrient20 double,
  nutrient21 double,
  nutrient22 double,
  nutrient23 double,
  nutrient24 double,
  nutrient25 double,
  nutrient26 double,
  nutrient27 double,
  nutrient28 double,
  nutrient29 double,
  nutrient30 double,
  nutrient31 double,
  nutrient32 double,
  nutrient33 double,
  nutrient34 double,
  nutrient35 double,
  nutrient36 double
);

create table profile (
-- A profile that describes a target daily dose of nutrients (and extrema)
  id integer primary key autoincrement not null,
  name varchar(255) not null,
  nutrient0_target double not null,  -- target amount of nutrient.unit per day
  nutrient0_max double not null,  -- max amount of nutrient.unit per day
  nutrient1_target double not null,
  nutrient1_max double not null,
  nutrient2_target double not null,
  nutrient2_max double not null,
  nutrient3_target double not null,
  nutrient3_max double not null,
  nutrient4_target double not null,
  nutrient4_max double not null,
  nutrient5_target double not null,
  nutrient5_max double not null,
  nutrient6_target double not null,
  nutrient6_max double not null,
  nutrient7_target double not null,
  nutrient7_max double not null,
  nutrient8_target double not null,
  nutrient8_max double not null,
  nutrient9_target double not null,
  nutrient9_max double not null,
  nutrient10_target double not null,
  nutrient10_max double not null,
  nutrient11_target double not null,
  nutrient11_max double not null,
  nutrient12_target double not null,
  nutrient12_max double not null,
  nutrient13_target double not null,
  nutrient13_max double not null,
  nutrient14_target double not null,
  nutrient14_max double not null,
  nutrient15_target double not null,
  nutrient15_max double not null,
  nutrient16_target double not null,
  nutrient16_max double not null,
  nutrient17_target double not null,
  nutrient17_max double not null,
  nutrient18_target double not null,
  nutrient18_max double not null,
  nutrient19_target double not null,
  nutrient19_max double not null,
  nutrient20_target double not null,
  nutrient20_max double not null,
  nutrient21_target double not null,
  nutrient21_max double not null,
  nutrient22_target double not null,
  nutrient22_max double not null,
  nutrient23_target double not null,
  nutrient23_max double not null,
  nutrient24_target double not null,
  nutrient24_max double not null,
  nutrient25_target double not null,
  nutrient25_max double not null,
  nutrient26_target double not null,
  nutrient26_max double not null,
  nutrient27_target double not null,
  nutrient27_max double not null,
  nutrient28_target double not null,
  nutrient28_max double not null,
  nutrient29_target double not null,
  nutrient29_max double not null,
  nutrient30_target double not null,
  nutrient30_max double not null,
  nutrient31_target double not null,
  nutrient31_max double not null,
  nutrient32_target double not null,
  nutrient32_max double not null,
  nutrient33_target double not null,
  nutrient33_max double not null,
  nutrient34_target double not null,
  nutrient34_max double not null,
  nutrient35_target double not null,
  nutrient35_max double not null,
  nutrient36_target double not null,
  nutrient36_max double not null
);

INSERT INTO nutrient
VALUES
(0, "Calories", "kcal"),
(1, "Carbohydrates", "g"),
(2, "Protein", "g"),
(3, "Total Fat", "g"),
(4, "Omega-3 Fatty Acids", "g"),
(5, "Omega-6 Fatty Acids", "g"),
(6, "Total Fiber", "g"),
(7, "Cholesterol", "mg"),
(8, "Vitamin A", "IU"),
(9, "Vitamin B6", "mg"),
(10, "Vitamin B12", "ug"),
(11, "Vitamin C", "mg"),
(12, "Vitamin D", "IU"),
(13, "Vitamin E", "IU"),
(14, "Vitamin K", "ug"),
(15, "Thiamin", "mg"),
(16, "Riboflavin", "mg"),
(17, "Niacin", "mg"),
(18, "Folate", "ug"),
(19, "Pantothenic Acid", "mg"),
(20, "Biotin", "ug"),
(21, "Choline", "mg"),
(22, "Calcium", "g"),
(23, "Chloride", "g"),
(24, "Chromium", "ug"),
(25, "Copper", "mg"),
(26, "Iodine", "ug"),
(27, "Iron", "mg"),
(28, "Magnesium", "mg"),
(29, "Manganese", "mg"),
(30, "Molybdenum", "ug"),
(31, "Phosphorus", "g"),
(32, "Potassium", "g"),
(33, "Selenium", "ug"),
(34, "Sodium", "g"),
(35, "Sulfur", "g"),
(36, "Zinc", "mg");

-- using 9e999 as Infinity (didn't find a literal for infinity in sqlite3)
INSERT INTO profile
VALUES
(NULL, "My custom profile",
2500, 9e999,
400, 9e999,
120, 9e999,
65, 9e999,
0.75, 3.0,
1.5, 17,
40, 9e999,
0, 300,
5000, 10000,
2, 100,
6, 9e999,
60, 2000,
400, 4000,
30, 1500,
80, 9e999,
1.5, 9e999,
1.7, 9e999,
20, 35,
400, 1000,
10, 9e999,
300, 9e999,
550, 3500,
1, 2.5,
3.4, 9e999,
120, 600,
2, 10,
150, 1100,
18, 45,
400, 9e999,
2, 11,
75, 2000,
1, 4,
3.5, 6,
70, 400,
2.4, 2.4,
2, 9e999,
15, 40);
