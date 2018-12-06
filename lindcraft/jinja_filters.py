

def small_product_image(path):
    """Modify the name of the image path to find the smaller image"""
    return path.replace('.jpg','_sm.jpg')
    
    
def register_jinja_filters(app):
    # register the filters
    app.jinja_env.filters['small_product_image'] = small_product_image
