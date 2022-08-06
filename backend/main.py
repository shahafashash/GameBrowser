from sqlalchemy.orm import Session
import crud
import models
from database import SessionLocal, engine
import requests
from configparser import ConfigParser
from typing import Any, List, Dict, Union
from datetime import datetime
import subprocess
from pathlib import Path

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()


# For testing purposes only
# 1: empty the database
# 2: create 2 categories: 'VR' and 'PC'
def empty_database(db: Session) -> None:
    """Empties the database.
    Args:
        db: The database session.
    """
    db.query(models.Game).delete()
    db.query(models.Category).delete()
    db.query(models.Picture).delete()
    db.query(models.LookupFolder).delete()
    db.commit()


def create_2_categories(db: Session) -> None:
    """Creates 2 categories in the database.
    Args:
        db: The database session.
    """
    crud.create_category(db, "VR")
    crud.create_category(db, "PC")
    db.commit()


def add_lookup_folders(db: Session) -> None:
    """Adds lookup folders to the database.
    Args:
        db: The database session.
    """
    crud.create_lookup_folder(db, "D:\SteamLibrary\steamapps\common")
    crud.create_lookup_folder(db, "D:\EpicGamesLibrary")


class BrowserBackend:
    def __init__(self, db: Session) -> None:
        # create a config parser
        self.config: ConfigParser = ConfigParser()
        # read the config file
        self.config.read("config.ini")
        # get the api key from the config file
        self.__api_key: str = self.config["STEAM_GRID_DB"]["api_key"]
        self.db: Session = db

        # create all the tables if they don't exist
        models.Base.metadata.create_all(bind=engine)
        # update the database with the games from the lookup folders
        self.update_games()

    @property
    def api_key(self) -> str:
        return self.__api_key

    @api_key.setter
    def api_key(self, _: Any) -> None:
        raise AttributeError("Cannot change API key")

    def _get_game_picture_from_steam_grid(self, steam_grid_id: int) -> bytes:
        auth_header = {"Authorization": f"Bearer {self.api_key}"}
        query_parameters = {
            "dimensions": ["600x900"],
            "mimes": ["image/png"],
            "types": ["static"],
            "nsfw": "false",
            "humor": "false",
        }
        base_url = "https://www.steamgriddb.com/api/v2"
        url = f"{base_url}/grids/game/{steam_grid_id}"
        response = requests.get(url, headers=auth_header, params=query_parameters)
        # check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Error: {response}")
        # get the picture from the response
        results = response.json()["data"]
        for res in results:
            # check if the 'url' field is not empty
            if res["url"] != "":
                # get the picture from the url
                response = requests.get(res["url"])
                # check if the request was successful
                if response.status_code != 200:
                    raise Exception(f"Error: {response}")
                # return the picture
                return response.content
        # if no picture was found return empty bytes
        return bytes()

    def _get_game_id_from_steam_grid(self, name: str) -> int:
        auth_header = {"Authorization": f"Bearer {self.api_key}"}
        url = f"https://www.steamgriddb.com/api/v2/search/autocomplete/{name}"
        response = requests.get(url, headers=auth_header)
        # check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Error: {response}")
        # get the game id from the response
        results = response.json()["data"]
        for res in results:
            # check that the game name matches the name of the game
            if res["name"] == name:
                # return the game id
                return res["id"]
        # if no game was found return -1
        return -1

    def _add_game_picture(self, name: str, category: str) -> None:
        # get the game from the database
        game = crud.get_game(db, name, category)
        if game is None:
            # create the game if it doesn't exist
            game = crud.create_game(db, name, category)

    # TODO: Fix this function
    def _collect_games_from_folder(
        self, lookup_folder: str
    ) -> List[Dict[str, Union[str, int]]]:
        # resolve the path
        resolved_path = Path(lookup_folder).resolve()
        # recursively get all the '.exe' files in the folder only one level deep
        exe_files = resolved_path.rglob("*.exe")
        # get the names of the games if the file is of type 'Application'
        applications = {
            exe_file.name: exe_file
            for exe_file in exe_files
            if exe_file.stat().st_mode & 0o111 == 0o111
        }
        # creating a dictionary with the game name as key and as a value - a dictionary with 'executable', 'steam_grid_id' and 'category' as keys
        games = {
            game_name: {"executable": None, "steam_grid_id": None, "category": None}
            for game_name in applications
        }

        # for each game in the dictionary, try to get the game id from steam grid. If the game id is not found, the game is not in steam grid and is removed from the dictionary
        to_remove = []
        for game_name in games:
            print(f'Looking up "{game_name}": ', end="")
            steam_grid_id = self._get_game_id_from_steam_grid(game_name)
            if steam_grid_id == -1:
                print("FAILED")
                to_remove.append(game_name)
            else:
                print(f"SUCCESS ({steam_grid_id})")
                games[game_name]["steam_grid_id"] = steam_grid_id
                games[game_name]["executable"] = applications[game_name]
                games[game_name]["category"] = (
                    "VR" if game_name.lower().endswith("vr") else "PC"
                )  # TODO: add a check for VR games because this is a temporary solution

        # remove the games that were not found in steam grid
        for game_name in to_remove:
            del games[game_name]
        return games

    def add_new_game(
        self, name: str, category: str, executable: str, steam_grid_id: int = None
    ) -> None:
        """Adds a new game to the database.

        Args:
            name (str): The name of the game.
            category (str):  The category of the game.
            executable (str):  The executable of the game.
            steam_grid_id (int, optional):  The steam grid id of the game. Defaults to None.

        Raises:
            Exception: If the game already exists.
            Exception: If the game doesn't exist in Steam Grid DB.
        """
        if steam_grid_id is None:
            # get the game id from steam grid
            steam_grid_id = self._get_game_id_from_steam_grid(name)
        # get the game picture from steam grid
        picture = self._get_game_picture_from_steam_grid(steam_grid_id)
        # add the game to the database
        game = crud.create_game(db, name, category, executable, steam_grid_id)
        # check that the game was created
        if game is None:
            raise Exception(f"Error while creating game {name}")
        # check if the game picture was found
        if picture == bytes():
            # remove the game if the picture was not found
            crud.delete_game(db, game.id)
            raise Exception(f"Error while getting game picture for {name}")

        # add the game picture to the database
        crud.create_picture(db, picture, game.id)

    def get_game_picture(self, name: str, category: str) -> bytes:
        """Gets the picture of a game.

        Args:
            name (str): The name of the game.
            category (str):  The category of the game.

        Returns:
            bytes: The picture of the game.

        Raises:
            Exception: If the game doesn't exist in the database.
        """
        # get the game from the database
        game = crud.get_game(db, name, category)
        if game is None:
            raise Exception(f"Game {name} doesn't exist in the database")
        # get the game picture from the database
        picture = crud.get_picture(db, game.id)
        if picture is None:
            raise Exception(f"Game {name} doesn't have a picture")
        # return the picture
        return picture.picture

    def launch_game(self, name: str, category: str) -> None:
        """Launches a game.

        Args:
            name (str): The name of the game.
            category (str):  The category of the game.

        Raises:
            Exception: If the game doesn't exist in the database.
            Exception: If the game fails to launch.
        """
        # get the game from the database
        game = crud.get_game(db, name, category)
        if game is None:
            raise Exception(f"Game {name} doesn't exist in the database")
        # update the last played date
        crud.update_game(db, game, last_played=datetime.now())
        # launch the game
        try:
            subprocess.check_call(game.executable, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error while launching game {name}: {e}")

    def add_lookup_folder(self, folder: str) -> None:
        """Adds a folder to the lookup folders table.
        All the games in the lookup folder will be added to the database
        every time the program is run.
        """
        # get the games from the folder
        games = self._collect_games_from_folder(folder)
        # add the games to the database
        for game_name, game_data in games.items():
            self.add_new_game(
                game_name,
                game_data["category"],
                game_data["executable"],
                game_data["steam_grid_id"],
            )

    def update_games(self) -> None:
        """Updates the games in the database.
        All the games in the lookup folders will be added to the database
        every time the program is run.
        """
        # get the lookup folders from the database
        lookup_folders = crud.get_lookup_folders(db)
        # for each lookup folder, add the games to the database
        games = {}
        for lookup_folder in lookup_folders:
            games.update(self._collect_games_from_folder(lookup_folder.location))
        # for each game in the database, check if it exists in the lookup folders.
        # If it doesn't exist, delete it from the database. If it does exist, update the executable and parent folder.
        db_games = crud.get_all_games(db)
        for game in db_games:
            if game.name not in games:
                crud.delete_game(db, game.id)
            else:
                crud.update_game(
                    db,
                    game,
                    executable=games[game.name]["executable"],
                    parent_folder=Path(games[game.name]["executable"]).parent,
                )

        # add the new games to the database
        db_games_names = [game.name for game in db_games]
        for game_name, game_data in games.items():
            if game_name not in db_games_names:
                breakpoint()
                self.add_new_game(
                    game_name,
                    game_data["category"],
                    game_data["executable"],
                    game_data["steam_grid_id"],
                )

    # def get_last_played(self) -> List[str]:
    #     return list(map(lambda x: x.as_dict(), models.LastPlayedGameView.query.all()))


if __name__ == "__main__":
    empty_database(db)
    create_2_categories(db)
    add_lookup_folders(db)
    backend = BrowserBackend(db)
