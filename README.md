# Item Catalog
An application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Getting Started
### prerequisites

Item Catalog requires the following to run:

* [VirtualBox](https://www.virtualbox.org/wiki/Downloads) the software that actually runs the virtual machine.
* [Vagrant](https://www.vagrantup.com/downloads.html) is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.


### Installing
* First clone the project and virtal machine repository
```
$ git clone https://github.com/AboSalaah/fullstack-nanodegree-vm.git
```
### Running the code
* Change to a folder called vagrant inside the cloned repository
```
$ cd ../cloned_repository/vagrant
```
* Start the virtual machine.
```
$ vagrant up
```
This will cause Vagrant to download the Linux operating system and install it.

* run ```vagrant ssh``` to log in to 
your newly installed Linux VM.
```
$ vagrant ssh
```

* Change folder to /vagrant to access the portion that is shared between your machine and the virtual machine
```
$ cd /vagrant
```
* Change folder to /catalog folder which contains the project installed and run the server
```
$ cd .../catalog
python database_setup.py // to setup the tables and relations of the database
$ python fill_database.py // to fill the database with dummy data 
$ python server.py
```
### API endpoints
* GET localhost:8000/categories/JSON

for example: http://localhost:8000/categories/JSON

Response body:
```
{
  "categories": [
    {
      "id": 1, 
      "items": [
        {
          "category_id": 1, 
          "description": "A football player from Brazil, and one of the best football players of all time", 
          "id": 1, 
          "last_modification": "Tue, 13 Aug 2019 07:26:42 GMT", 
          "name": "Ronaldinho", 
          "user_id": 1
        }, 
        {
          "category_id": 1, 
          "description": "A football player from Argentina, and one of the best or maybe the best football palyer of all time", 
          "id": 4, 
          "last_modification": "Tue, 13 Aug 2019 07:26:42 GMT", 
          "name": "Lionel Messi", 
          "user_id": 1
        }
      ], 
      "name": "Football"
    }, 
    {
      "id": 2, 
      "items": [
        {
          "category_id": 2, 
          "description": "A tennis palyer from Spain, and he is called the king of clay", 
          "id": 2, 
          "last_modification": "Tue, 13 Aug 2019 07:26:42 GMT", 
          "name": "Rafael Nadal", 
          "user_id": 1
        }
      ], 
      "name": "Tennis"
    }, 
    {
      "id": 3, 
      "items": [
        {
          "category_id": 3, 
          "description": "A handball player from Egypt, and one of the best handball player of Egypt's history", 
          "id": 3, 
          "last_modification": "Tue, 13 Aug 2019 07:26:42 GMT", 
          "name": "Ahmed El-ahmar", 
          "user_id": 1
        }, 
        {
          "category_id": 3, 
          "description": "A handball player from Denmark and he has won the handball player of the year three times", 
          "id": 5, 
          "last_modification": "Tue, 13 Aug 2019 07:31:56 GMT", 
          "name": "Mikkel Hansen", 
          "user_id": 2
        }
      ], 
      "name": "Handball"
    }, 
    {
      "id": 4, 
      "items": [
        {
          "category_id": 4, 
          "description": "A basketball player from the USA and he is called the GOAT of basketball", 
          "id": 8, 
          "last_modification": "Tue, 13 Aug 2019 08:08:16 GMT", 
          "name": "Michael Jordan", 
          "user_id": 2
        }
      ], 
      "name": "Basketball"
    }, 
    {
      "id": 5, 
      "items": [
        {
          "category_id": 5, 
          "description": "A volleyball player from Canada and one of the best in the world and he is called Canada\u2019s scoring machine.", 
          "id": 7, 
          "last_modification": "Tue, 13 Aug 2019 07:35:03 GMT", 
          "name": "Earvin Ngapeth", 
          "user_id": 2
        }
      ], 
      "name": "Volleyball"
    }
  ]
}
```
* GET localhost:8000/catalog/<category_name>/items/JSON

for example: http://localhost:8000/catalog/Football/items/JSON/

Response body:
```
{
  "Items": [
    {
      "category_id": 1, 
      "description": "A football player from Brazil, and one of the best football players of all time", 
      "id": 1, 
      "last_modification": "Tue, 13 Aug 2019 07:26:42 GMT", 
      "name": "Ronaldinho", 
      "user_id": 1
    }, 
    {
      "category_id": 1, 
      "description": "A football player from Argentina, and one of the best or maybe the best football palyer of all time", 
      "id": 4, 
      "last_modification": "Tue, 13 Aug 2019 07:26:42 GMT", 
      "name": "Lionel Messi", 
      "user_id": 1
    }
  ]
}
```
* GET localhost:8000/catalog/<category_name>/<item_name>/JSON

for example: http://localhost:8000/catalog/Football/Ronaldinho/JSON 

Response body:
```
{
  "Item": {
    "category_id": 1, 
    "description": "A football player from Brazil, and one of the best football players of all time", 
    "id": 1, 
    "last_modification": "Tue, 13 Aug 2019 07:26:42 GMT", 
    "name": "Ronaldinho", 
    "user_id": 1
  }
}
```

### Technologies
Project is created with:
* Python 2.7.12
* Flask web development framework
* SQLAlchemy
* HTML
* CSS
* SQLite

### Coding Syle
* Follows PEP 8 — the Style Guide for Python Code


