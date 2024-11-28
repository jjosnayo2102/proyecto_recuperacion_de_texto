import pickle

with open("index_image_sec.dat","rb") as file:
    bd = pickle.load(file)
print(len(bd))     
