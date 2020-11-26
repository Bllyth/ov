from collections import defaultdict


def database_key_definitions(default):
    """
    All primary/foreign keys in Redash are of type `db.Integer` by default.
    You may choose to use different column types for primary/foreign keys. To do so, add an entry below for each model you'd like to modify.
    For each model, add a tuple with the database type as the first item, and a dict including any kwargs for the column definition as the second item.
    """
    definitions = defaultdict(lambda: default)
    definitions.update(
        {
            # "DataSource": (db.String(255), {
            #    "default": generate_key
            # })
        }
    )

    return definitions

# Since you can define custom primary key types using `database_key_definitions`, you may want to load certain extensions when creating the database.
# To do so, simply add the name of the extension you'd like to load to this list.
database_extensions = []