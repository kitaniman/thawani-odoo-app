
def prepare_product_name(product_name):
    '''Pepare the name of a product to be sent to Thawani API'''
    if len(product_name) > 40:
        return product_name[:27] + '...'
    return product_name
