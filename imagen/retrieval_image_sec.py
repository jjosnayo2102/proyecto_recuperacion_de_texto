# Calcular la complejidad  del KNN optimizado con MaxHeap
import numpy as np
import heapq

def ED(P,Q):
    P = np.array(P)
    Q = np.array(Q)
    return np.linalg.norm(abs(P-Q))

def knnSearch(query, collection, k):
    max_heap = []
    for f in range(len(collection)):
        dist = ED(collection[f], query)
        if len(max_heap) < k:
            heapq.heappush(max_heap, (-dist, f))
        else:
            heapq.heappushpop(max_heap, (-dist, f))
    res = [(f, -dist) for dist, f in max_heap]
    return res
