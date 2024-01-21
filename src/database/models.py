from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class FlashcardSet(Base):
    __tablename__ = 'flashcard_sets'

    id = Column(Integer, primary_key=True,
                autoincrement=True)
    name = Column(String)
    course_name = Column(String, default=None)

    flashcards = relationship("Flashcard",
                              back_populates="set")


class Flashcard(Base):
    __tablename__ = 'flashcards'

    id = Column(Integer, primary_key=True,
                autoincrement=True)
    term = Column(Text)
    definition = Column(Text)
    exclude = Column(Boolean, default=False)

    course_name = Column(String, default=None)
    # do not delete flashcards when the set is deleted
    set_id = Column(Integer, ForeignKey('flashcard_sets.id',
                                        ondelete="SET NULL"))

    set = relationship("FlashcardSet", back_populates="flashcards")

    def __repr__(self):
        return f"<Flashcard(term='{self.term}', definition='{self.definition}', exclude={self.exclude})>"

    def __str__(self):
        return f"{self.term}: {self.definition}"

    def __eq__(self, other):
        if isinstance(other, Flashcard):
            return self.term == other.term and self.definition == other.definition
        else:
            return False

    def __hash__(self):
        return hash((self.term, self.definition))
