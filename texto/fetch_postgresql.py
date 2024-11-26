import pandas as pd
import psycopg2

df = pd.read_csv("spotify_songs.csv")

coneccion = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="j73987927j",
    port="5432"
)

cur = coneccion.cursor()

consulta1 = """ 
CREATE TABLE canciones (
    track_id VARCHAR(255),
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

for index, row in df.iterrows():
    try:
        cur.execute("""
            INSERT INTO canciones (
                track_id, track_name, track_artist, lyrics, track_popularity, 
                track_album_id, track_album_name, track_album_release_date, playlist_name, 
                playlist_id, playlist_genre, playlist_subgenre, danceability, energy, 
                track_key, loudness, mode, speechiness, acousticness, instrumentalness, 
                liveness, valence, tempo, duration_ms, language
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['track_id'], row['track_name'], row['track_artist'], row['lyrics'], row['track_popularity'],
            row['track_album_id'], row['track_album_name'], row['track_album_release_date'], row['playlist_name'],
            row['playlist_id'], row['playlist_genre'], row['playlist_subgenre'], row['danceability'], row['energy'],
            row['key'], row['loudness'], row['mode'], row['speechiness'], row['acousticness'], row['instrumentalness'],
            row['liveness'], row['valence'], row['tempo'], row['duration_ms'], row['language']
        ))
        coneccion.commit()
    except Exception as e:
        print(f"Error en el registro {index}: {e}")
        coneccion.rollback()

consulta2 = """
CREATE EXTENSION IF NOT EXISTS pg_trgm;
alter table canciones rename to canciones_completo;
create table canciones as (select track_name,track_artist,lyrics from canciones_completo);
alter table canciones add column terms_lyrics tsvector;
update canciones set terms_lyrics = to_tsvector('english', lyrics);
drop table canciones_completo;
create index lyricsidx on canciones using GIN(terms_lyrics);
"""

cur.execute(consulta2)
