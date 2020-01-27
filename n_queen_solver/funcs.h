#ifndef FUNCS_H
#define FUNCS_H
#include <cstdlib>
#include <iostream>
#include <stack>
#include <cassert>
#include "queen.h"

typedef std::stack<queen> my_st;
bool inquire(const char* query);
void eat_line();
void solve(my_st& st, const unsigned short rows, const unsigned short cols, const unsigned short ctr,const unsigned short max);
bool check(my_st& st);
bool conflict(const queen& q1, const queen& q2,const unsigned short offset);
void try_another(my_st& st,const unsigned short cols);
void display(my_st& st);
#endif
