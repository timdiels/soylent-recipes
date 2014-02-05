create temp table food (
-- Food and the nutrients it contains
  id integer primary key autoincrement not null,
  name varchar(255) not null,
  source_id int not null references source(id),
  cluster_id int,
  price double,
  nutrient0 double not null,  -- contained amount of nutrient.unit per 100g of food
  nutrient1 double not null,
  nutrient2 double not null,
  nutrient3 double not null,
  nutrient4 double not null,
  nutrient5 double not null,
  nutrient6 double not null,
  nutrient7 double not null,
  nutrient8 double not null,
  nutrient9 double not null,
  nutrient10 double not null,
  nutrient11 double not null,
  nutrient12 double not null,
  nutrient13 double not null,
  nutrient14 double not null,
  nutrient15 double not null,
  nutrient16 double not null,
  nutrient17 double not null,
  nutrient18 double not null,
  nutrient19 double not null,
  nutrient20 double not null,
  nutrient21 double not null,
  nutrient22 double not null,
  nutrient23 double not null,
  nutrient24 double not null,
  nutrient25 double not null,
  nutrient26 double not null,
  nutrient27 double not null,
  nutrient28 double not null,
  nutrient29 double not null,
  nutrient30 double not null,
  nutrient31 double not null,
  nutrient32 double not null,
  nutrient33 double not null,
  nutrient34 double not null,
  nutrient35 double not null,
  nutrient36 double not null
);

-- Get rid of foods with no nutritional value
insert into temp.food
    select *
    from main.food
    where 0.0 <
      nutrient0 + nutrient1 + nutrient2 + nutrient3 + nutrient4 + nutrient5 +
      nutrient6 + nutrient7 + nutrient8 + nutrient9 + nutrient10 + nutrient11 +
      nutrient12 + nutrient13 + nutrient14 + nutrient15 + nutrient16 + nutrient17 +
      nutrient18 + nutrient19 + nutrient20 + nutrient21 + nutrient22 + nutrient23 +
      nutrient24 + nutrient25 + nutrient26 + nutrient27 + nutrient28 + nutrient29 +
      nutrient30 + nutrient31 + nutrient32 + nutrient33 + nutrient34 + nutrient35 +
      nutrient36;

delete from main.food;
delete from main.sqlite_sequence where name='food';

insert into main.food
    select NULL, name, source_id, cluster_id, price,
          nutrient0, nutrient1, nutrient2, nutrient3, nutrient4,
          nutrient5, nutrient6, nutrient7, nutrient8, nutrient9,
          nutrient10, nutrient11, nutrient12, nutrient13, nutrient14,
          nutrient15, nutrient16, nutrient17, nutrient18, nutrient19,
          nutrient20, nutrient21, nutrient22, nutrient23, nutrient24,
          nutrient25, nutrient26, nutrient27, nutrient28, nutrient29,
          nutrient30, nutrient31, nutrient32, nutrient33, nutrient34,
          nutrient35, nutrient36
    from temp.food;
