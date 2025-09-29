import os.path
import pickle

class MyDB:

    def __init__(self, filename):
        self.fname = filename
        #looking for a file
        #file system is outside of the boundary
        #don't actually touch the file
        #HOW??
        if not os.path.isfile(self.fname):
            self.saveStrings([])

    def loadStrings(self):
        with open(self.fname, 'rb') as f:
            #outside of the boundary
            arr = pickle.load(f)
        return arr

    def saveStrings(self, arr):
        with open(self.fname, 'wb') as f:
            #outside of the boundary
            pickle.dump(arr, f)

    def saveString(self, s):
        arr = self.loadStrings()
        arr.append(s)
        self.saveStrings(arr)
