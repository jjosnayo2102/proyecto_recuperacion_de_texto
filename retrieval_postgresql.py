import psycopg2

def conectar():
    coneccion = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="j73987927j",
        port="5432"
        )
    return coneccion.cursor()


def recuperacion_postgresql(input, top):
    query = """
    select track_name, ts_rank_cd(terms_lyrics, plainto_tsquery('english',%s)) as rank, track_artist, lyrics
    from canciones
    order by rank desc 
    limit %s;
    """
    cur = conectar()
    cur.execute(query,(input,top))
    res = cur.fetchall()
    resd = []
    for row in res:
        d = {}
        d["titulo"] = row[0]
        d["puntaje"] = row[1]
        d["autor"] = row[2]
        d["letra"] = row[3]
        resd.append(d)
    cur.close()
    return resd
