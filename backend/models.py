from email.policy import default
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    LargeBinary,
    DateTime,
    select,
)
from sqlalchemy.orm import relationship

# from sqlalchemy_utils import create_view

from database import Base
from pathlib import Path


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    executable = Column(String, index=True, nullable=False)
    steam_grid_id = Column(Integer, index=True, nullable=False)
    last_played = Column(DateTime, index=True, nullable=True, default=None)
    parent_directory = Column(String, index=True, nullable=False)

    pictures = relationship("Picture", back_populates="game")
    category = relationship("Category", back_populates="games")

    def __repr__(self):
        return f"<Game(name='{self.name}')>"

    def as_dict(self):
        return {
            "name": self.name,
            "category": self.category.name,
            "last_played": self.last_played,
            "pictures": [picture.picture for picture in self.pictures],
        }


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    games = relationship("Game", back_populates="category")

    def __repr__(self):
        return f"<Category(name='{self.name}')>"

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "games": [game.as_dict() for game in self.games],
        }


class LookupFolder(Base):
    __tablename__ = "lookup_folders"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True, nullable=False)

    def __repr__(self):
        return f"<LookupFolder(location='{self.location}')>"

    def as_dict(self):
        return {
            "id": self.id,
            "location": self.location,
        }


class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True, index=True)
    picture = Column(LargeBinary, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)

    game = relationship("Game", back_populates="pictures")

    def __repr__(self):
        return f"<Picture(picture='{self.picture}')>"

    def as_dict(self):
        return {
            "id": self.id,
            "picture": self.picture,
        }


# create a view that holds the 5 last played games
# stmt = select([Game.name, Game.last_played]).order_by(Game.last_played.desc()).limit(5)
# view = create_view("last_played_games", stmt, Base.metadata)


# class LastPlayedGameView(Base):
#     __table__ = view

#     def __repr__(self):
#         return f"<LastPlayedGame(name='{self.name}', last_played='{self.last_played}')>"

#     def as_dict(self):
#         return {
#             "name": self.name,
#             "last_played": self.last_played,
#         }
