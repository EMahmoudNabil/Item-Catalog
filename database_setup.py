import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String,DateTime,func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    items = relationship("Item")


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'items': [item.serialize for item in self.items] 
        }
    



class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    last_modification = Column(DateTime, default=func.now())
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category,back_populates='items')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'last_modification': self.last_modification,
            'category_id': self.category_id,
            'user_id': self.user_id
        }
    



    


engine = create_engine('postgresql://catalog:1234@localhost/itemcatalogpsql')


Base.metadata.create_all(engine)