#!/home/ume/anaconda3/bin/python3
# #!/usr/bin/env python3

# numpy importieren
import numpy as np

# hundert zufällige Zahlen
x = np.random.normal(size=100)

# x in ein zweidimensionales array umwandeln
x.reshape((20,5))

# calculate the matrix dot product: X*X, where x is the transpose of x (hä???)
x.dot(x.T)
print ("hallo")
