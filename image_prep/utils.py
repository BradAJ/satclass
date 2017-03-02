

# HELPER FUNCTION
def spiral_stepper(step_size = 1, max_steps = 1):
    """
    Create a list of integer steps to spiral outward in a square pattern
    from the origin.

    INPUT:
    step_size: (int) Could use pixel values for step size, but easier 
                to use 1. And then translate that to pixels outside this helper.
    max_steps: (int) number of steps to iterate over.

    OUTPUT:
    (list) of tuples of coordinates e.g.: 
    >>>spiral_stepper(max_steps = 5)
    >>>[(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    """
    
    def _next_spiral_corner(x0=0, y0=0, k=1, accum=[(0,0)], 
                            max_len=100, step_size=1):
        """
        recursive algo idea from:
        http://stackoverflow.com/questions/3706219/

        N = INT((1+k)/2)
        Sign = | +1 when N is Odd
               | -1 when N is Even
        [dx,dy] = | [N*Sign,0]  when k is Odd
                  | [0,N*Sign]  when k is Even
        [X(k),Y(k)] = [X(k-1)+dx,Y(k-1)+dy]

        weird recursion issue where sometimes search 
        gets reset to (1,0) so some points repeated

        """

        if len(accum) >= max_len:
            return accum
        num_steps = (k + 1) // 2


        step_dir = -1 if (num_steps % 2) == 0 else 1
        
        x_trans, y_trans = (0, step_dir) if (k % 2) == 0 else (step_dir, 0)

        for i in xrange(1, num_steps+1):
            xnext = x0 + (i*step_size*x_trans)
            ynext = y0 + (i*step_size*y_trans)
            
            if (xnext,ynext) in accum:
                print xnext,ynext, x0, y0, i, x_trans, y_trans,k,len(accum)
            accum.append((xnext, ynext))

        if len(set(accum)) < len(accum):
            #raise Exception('Recursion error, retry')
            return _next_spiral_corner(x0=0, y0=0, k=1, accum=[(0,0)], 
                                        max_len=max_len, step_size=step_size)
        return _next_spiral_corner(x0=accum[-1][0], y0=accum[-1][1], k=k+1, 
                                    accum=accum, max_len=max_len, 
                                    step_size=step_size)

    return _next_spiral_corner(x0=0, y0=0, k=1, accum=[(0,0)], 
                                max_len=max_steps, step_size=step_size) 