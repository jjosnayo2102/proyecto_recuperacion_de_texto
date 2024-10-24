from prueba import InvertIndex

def recuperacion(input,top):
    resd = [{"titulo": "temporal","puntaje": "temporal","autor": "temporal","letra": "temporal"}]
    return resd

indice = InvertIndex("indice.dat")
indice.load_index()

ret = indice.retrieval("The trees, are singing in the wind The sky blue, only as it can be And the angels, smiled at me I saw you, in that lonely bench At half past four, I kissed your soft soft hands and at 6 I kissed your lips and the angels smiled, I thought Hey I feel alive! The park sign, said it was closed And we jumped that fence with no cares at all and we kissed under a tree We danced, under the midnight sun And I loved you, without knowing you at all and we laughed and felt so free and the angels they smiled, I thought Hey, I feel alive!", 3)
print(ret) # agarra 2 menos que la verdadera fila, en csv: ret + 2