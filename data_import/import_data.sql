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
.print "Switching to new data file"
.open database.sqlite
delete from category;
.read lindcraft_category.sql
delete from product;
.read lindcraft_product.sql
-- remove the leading slash
update product set image_path = substr(image_path,2);
delete from model;
.read lindcraft_model.sql
.print "Import complete. Now using file database.sqlite"

