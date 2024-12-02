# import pandas as pd
# import psycopg2
#
# df = pd.read_csv("spotify_songs.csv")
#
# coneccion = psycopg2.connect(
#     host="localhost",
#     database="proyecto2db2",
#     user="postgres",
#     password="",
#     port="5432"
# )
#
# cur = coneccion.cursor()
#
# consulta1 = """
# CREATE TABLE  IF NOT EXISTS canciones (
#     track_id VARCHAR(255) UNIQUE,
#     track_name VARCHAR(255),
#     track_artist VARCHAR(255),
#     lyrics TEXT,
#     track_popularity INT,
#     track_album_id VARCHAR(255),
#     track_album_name VARCHAR(255),
#     track_album_release_date VARCHAR,
#     playlist_name VARCHAR(255),
#     playlist_id VARCHAR(255),
#     playlist_genre VARCHAR(255),
#     playlist_subgenre VARCHAR(255),
#     danceability FLOAT,
#     energy FLOAT,
#     track_key INT,
#     loudness FLOAT,
#     mode INT,
#     speechiness FLOAT,
#     acousticness FLOAT,
#     instrumentalness FLOAT,
#     liveness FLOAT,
#     valence FLOAT,
#     tempo FLOAT,
#     duration_ms INT,
#     language VARCHAR(10)
# );
# """
#
# cur.execute(consulta1)
#
# for index, row in df.iterrows():
#     try:
#         cur.execute("""
#             INSERT INTO canciones (
#                 track_id, track_name, track_artist, lyrics, track_popularity,
#                 track_album_id, track_album_name, track_album_release_date, playlist_name,
#                 playlist_id, playlist_genre, playlist_subgenre, danceability, energy,
#                 track_key, loudness, mode, speechiness, acousticness, instrumentalness,
#                 liveness, valence, tempo, duration_ms, language
#             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """, (
#             row['track_id'], row['track_name'], row['track_artist'], row['lyrics'], row['track_popularity'],
#             row['track_album_id'], row['track_album_name'], row['track_album_release_date'], row['playlist_name'],
#             row['playlist_id'], row['playlist_genre'], row['playlist_subgenre'], row['danceability'], row['energy'],
#             row['key'], row['loudness'], row['mode'], row['speechiness'], row['acousticness'], row['instrumentalness'],
#             row['liveness'], row['valence'], row['tempo'], row['duration_ms'], row['language']
#         ))
#         coneccion.commit()
#     except Exception as e:
#         print(f"Error en el registro {index}: {e}")
#         coneccion.rollback()
#
# consulta2 = """
# CREATE EXTENSION IF NOT EXISTS pg_trgm;
# alter table canciones rename to canciones_completo;
# create table canciones as (select track_name,track_artist,lyrics from canciones_completo);
# alter table canciones add column terms_lyrics tsvector;
# update canciones set terms_lyrics = to_tsvector('english', lyrics);
# drop table canciones_completo;
# create index lyricsidx on canciones using GIN(terms_lyrics);
# """
#
# cur.execute(consulta2)

import pandas as pd
import psycopg2

# Leer el archivo CSV
df = pd.read_csv("spotify_songs.csv")#.head(16000)

# Establecer conexión a la base de datos
coneccion = psycopg2.connect(
    host="localhost",
    database="proyecto2db2",
    user="postgres",
    password="",
    port="5432"
)
cur = coneccion.cursor()

try:
    # 1. Crear tabla completa con todos los datos
    consulta1 = """ 
    CREATE TABLE IF NOT EXISTS canciones_completo (
        track_id VARCHAR(255) UNIQUE,
        track_name VARCHAR(255),
        track_artist VARCHAR(255),
        lyrics TEXT,
        track_popularity INT,
        track_album_id VARCHAR(255),
        track_album_name VARCHAR(255),
        track_album_release_date VARCHAR,
        playlist_name VARCHAR(255),
        playlist_id VARCHAR(255),
        playlist_genre VARCHAR(255),
        playlist_subgenre VARCHAR(255),
        danceability FLOAT,
        energy FLOAT,
        track_key INT,
        loudness FLOAT,
        mode INT,
        speechiness FLOAT,
        acousticness FLOAT,
        instrumentalness FLOAT,
        liveness FLOAT,
        valence FLOAT,
        tempo FLOAT,
        duration_ms INT,
        language VARCHAR(10)
    );
    """
    cur.execute(consulta1)


    # 2. Insertar datos
    # Crear un generador para mejorar la eficiencia de inserción
    def generate_rows():
        for index, row in df.iterrows():
            yield (
                row['track_id'], row['track_name'], row['track_artist'], row['lyrics'], row['track_popularity'],
                row['track_album_id'], row['track_album_name'], row['track_album_release_date'], row['playlist_name'],
                row['playlist_id'], row['playlist_genre'], row['playlist_subgenre'], row['danceability'], row['energy'],
                row['key'], row['loudness'], row['mode'], row['speechiness'], row['acousticness'],
                row['instrumentalness'],
                row['liveness'], row['valence'], row['tempo'], row['duration_ms'], row['language']
            )


    # Inserción de datos utilizando executemany para mayor eficiencia
    insert_query = """
    INSERT INTO canciones_completo (
        track_id, track_name, track_artist, lyrics, track_popularity, 
        track_album_id, track_album_name, track_album_release_date, playlist_name, 
        playlist_id, playlist_genre, playlist_subgenre, danceability, energy, 
        track_key, loudness, mode, speechiness, acousticness, instrumentalness, 
        liveness, valence, tempo, duration_ms, language
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (track_id) DO NOTHING;
    """
    cur.executemany(insert_query, generate_rows())

    # 3. Crear extensión para búsqueda de texto
    cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # 4. Crear tabla de canciones con columnas de interés
    consulta2 = """
    CREATE TABLE canciones AS (
        SELECT DISTINCT ON (track_name, track_artist) 
        track_name, 
        track_artist, 
        lyrics 
        FROM canciones_completo
        WHERE lyrics IS NOT NULL AND trim(lyrics) != ''
    );

    -- Añadir columna de términos de letras
    ALTER TABLE canciones ADD COLUMN terms_lyrics tsvector;

    -- Actualizar columna de términos de letras
    UPDATE canciones 
    SET terms_lyrics = to_tsvector('english', lyrics)
    WHERE lyrics IS NOT NULL AND trim(lyrics) != '';

    -- Crear índice GIN para búsqueda eficiente
    CREATE INDEX lyricsidx ON canciones USING GIN(terms_lyrics);
    """
    cur.execute(consulta2)

    # Confirmar cambios
    coneccion.commit()

    # Verificar resultados
    cur.execute("""
        SELECT 
            count(*) as total_rows, 
            count(terms_lyrics) as rows_with_terms_lyrics,
            count(CASE WHEN terms_lyrics IS NOT NULL AND length(terms_lyrics::text) > 0 THEN 1 END) as non_empty_terms_lyrics
        FROM canciones
    """)
    result = cur.fetchone()
    print(f"Total de filas: {result[0]}")
    print(f"Filas con terms_lyrics: {result[1]}")
    print(f"Filas con terms_lyrics no vacío: {result[2]}")

except psycopg2.Error as e:
    print(f"Error de PostgreSQL: {e}")
    coneccion.rollback()
except Exception as e:
    print(f"Error inesperado: {e}")
    coneccion.rollback()
finally:
    cur.close()
    coneccion.close()