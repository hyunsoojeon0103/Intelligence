#ifndef QUEEN_H
#define QUEEN_H
struct queen
{
    queen(const unsigned short row_in = 1, const unsigned short col_in = 1):row(row_in),col(col_in){}
    unsigned short row;
    unsigned short col;
};
#endif
