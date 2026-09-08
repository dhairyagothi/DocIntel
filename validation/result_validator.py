from models.relationship import Relationship


def valid_relationships(relationships: list[Relationship]) -> list[Relationship]:
    return [relationship for relationship in relationships if not relationship.validation_errors]