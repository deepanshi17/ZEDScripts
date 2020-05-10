import os

'''
Functions to set up a folder to store data
it takes a filepath as the base name and will automatically make a folder
with the path and if it already exists it will append a number to the end
example given the path /home/documents/saveData/
name data
the setup folders function will take the path and name each time is run it will make 
/home/documents/saveData/data0 , /home/documents/saveData/data1 ...
'''

def checkFolder(path, folder):
    files = os.listdir(path)
    if folder in files:
        return True

    else:
        return False


#takes the path and the name of the folder you want made setups a folder with the name and numbers added to it to make a new folder
#the function will make the folder and then return the path of the new folder
def setupFolder(path,name):
    print("setting up data folder")

    if path[-1] != "/":
        path = path + '/'


    try:
        os.mkdir(path=path)
    except Exception as e:
        print('Problem creating the first data folder its probably already made')
        print(e)

    x = 0
    while checkFolder(path, name + str(x)):
        x += 1

    path = path + name + str(x) + '/'

    try:
        os.mkdir(path=path)
    except Exception as e:
        print('Problem creating the second data folder its probably already made')
        print(e)

    print("finished setting up data folder")

    return path
