from takeabeltof.database import SqliteTable
from takeabeltof.utils import cleanRecordID
from users.views.password import getPasswordHash
        
class Category(SqliteTable):
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'category'
        self.order_by_col = 'display_order, name'
        self.defaults = {'display_order':0,}
        
    def create_table(self):
        """Define and create the Category table"""
        
        sql = """
            name TEXT UNIQUE NOT NULL,
            display_order INTEGER DEFAULT 0 """
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()

    def is_active(self,cat_id):
        """return True if there is at least one active product in this category"""
        
        sql = """
            select m.id from model as m
            join product as p on m.prod_id = p.id
            where m.active = 1 and p.cat_id = {}
        """.format(cleanRecordID(cat_id))
        #import pdb;pdb.set_trace()
        recs = self.db.execute(sql).fetchall()
        if recs:
            return True
            
        return False
        
    def select_active(self,**kwargs):
        """Return a namedlist of category recs that have at least one active model"""
    
        where = kwargs.get('where',1)
        order_by = kwargs.get('order_by',self.order_by_col)
        sql = """
        select distinct category.* from category
        join product on category.id = product.cat_id
        join model on model.prod_id = product.id
        where {} and model.active = 1
        order by {}
        """.format(where,order_by)
    
        return self.select_raw(sql)
    

class Product(SqliteTable):
    """A Product is a style of rack etc. It will have one or more models that
    will hold different numbers of bikes
    There is one Category associated with each model"""
        
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'product'
        self.order_by_col = 'display_order, name'
        self.defaults = {'display_order':0,}
        
    def create_table(self):
        """Define and create the Product table"""
        
        sql = """
            cat_id INTEGER,
            name TEXT UNIQUE NOT NULL,
            desc TEXT,
            image_path TEXT,
            display_order INTEGER DEFAULT 0,
            
            FOREIGN KEY (cat_id) REFERENCES category(id) ON DELETE CASCADE"""
            
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()

    def select_active(self,**kwargs):
        """Return a namedlist of product recs that have at least one active model"""
        
        where = kwargs.get('where',"")
        if len(where.strip()) > 0:
            where += " and "
        where += ' active = 1 '
            
        order_by = kwargs.get('order_by',self.order_by_col)
        sql = """
        select distinct p.* from product as p
        join model on model.prod_id = p.id
        where {}
        order by {}
        """.format(where,order_by)
        
        return self.select_raw(sql)

class Model(SqliteTable):
    """A product item has one or more Models or versions of the product"""
    
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'model'
        #self.order_by_col = 'id'
        """ ordering =['product__category__displayOrder','model'] """
        
        self.defaults = {"active":1,}
        self.order_by_col = 'model, id'
        
    def create_table(self):
        """Define and create the Model table"""
        
        sql = """
            prod_id INTEGER,
            model TEXT UNIQUE NOT NULL,
            desc TEXT,
            size TEXT,
            bike_cnt INTEGER DEFAULT 1,
            price NUMBER DEFAULT 0,
            price_change_date DATETIME,
            active NUMBER DEFAULT 1,
            
            FOREIGN KEY (prod_id) REFERENCES product(id) ON DELETE CASCADE"""
            
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()
        
    def select_active(self,**kwargs):
        """Return a list of named list objects but only active models"""
        where = kwargs.get('where','')
        order_by = kwargs.get('order_by',self.order_by_col)

        #import pdb;pdb.set_trace()
        if len(where.strip()) > 0:
            where += " and "
        where += ' active = 1 '
            
        kwargs.update({'where':where,'order_by':order_by,})
        return super().select(**kwargs)
        
    def update(self,rec,form,save=False):
        """The active field needs to be an int"""
        super().update(rec,form,save)
        if type(rec.active) is str or type(rec.active) is float:
            rec.active = int(rec.active)
            
            if save:
                self.save(rec)
            
            
def init_db(db):
    """Create a intial database."""
    Category(db).init_table()
    Product(db).init_table()
    Model(db).init_table()
