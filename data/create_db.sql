create table nutrient (
  id integer primary key autoincrement not null,
  name varchar(255) not null,
  unit varchar(10) not null
);

create table source (
  id integer primary key autoincrement not null,
  name varchar(255) not null
);

create table food (
  id integer primary key autoincrement not null,
  name varchar(255) not null,
  source_id int not null references source(id),
  price double,
  nutrient0 double,  -- nutrient.unit per 100g
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
