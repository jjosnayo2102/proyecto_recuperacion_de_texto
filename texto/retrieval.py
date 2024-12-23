from texto.fetch import InvertIndex, pd, default_value

indice = InvertIndex("indice")
indice.load_index()
df = pd.read_csv("texto/spotify_songs.csv")
contenido = df[["track_name", "track_artist", "lyrics"]]

def recuperacion(input,top):
    ret = indice.retrieval(input, top) # los cuenta a partir de la segunda fila, sin contar el header
    resd = []
    for tupla in ret:
        fila = contenido.iloc[tupla[0]-1]
        d = {"titulo": fila["track_name"],"puntaje": tupla[1],"autor": fila["track_artist"], "letra": fila["lyrics"]}
        resd.append(d)
    return resd
