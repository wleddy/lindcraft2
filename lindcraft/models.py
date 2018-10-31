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
            name TEXT UNIQUE NOT NULL,
            desc TEXT,
            image_path TEXT,
            display_order INTEGER DEFAULT 0,
            cat_id INTEGER,
            
            FOREIGN KEY (cat_id) REFERENCES category(id) ON DELETE CASCADE"""
            
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()


class Model(SqliteTable):
    """A product item has one or more Models or versions of the product"""
    
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'model'
        #self.order_by_col = 'id'
        """ ordering =['product__category__displayOrder','model'] """
        
        self.defaults = {}
        
    def create_table(self):
        """Define and create the Model table"""
        
        sql = """
            model TEXT UNIQUE NOT NULL,
            desc TEXT,
            size TEXT,
            bike_cnt INTEGER DEFAULT 1,
            price NUMBER DEFAULT 0,
            active NUMBER DEFAULT 1,
            price_change_date DATETIME,
            prod_id INTEGER,
            
            FOREIGN KEY (prod_id) REFERENCES product(id) ON DELETE CASCADE"""
            
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()


def init_db(db):
    """Create a intial database."""
    Category(db).init_table()
    Product(db).init_table()
    Model(db).init_table()
