def order_detail_cache_key(order_id):
    return f"orders:detail:{order_id}"


def order_management_detail_cache_key(order_id):
    return f"orders:management:detail:{order_id}"


def customer_orders_list_cache_key(user_id):
    return f"orders:customer:list:{user_id}"


def management_orders_list_cache_key():
    return "orders:management:list"


def management_orders_filtered_cache_key(params_hash):
    return f"orders:management:list:filtered:{params_hash}"