import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import abort, render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = {}
    x = db.execute('SELECT COUNT(*) AS Pokemons FROM POKEMON').fetchone()
    stats.update(x)
    x = db.execute('SELECT COUNT(*) AS Types FROM TYPES').fetchone()
    stats.update(x)
    x = db.execute('SELECT COUNT(*) AS Moves FROM MOVES').fetchone()
    stats.update(x)
    logging.info(stats)
    return render_template('index.html',stats = stats)

# Pokemons
@APP.route('/pokemons/')
def list_pokemons():
    pokemons = db.execute(
        '''
        SELECT PokId, POKEMON.Name, Evolution, Hp, Atk, Def, Spc, Spe, MetId
        FROM POKEMON 
        JOIN BASE_STATS USING (PokId)
        JOIN PKMNEVOMET USING (PokId)
        LEFT OUTER JOIN EVOLUTION_METHOD USING (MetId)
        ORDER BY PokId
        ''').fetchall()
    return render_template('pokemon-list.html', pokemons = pokemons)

@APP.route('/pokemons/<int:id>/')
def get_Pokemon(id):
    pokemon = db.execute(
        '''
        SELECT PokId, POKEMON.Name, Evolution, Hp, Atk, Def, Spc, Spe, MetId
        FROM POKEMON
        JOIN BASE_STATS USING (PokId)
        JOIN PKMNEVOMET USING (Pokid)
        LEFT OUTER JOIN EVOLUTION_METHOD USING (MetId)
        WHERE PokId = %s
        ''', id).fetchone()
    if pokemon is None:
        abort(404, 'Pokemon id {} does not exist.'.format(id))
    
    types = db.execute(
        '''
        SELECT TypeId, TYPES.Name
        FROM TYPES NATURAL JOIN PKMNTPS
        WHERE PokId = %s
        ORDER BY TYPES.Name
        ''', id).fetchall()
    
    moves = db.execute(
        '''
        SELECT MoveId, MOVES.Name
        FROM MOVES NATURAL JOIN PKMNMVS
        WHERE PokId = %s
        ORDER BY MOVES.Name
        ''', id).fetchall()
    
    evo = db.execute(
        '''
        SELECT MetId, EVOLUTION_METHOD.Name
        FROM EVOLUTION_METHOD NATURAL JOIN PKMNEVOMET
        WHERE Pokid = %s
        ORDER BY EVOLUTION_METHOD.Name
        ''', id).fetchall()
    
    places = db.execute(
        '''
        SELECT LocalId, PLACES.Name
        FROM PLACES NATURAL JOIN PKMNLCL
        WHERE PokId = %s
        ORDER BY PLACES.Name
        ''', id).fetchall()
    return render_template('pokemon.html',
                     pokemon=pokemon, types=types, moves=moves, evo=evo, places=places)

@APP.route('/pokemons/search/<expr>/')
def search_pokemon(expr):
    search = { 'expr': expr }
    expr = '%' + expr + '%'
    pokemons = db.execute(
        '''
        SELECT PokId, Name
        FROM POKEMON
        WHERE Name LIKE %s
        ''', expr).fetchall()
    return render_template('pokemon-search.html',
                     search=search, pokemons=pokemons)


#Types
@APP.route('/types/')
def list_types():
    types = db.execute('''
      SELECT TypeId, Name
      FROM TYPES
      ORDER BY NAME
    ''').fetchall()
    return render_template('type-list.html', types=types)

@APP.route('/types/<int:id>/')
def view_pokemons_by_type(id):
    types = db.execute(
        '''
        SELECT TypeId, Name
        FROM TYPES
        WHERE TypeId = %s
        ''', id).fetchone()
    if types is None:
        abort(404, 'Type id {} does not exist.'.format(id))
    
    pokemons = db.execute(
        '''
        SELECT PokId, Name
        FROM POKEMON NATURAL JOIN PKMNTPS
        WHERE TypeId = %s
        ORDER BY Name
        ''', id).fetchall()

    effec = db.execute(
      '''
      SELECT TypeIdVS, DmgMult, TypeId, TYPES.Name
      FROM EFFEC
      JOIN TYPES ON (TypeIdVS = TypeId)
      WHERE TypeIdBase = %s
      ORDER BY TypeId
      ''', id).fetchall()
    
    resis = db.execute(
    '''
    SELECT TypeIdVS, DmgMult, TypeId, TYPES.Name
    FROM RESIS
    JOIN TYPES ON (TypeIdVS = TypeId)
    WHERE TypeIdBase = %s
    ORDER BY TypeId
      ''', id).fetchall()

    return render_template('type.html',
                     types=types, pokemons=pokemons, effec=effec, resis=resis)


#Moves
@APP.route('/moves/')
def list_moves():
    moves = db.execute('''
      SELECT MoveId, Name, BasePower, Acc, PP, Type
      FROM MOVES
      ORDER BY Name
    ''').fetchall()
    return render_template('moves-list.html', moves=moves)

@APP.route('/moves/<int:id>/')
def view_pokemon_by_move(id):
  move = db.execute(
    '''
    SELECT MoveId, Name, BasePower, Acc, PP, Type
    FROM MOVES
    WHERE MoveId = %s
    ''', id).fetchone()

  if move is None:
     abort(404, 'Move id {} does not exist.'.format(id))

  pokemons = db.execute(
    '''
    SELECT PokId, Name
    FROM POKEMON NATURAL JOIN PKMNMVS
    WHERE MoveId = %s
    ORDER BY Name
    ''', id).fetchall()

  return render_template('move.html', 
           move=move, pokemons=pokemons)


#Locals
@APP.route('/places/')
def list_places():
    places = db.execute('''
      SELECT LocalId, Name 
      FROM PLACES
      ORDER BY Name
    ''').fetchall()
    return render_template('places-list.html', places=places)

@APP.route('/places/<int:id>/')
def view_pokemon_by_place(id):
  place = db.execute(
    '''
    SELECT LocalId, Name
    FROM PLACES
    WHERE LocalId = %s
    ''', id).fetchone()

  if place is None:
     abort(404, 'local id {} does not exist.'.format(id))

  pokemons = db.execute(
    '''
    SELECT PokId, Name
    FROM POKEMON NATURAL JOIN PKMNLCL
    WHERE LocalId = %s
    ORDER BY Name
    ''', id).fetchall()

  return render_template('place.html', 
           place=place, pokemons=pokemons)

#evo
@APP.route('/evo/')
def list_evo():
    evo = db.execute('''
      SELECT MetId, Name 
      FROM EVOLUTION_METHOD
      ORDER BY Name
    ''').fetchall()

    if evo is None:
     abort(404, 'id {} does not exist.'.format(id))

    return render_template('evo-list.html', evo=evo)

@APP.route('/evo/<int:id>/')
def view_pokemon_by_evo(id):
  evo = db.execute(
    '''
    SELECT MetId, Name
    FROM EVOLUTION_METHOD
    WHERE MetId = %s
    ''', id).fetchone()

  if evo is None:
     abort(404, 'Met id {} does not exist.'.format(id))

  pokemons = db.execute(
    '''
    SELECT PokId, Name
    FROM POKEMON NATURAL JOIN PKMNEVOMET
    WHERE MetId = %s
    ORDER BY Name
    ''', id).fetchall()

  return render_template('evo.html', 
           evo=evo, pokemons=pokemons)






    
    
    