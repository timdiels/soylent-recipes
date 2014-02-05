#!/usr/bin/sh

# TODO grab O3 and other things that are missing in abbrev

cat << EOF
create temp table food (
NDB_No varchar(5),
FdGrp_Cd varchar(4),
Long_Desc varchar(200),
Shrt_Desc varchar(60),
ComName varchar(100),
ManufacName varchar(65),
Survey varchar(1),
Ref_desc varchar(135),
Refuse decimal(2, 0),
SciName varchar(65),
N_Factor decimal(4, 2),
Pro_Factor decimal(4, 2),
Fat_Factor decimal(4, 2),
CHO_Factor decimal(4, 2)
);

create temp table abbrev (
NDB_No varchar(5),
Shrt_Desc varchar(60),
Water decimal(10,2),
Energ_Kcal decimal(10,0),
Protein decimal(10,2),
Lipid_Tot decimal(10,2),
Ash decimal(10,2),
Carbohydrt decimal(10,2),
Fiber_TD decimal(10, 1),
Sugar_Tot decimal(10,2),
Calcium decimal(10,0),
Iron decimal(10,2),
Magnesium decimal(10,0),
Phosphorus decimal(10,0),
Potassium decimal(10,0),
Sodium decimal(10,0),
Zinc decimal(10,2),
Copper decimal(10, 3),
Manganese decimal(10, 3),
Selenium decimal(10, 1),
Vit_C decimal(10, 1),
Thiamin decimal(10, 3),
Riboflavin decimal(10, 3),
Niacin decimal(10, 3),
Panto_acid decimal(10, 3),
Vit_B6 decimal(10, 3),
Folate_Tot decimal(10,0),
Folic_acid decimal(10,0),
Food_Folate decimal(10,0),
Folate_DFE decimal(10,0),
Choline_Tot decimal(10,0),
Vit_B12 decimal(10,2),
Vit_A_IU decimal(10,0),
Vit_A_RAE decimal(10,0),
Retinol decimal(10,0),
Alpha_Carot decimal(10,0),
Beta_Carot decimal(10,0),
Beta_Crypt decimal(10,0),
Lycopene decimal(10,0),
LutZea decimal(10,0),
Vit_E decimal(10,2),
Vit_D_mcg decimal(10, 1),
Vit_D_IU decimal(10,0),
Vit_K decimal(10, 1),
FA_Sat decimal(10, 3),
FA_Mono decimal(10, 3),
FA_Poly decimal(10, 3),
Cholestrl decimal(10, 3),
GmWt_1 decimal(9, 2),
GmWt_Desc1 varchar(120),
GmWt_2 decimal(9, 2),
GmWt_Desc2 varchar(120),
Refuse_Pct decimal(2)
);

EOF

format() {
  sed 's///g' | sed 's/"/""/g' | sed 's/\^$/\^NULL/g' | sed 's/\^\^/\^NULL\^/g' | sed 's/\^\^/\^NULL\^/g' | sed 's/~/"/g' | sed 's/\^/, /g' | sed 's/$/\);/'
}

cat FOOD_DES.txt | format | sed 's/^/INSERT INTO temp.food VALUES \(/'

cat ABBREV.txt | format | sed 's/^/INSERT INTO temp.abbrev VALUES \(/'

cat << EOF

INSERT INTO source(name) VALUES('USDA SR26');

INSERT INTO main.food
SELECT NULL, shrt_desc, 1, NULL, NULL, 
        IFNULL(energ_kcal, 0),
        IFNULL(carbohydrt, 0),
        IFNULL(protein, 0),
        IFNULL(lipid_tot, 0),
        IFNULL(NULL, 0),
        IFNULL(NULL, 0),
        IFNULL(Fiber_TD, 0),
        IFNULL(cholestrl, 0),
        IFNULL(vit_a_iu, 0),
        IFNULL(vit_b6, 0),
        IFNULL(vit_b12, 0),
        IFNULL(vit_c, 0),
        IFNULL(vit_d_iu, 0),
        IFNULL(NULL, 0),
        IFNULL(vit_k, 0),
        IFNULL(thiamin, 0),
        IFNULL(riboflavin, 0),
        IFNULL(niacin, 0),
        IFNULL(folate_tot, 0),
        IFNULL(panto_acid, 0),
        IFNULL(NULL, 0),
        IFNULL(choline_tot, 0),
        IFNULL(calcium/1000, 0),
        IFNULL(NULL, 0),
        IFNULL(NULL, 0),
        IFNULL(copper, 0),
        IFNULL(NULL, 0),
        IFNULL(iron, 0),
        IFNULL(magnesium, 0),
        IFNULL(manganese, 0),
        IFNULL(NULL, 0),
        IFNULL(phosphorus/1000, 0),
        IFNULL(potassium/1000, 0),
        IFNULL(selenium, 0),
        IFNULL(sodium/1000, 0),
        IFNULL(NULL, 0),
        IFNULL(zinc, 0)
  FROM temp.abbrev;

EOF
# TODO carbohydrate, by difference = ???
# Total dietary fiber = Total fiber?
# vit_e is in mg, but we need it in IU
# do we need to take into account that refuse thing?
# missing: biotin, Omega3, Omega6, chloride, chromium, iodine, molybdenum, sulfur
# does rounding occur erroneously at calcium, phosphorus, potassium, sodium field?

#TODO stop script on error
