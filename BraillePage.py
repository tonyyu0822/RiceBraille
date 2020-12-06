import numpy as np

class BraillePage:
    """
    Class representing a page of braille. Position of finger is measured from top right corner.
    """
    # number of rows and columns of Braille characters on printed Braille sheet
    numRows = 26
    numColumns = 42

    # Braille sheet dimensions
    pageWidth = 11.5625
    pageHeight = 11
    leftMargin = 0.875
    rightMargin = 0.75
    topMargin = 0.5
    botMargin = 0.625

    # Page matrix (will be None until assignCharGridCoords() is called)
    charMatrix = None

    # THESE ARE TEST VALUES, REAL VALUES SHOULD BE GENERATED FROM FINGER TRACKING
    x_pos = 3.975
    y_pos = 5.875

    def __init__(self, brf_file):
        """
        initialize page of Braille
        :param brf_file: path to .brf file of Braille to load in
        """
        # load in file at input path
        fileStr = self.loadBrf(brf_file)

        # convert input Braille file into a matrix
        self.charMatrix = self.assignCharGridCoords(fileStr)
    
    # Converts .brf file into text string
    def loadBrf(self, brf_file):
        """
        Loads in Braille .brf file into a String
        :param brf_file: path to .brf file of Braille to load in 
        """
        with open(brf_file, 'r') as fh:
            fileStr = fh.read()
        return fileStr
        
    def assignCharGridCoords(self, textFile):
        """
        :return: np matrix where each character is allocated a grid position on the page
        ex. reference 3rd row, 5th character by calling assignCharGridCoords(textFile,numRows,numColumns)[5][3]
        """
        charCoords = np.empty((self.numRows, self.numColumns), str)
        charCount = 0
        for row in range(self.numRows):
            for column in range(self.numColumns):
                char = textFile[charCount]
                charCount += 1
                if char == '\n':
                    break
                charCoords[row][column] = char
        print('done')
        return charCoords

    def position2GridCoord(self, x_pos, y_pos):
        """
        Translates the x and y postions (continuous) of the finger into discrete row, column coordinates on Braille sheet

        SOMETIMES OFF BY 1 ROW OR COLUMN, POSSIBLY DUE TO EMBOSSER INACCURACY
        """
        x_coord = int(self.numColumns * (x_pos - self.leftMargin) / (self.pageWidth - self.leftMargin - self.rightMargin))
        y_coord = int(self.numRows * (y_pos - self.topMargin) / (self.pageHeight - self.topMargin - self.botMargin))
        return x_coord, y_coord
        
    def position2Char(self, x_pos, y_pos):
        """
        :returns: the character at the given x, y positions (continuous) measured from top left of Braille sheet. Also returns the row and column the character is located at.
        """
        if (x_pos >= self.leftMargin and x_pos < self.pageWidth - self.rightMargin and y_pos >= self.topMargin and y_pos < self.pageHeight - self.botMargin):
            # if statement checks if x,y finger position is within the margins
            gridCoords = self.position2GridCoord(x_pos, y_pos)
            row = gridCoords[0]
            column = gridCoords[1]
            return self.charMatrix[column][row], row, column
        else:
            #returns char = ' ' and row/column = -1 if finger outside margins
            return ' ', -1, -1
        
        
    # charMatrix = assignCharGridCoords(file, numRows, numColumns)

    # # HERE YOU CAN ITERATE OVER ALL FINGERS
    # charUnderFinger = position2Char(x_pos, y_pos, pageWidth, pageHeight, leftMargin, rightMargin, topMargin, botMargin, numRows, numColumns,charMatrix)

    # print(charUnderFinger)

if __name__ == '__main__':
    test = BraillePage('./braille_files/B_2019 project FingerTracker.brf')