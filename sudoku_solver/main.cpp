#include <ncurses.h>
#include <fstream>
#include <iostream>
#include <string>
#include "cell.h"
#include "solver.h"
#include "variable.h"
#include "sdk_board.h"

#define WIDTH 37
#define HEIGHT 19

void display(WINDOW* board,const solver& sdk_solver);

int main(int argc, char** argv)
{
    std::ifstream file;
    
    file.open("test.txt");
    
    if(file.is_open())
    {
        initscr();
        refresh();
        noecho();
        curs_set(false);
        
        solver sdk_solver;

        char ans = 'y';
        
        while(!file.eof() && ans == 'y')
        {
            std::string board_str;
            file >> board_str;
            
            sdk_solver.set_board(board_str);
            
            WINDOW* board = newwin(HEIGHT+1,WIDTH+1,0,0);
            
            display(board,sdk_solver);
            
            do
                mvprintw(HEIGHT+1,0,"Enter 's' for a solution"); 
            while((ans = getch()) != 's');
                mvprintw(HEIGHT+1,0,"                        ");

            if(!sdk_solver.solve())
            {
                mvprintw(HEIGHT+1,0,"Failed to solve the board...");
                ans = getch();
                mvprintw(HEIGHT+1,0,"                           ");
            }
            else 
                display(board,sdk_solver);
            
            do
            {
                mvprintw(HEIGHT+1,0,"Would you like another one? 'y' or 'n'");
                ans = getch();
                mvprintw(HEIGHT+1,0,"                                      ");
            }while(ans !='y' && ans !='n'); 
            
            sdk_solver.clear();
            delwin(board);
        }
        endwin();
        file.close();
    }
    else
        std::cout << "Failed to open the file" << std::endl;
    
    return 0;
}
void display(WINDOW* board, const solver& sdk_solver)
{ 
    size_t ctr = 0;
    for(size_t i =0; i < HEIGHT; ++i)
        for(size_t j = 0; j < WIDTH; ++j)
        {
            if(i == 0) //First row of the board
            {
                if(j == 0) //First column
                    mvwaddch(board,i,j,ACS_ULCORNER);
                else if(j == WIDTH-1) // Last column
                    mvwaddch(board,i,j,ACS_URCORNER);
                else if(j % 4 == 0) // dividers
                    mvwaddch(board,i,j,ACS_TTEE);
                else // normal line
                    mvwaddch(board,i,j,ACS_HLINE);
            }
            else if(i == HEIGHT - 1) // Last row of the board
            {
                if(j == 0)
                    mvwaddch(board,i,j,ACS_LLCORNER);
                else if(j == WIDTH-1)
                    mvwaddch(board,i,j,ACS_LRCORNER);
                else if(j % 4 == 0)
                    mvwaddch(board,i,j,ACS_BTEE);
                else
                    mvwaddch(board,i,j,ACS_HLINE);
            }
            else  // the middle left and right sides
            {
                if(j == 0 && i % 2 ==0) //first column
                    mvwaddch(board,i,j,ACS_LTEE);
                else if(j == WIDTH-1 && i % 2 ==0) // last column
                    mvwaddch(board,i,j,ACS_RTEE);
                else if(i % 2 == 0 && j % 4 ==0) // PLUS
                    mvwaddch(board,i,j,ACS_PLUS);
                else if(j % 4 == 0) // vertical dividers
                    mvwaddch(board,i,j,ACS_VLINE);
                else if(i % 2 ==0)
                    mvwaddch(board,i,j,ACS_HLINE);
                else if(j % 2 ==0) // Single digit data
                {
                    if(sdk_solver.get_value(ctr) != '0')
                        mvwprintw(board,i,j,"%c",sdk_solver.get_value(ctr));
                    ++ctr;
                }
            }
        }
    wrefresh(board);
}
