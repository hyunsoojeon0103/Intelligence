#include <iostream>
#include <stack>
#include "queen.h"
#include "funcs.h"
int main()
{
    unsigned short rows = 8;
    unsigned short cols = 8;
    if(!inquire("Would you like a standard 8 by 8 board?"))
    {
        std::cout << "What is the number of rows?\n";
        std::cin >> rows;
        std::cout << "What is the number of columns?\n";
        std::cin >> cols;
    }
    
    unsigned short max = (rows < cols)? rows: cols;
    
    unsigned short ctr = 0;

    do
    {
        std::stack<queen> st;
        solve(st,rows,cols,ctr,max);
        display(st);
    }while(inquire("Would you like to see another solution?") && ctr++ <= rows*cols);

    std::cout << "Bye\n";

    return 0;
}
