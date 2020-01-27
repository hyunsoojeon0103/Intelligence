#ifndef VARIABLE__H
#define VARIABLE__H
#include <string>
#include "cell.h"
struct variable
{
    variable():domain("123456789")
    {}
    variable(const variable& var)
    {
        c = var.c;
        domain = var.domain;
    }
    variable(const char row, const char col,const char val):domain("123456789")
    {
        c.loc[0] = row;
        c.loc[1] = col;
        c.val = val;
    }
    variable& operator = (const variable& var)
    {c= var.c; domain = var.domain; return *this;}
    cell c;
    std::string domain;
};
#endif
