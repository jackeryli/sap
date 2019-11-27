class illegalMotorDetector():
    def detect(park_poly, x, y):

        ax = x - park_poly[0][0][0]
        ay = y - park_poly[0][0][1]
        bx = x - park_poly[0][1][0]
        by = y - park_poly[0][1][1]
        cx = x - park_poly[0][2][0]
        cy = y - park_poly[0][2][1]
        dx = x - park_poly[0][3][0]
        dy = y - park_poly[0][3][1]

        #print(ax*by-ay*bx, bx*cy-by*cx, cx*dy-cy*dx, dx*ay-dy*ax)

        if(ax*by-ay*bx > 0): return 0
        elif(bx*cy-by*cx > 0): return 0
        elif(cx*dy-cy*dx > 0): return 0
        elif(dx*ay-dy*ax > 0): return 0
        else: return 1
