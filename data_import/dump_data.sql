.output lindcraft_category.sql
.mode insert category
select * from lindcraft_category;
.output lindcraft_product.sql
.mode insert product
select * from lindcraft_product;
.output lindcraft_model.sql
.mode insert model
select * from lindcraft_model;
.mode list
.output
