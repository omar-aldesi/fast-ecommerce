from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


def get_or_create(session: Session, model, defaults=None, **kwargs):
    """
    Get an instance of the model or create it if it doesn't exist.

    Args:
        session (Session): The SQLAlchemy session.
        model (Base): The SQLAlchemy model.
        defaults (dict, optional): A dictionary of default values to set on the instance. Defaults to None.
        **kwargs: The fields to filter by.

    Returns:
        tuple: A tuple of (instance, created), where created is a boolean indicating whether the instance was created.
    """
    defaults = defaults or {}
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False

    params = {**kwargs, **defaults}
    instance = model(**params)

    try:
        session.add(instance)
        session.commit()
        return instance, True
    except IntegrityError:
        session.rollback()
        instance = session.query(model).filter_by(**kwargs).first()
        return instance, False

# Example usage
# Assuming you have a User model and a session instance

# from your_project.models import User
# from your_project.database import session

# user, created = get_or_create(session, User, email='user@example.com', defaults={'name': 'John Doe'})
# if created:
#     print("User created:", user)
# else:
#     print("User already exists:", user)
