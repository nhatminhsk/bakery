"""Store context and authorization helpers for multi-store system."""

from flask_login import current_user
from app.models.store import Store, StoreStaff
from app.extensions import db


def get_user_store(user_id=None):
    """Get the store assigned to a staff member.
    
    Args:
        user_id: The user ID (defaults to current_user.id if logged in)
    
    Returns:
        Store object if user is assigned to a store, None otherwise
    """
    if user_id is None:
        if current_user.is_anonymous:
            return None
        user_id = current_user.id
    
    assignment = StoreStaff.query.filter_by(user_id=user_id, is_active=True).first()
    if assignment:
        return assignment.store
    return None


def get_current_user_store():
    """Get the store for the current logged-in user.
    
    Returns:
        Store object if current_user is assigned to a store, None otherwise
    """
    if current_user.is_anonymous:
        return None
    return get_user_store(current_user.id)


def can_user_access_store(user_id, store_id):
    """Check if user can access a specific store.
    
    Admin can access all stores, staff can only access their assigned store.
    
    Args:
        user_id: The user ID
        store_id: The store ID
    
    Returns:
        True if user can access store, False otherwise
    """
    from app.models.user import User
    user = User.query.get(user_id)
    if not user:
        return False
    
    if user.is_admin():
        # Admin can access any store
        return True
    
    if user.is_staff():
        # Staff can only access their assigned store
        assignment = StoreStaff.query.filter_by(user_id=user_id, is_active=True).first()
        if assignment:
            return assignment.store_id == store_id
        return False
    
    return False


def filter_query_by_user_store(query, store_id_column, user_id=None):
    """Filter a query to only include data for user's accessible store.
    
    Args:
        query: SQLAlchemy query object to filter
        store_id_column: The column containing store_id (e.g., Product.store_id)
        user_id: The user ID (defaults to current_user.id)
    
    Returns:
        Filtered query
    """
    if user_id is None:
        if current_user.is_anonymous:
            return query.filter(store_id_column == None)  # No access
        user_id = current_user.id
    
    from app.models.user import User
    user = User.query.get(user_id)
    if not user:
        return query.filter(store_id_column == None)  # No access
    
    if user.is_admin():
        # Admin can see all stores
        return query
    
    if user.is_staff():
        # Staff can only see their assigned store
        user_store = get_user_store(user_id)
        if user_store:
            return query.filter(store_id_column == user_store.id)
        return query.filter(store_id_column == None)  # No access
    
    return query.filter(store_id_column == None)  # No access


def get_default_store_id():
    """Get the default store ID (for backward compatibility).
    
    Returns:
        Store ID for default store, or 1 if it exists
    """
    store = Store.query.filter_by(id=1).first()
    return store.id if store else None
