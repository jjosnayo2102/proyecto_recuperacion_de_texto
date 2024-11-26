import psycopg2
import re

def conectar():
    coneccion = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="j73987927j",
        port="5432"
        )
    return coneccion.cursor()


# cambiar a & para búsqueda más exacta
# cambiar a | para mayor recall
def recuperacion_postgresql(input, top):
    input = input.lower()
    input = re.sub(r"[^\w\s]", "", input)
    input = input.split(" ")
    input = " & ".join(input)
    consulta = """
    select track_name, ts_rank_cd(terms_lyrics, to_tsquery('english',%s), 32) as rank, track_artist, lyrics
    from canciones
    where terms_lyrics @@ to_tsquery('english', %s)
    order by rank desc 
    limit %s;
    """
    cur = conectar()
    cur.execute(consulta,(input,input,top))
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
