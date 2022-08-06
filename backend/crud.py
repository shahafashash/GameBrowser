from pathlib import Path
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models


def create_game(
    db: Session, name: str, category: str, executable: str, steam_grid_id: int
) -> models.Game:
    """Creates a new game in the database if it doesn't exist.
    Args:
        db: The database session.
        name (str): The name of the game.
        category (str): The category of the game.
        executable (str): The executable of the game.
        steam_grid_id (int): The app id of the game in SteamGridDB.
    Returns:
        models.Game: The game that was created.
    """
    # check if game exists
    game = (
        db.query(models.Game)
        .filter(models.Game.name == name and models.Game.category == category)
        .first()
    )
    if game:
        return game
    # get the category from the database
    category_obj = (
        db.query(models.Category).filter(models.Category.name == category).first()
    )
    if not category_obj:
        return None
    # create game
    game = models.Game(
        name=name,
        category_id=category_obj.id,
        executable=executable,
        steam_grid_id=steam_grid_id,
        parent_directory=str(Path(executable).parent),
    )
    db.add(game)
    db.commit()
    return game


def update_game(
    db: Session,
    game: models.Game,
    name: str = None,
    category: str = None,
    executable: str = None,
    steam_grid_id: int = None,
    last_played: datetime = None,
    parent_directory: str = None,
) -> models.Game:
    """Updates a game in the database.
    Args:
        db: The database session.
        game (models.Game): The game to update.
        name (str): The name of the game.
        category (str): The category of the game.
        executable (str): The executable of the game.
        steam_grid_id (int): The app id of the game in SteamGridDB.
        last_played (datetime): The last time the game was played.
        parent_directory (str): The parent directory of the game.
    Returns:
        models.Game: The game that was updated.
    """
    if name:
        game.name = name
    if category:
        game.category = category
    if executable:
        game.executable = executable
    if steam_grid_id:
        game.steam_grid_id = steam_grid_id
    if last_played:
        game.last_played = last_played
    if parent_directory:
        game.parent_directory = parent_directory
    else:
        game.parent_directory = str(Path(game.executable).parent)
    db.commit()
    return game


def delete_game(db: Session, game: models.Game) -> None:
    """Deletes a game from the database.
    Args:
        db: The database session.
        game (models.Game): The game to delete.
    """
    db.delete(game)
    db.commit()


def get_game(db: Session, name: str, category: str) -> models.Game:
    """Gets a game from the database.
    Args:
        db: The database session.
        name (str): The name of the game.
        category (str): The category of the game.
    Returns:
        models.Game: The game that was retrieved.
    """
    return (
        db.query(models.Game)
        .filter(models.Game.name == name and models.Game.category == category)
        .first()
    )


def get_all_games(db: Session) -> List[models.Game]:
    """Gets all games from the database.
    Args:
        db: The database session.
    Returns:
        List[models.Game]: The games that were retrieved.
    """
    return db.query(models.Game).all()


def get_executable(db: Session, name: str, category: str) -> str:
    """Gets the executable of a game from the database.
    Args:
        db: The database session.
        name (str): The name of the game.
        category (str): The category of the game.
    Returns:
        str: The executable of the game.
    """
    return (
        db.query(models.Game)
        .filter(models.Game.name == name and models.Game.category == category)
        .first()
        .executable
    )


def get_steam_grid_id(db: Session, name: str, category: str) -> int:
    """Gets the steam grid id of a game from the database.
    Args:
        db: The database session.
        name (str): The name of the game.
        category (str): The category of the game.
    Returns:
        int: The app id of the game.
    """
    return (
        db.query(models.Game)
        .filter(models.Game.name == name and models.Game.category == category)
        .first()
        .steam_grid_id
    )


def get_game_picture(db: Session, name: str, category: str) -> bytes:
    """_summary_
    Gets the picture of a game from the database.
    Args:
        db: The database session.
        name (str): The name of the game.
        category (str): The category of the game.
    Returns:
        bytes: The picture of the game.
    """
    # get the picture from the database
    pictures = (
        db.query(models.Game)
        .filter(models.Game.name == name and models.Game.category == category)
        .first()
        .pictures
    )
    # return the picture
    return pictures[0].picture


def get_executable_by_id(db: Session, id: int) -> str:
    """Gets the executable of a game from the database.
    Args:
        db: The database session.
        id (int): The id of the game.
    Returns:
        str: The executable of the game.
    """
    return db.query(models.Game).filter(models.Game.id == id).first().executable


def get_games_by_category(db: Session, category: str) -> List[models.Game]:
    """Gets all games from the database that are in a given category.
    Args:
        db: The database session.
        category (str): The category of the game.
    Returns:
        List[models.Game]: The games that were retrieved.
    """
    return db.query(models.Game).filter(models.Game.category == category).all()


def create_category(db: Session, name: str) -> models.Category:
    """Creates a new category in the database if it doesn't exist.
    Args:
        db: The database session.
        name (str): The name of the category.
    Returns:
        models.Category: The category that was created.
    """
    # check if category exists
    category = db.query(models.Category).filter(models.Category.name == name).first()
    if category:
        return category
    # create category
    category = models.Category(name=name)
    db.add(category)
    db.commit()
    return category


def update_category(
    db: Session, category: models.Category, name: str
) -> models.Category:
    """Updates a category in the database.
    Args:
        db: The database session.
        category (models.Category): The category to update.
        name (str): The name of the category.
    Returns:
        models.Category: The category that was updated.
    """
    category.name = name
    db.commit()
    return category


def delete_category(db: Session, category: models.Category) -> None:
    """Deletes a category from the database.
    Args:
        db: The database session.
        category (models.Category): The category to delete.
    """
    db.delete(category)
    db.commit()


def get_category(db: Session, name: str) -> models.Category:
    """Gets a category from the database.
    Args:
        db: The database session.
        name (str): The name of the category.
    Returns:
        models.Category: The category that was retrieved.
    """
    return db.query(models.Category).filter(models.Category.name == name).first()


def get_categories(db: Session) -> List[models.Category]:
    """Gets all categories from the database.
    Args:
        db: The database session.
    Returns:
        List[models.Category]: The categories that were retrieved.
    """
    return db.query(models.Category).all()


def get_category_by_id(db: Session, id: int) -> models.Category:
    """Gets a category from the database.
    Args:
        db: The database session.
        id (int): The id of the category.
    Returns:
        models.Category: The category that was retrieved.
    """
    return db.query(models.Category).filter(models.Category.id == id).first()


def create_picture(db: Session, picture: bytes, game_id: int) -> models.Picture:
    """Creates a new picture in the database if it doesn't exist.
    Args:
        db: The database session.
        picture (bytes): The picture to add.
        game_id (int): The id of the game.
    Returns:
        models.Picture: The picture that was created.
    """
    # check if picture exists
    db_picture = (
        db.query(models.Picture)
        .filter(models.Picture.game_id == game_id and models.Picture.picture == picture)
        .first()
    )
    if db_picture:
        return db_picture
    # create picture
    db_picture = models.Picture(picture=picture, game_id=game_id)
    db.add(db_picture)
    db.commit()
    return db_picture


def update_picture(
    db: Session, picture: models.Picture, picture_bytes: bytes
) -> models.Picture:
    """Updates a picture in the database.
    Args:
        db: The database session.
        picture (models.Picture): The picture to update.
        picture_bytes (bytes): The picture to update to.
    Returns:
        models.Picture: The picture that was updated.
    """
    picture.picture = picture_bytes
    db.commit()
    return picture


def delete_picture(db: Session, picture: models.Picture) -> None:
    """Deletes a picture from the database.
    Args:
        db: The database session.
        picture (models.Picture): The picture to delete.
    """
    db.delete(picture)
    db.commit()


def get_picture(db: Session, game_id: int) -> models.Picture:
    """Gets a picture from the database.
    Args:
        db: The database session.
        game_id (int): The id of the game.
    Returns:
        models.Picture: The picture that was retrieved.
    """
    return db.query(models.Picture).filter(models.Picture.game_id == game_id).first()


def create_lookup_folder(db: Session, location: str) -> models.LookupFolder:
    """Creates a new lookup folder in the database if it doesn't exist.
    Args:
        db: The database session.
        location (str): The location of the lookup folder.
    Returns:
        models.LookupFolder: The lookup folder that was created.
    """
    # check if lookup folder exists
    lookup_folder = (
        db.query(models.LookupFolder)
        .filter(models.LookupFolder.location == location)
        .first()
    )
    if lookup_folder:
        return lookup_folder
    # create lookup folder
    lookup_folder = models.LookupFolder(location=location)
    db.add(lookup_folder)
    db.commit()
    return lookup_folder


def update_lookup_folder(
    db: Session, lookup_folder: models.LookupFolder, location: str
) -> models.LookupFolder:
    """Updates a lookup folder in the database.
    Args:
        db: The database session.
        lookup_folder (models.LookupFolder): The lookup folder to update.
        location (str): The location of the lookup folder.
    Returns:
        models.LookupFolder: The lookup folder that was updated.
    """
    lookup_folder.location = location
    db.commit()
    return lookup_folder


def delete_lookup_folder(db: Session, lookup_folder: models.LookupFolder) -> None:
    """Deletes a lookup folder from the database.
    Args:
        db: The database session.
        lookup_folder (models.LookupFolder): The lookup folder to delete.
    """
    db.delete(lookup_folder)
    db.commit()


def get_lookup_folder(db: Session, location: str) -> models.LookupFolder:
    """Gets a lookup folder from the database.
    Args:
        db: The database session.
        location (str): The location of the lookup folder.
    Returns:
        models.LookupFolder: The lookup folder that was retrieved.
    """
    return (
        db.query(models.LookupFolder)
        .filter(models.LookupFolder.location == location)
        .first()
    )


def get_lookup_folders(db: Session) -> List[models.LookupFolder]:
    """Gets all lookup folders from the database.
    Args:
        db: The database session.
    Returns:
        List[models.LookupFolder]: The lookup folders that were retrieved.
    """
    return db.query(models.LookupFolder).all()
