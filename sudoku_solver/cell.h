#ifndef CELL__H
#define CELL__H
struct cell
{
    cell()
    {
        loc[2] = '\0';
        val = '0';
    }
    char loc[3];
    char val;
};
#endif
