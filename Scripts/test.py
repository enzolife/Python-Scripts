import multiprocessing
import time

def func(msg):
    for i in range(3):
	    print(msg)
	    time.sleep(1)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    p = multiprocessing.Process(target=func, args=("hello", ))
    p.start()
    p.join()
    print("Sub-process done.")
