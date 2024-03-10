from scipy.special import softmax
import numpy as np
import time

def timer(func, param):
    start = time.time()
    func(param)
    print(f"Time elapsed: {time.time() - start}")

def np_softmax(arr):
    return np.exp(arr)/np.sum(np.exp(arr))


np.random.seed(1234)

arr = np.random.rand(30000, 30000) * 5

print("Without optimization:")
timer(np_softmax, arr)
timer(softmax, arr)

print("\n\nWith optimization:")
arr -= np.max(arr)
timer(np_softmax, arr)
timer(softmax, arr)
