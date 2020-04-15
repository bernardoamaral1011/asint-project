# asint-project
Internet Based Systems Architecture subject project

1º- fazer as bd's para os três tipos de dados, em python

2º- fazer as 3 API's em flask

3º- só depois fazer as aplicações que interagem com as API's

4º- Migrar as API's e a base de dados para o Google Cloud Platform


Admin:
    python only app that lets the admin interact with the api functions

Admin API: (/API/Buildings/...)
    group of html and flask files that implement the following functions:

- admin autentication
- receives text file and adds buildings
- list all users that are logged-in into the system
- list all users that are inside a certain building
- list the history of all the user movements and exchanged messages this list can be configured
with a simple query to select the user or building.

User: 
    html, javascript application that does the following:

- calls user api functions/domains

User API: 
    group of html and flask files that implement the following functions:

- login using the FENIX Authentication (istID and password).
- send messages to users nearby (in a defined distance range)
- define the distance range that will include the nearby users
- see who is neerby: on the range of the messages and on the same buiding.
- Receive messages sent by other users and bots


Bots:
    python application that interacts with bots API

Bots API:

- registration and assignment to a building
- send message to users in that building


Class Notes:

admin - python -> aplicação 
user - html -> página web
bots - python
server apis - flask

primeiro: definir api de interação com o servidor

admin pode ter autenticação ou pode configurar os bots como quiser -> 20
