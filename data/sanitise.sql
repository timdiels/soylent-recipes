-- Get rid of foods with no nutritional value
delete from main.food
where id not in (SELECT id 
                 FROM food f
                 INNER JOIN food_attribute fa 
                 ON fa.food_id = f.id
                 where value != 0.0);
