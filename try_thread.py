import threading, time

def func1():
    global flag
    for i in range(5):
        if not flag: break
        print(i)
        time.sleep(1)
    print("Func1 done!")
    return

def func2():
    global flag
    print("in: ", input("gg: "))
    flag = False
    return

flag = True

t1 = threading.Thread(target=func1)
t2 = threading.Thread(target=func2)

t1.start()
t2.start()

t1.join()
t2.join()

print("Finish")

