#include "funcs.h"
bool inquire(const char* query)
{
    char ans;
    do
    {
        std::cout << query << " [Yes or No]" << std::endl;
        std::cin >> ans;
        eat_line();
        ans = tolower(ans);
    }while(ans != 'y' && ans != 'n');
    return ans == 'y';
}
void eat_line()
{
    char tmp;
    do
        std::cin.get(tmp);
    while(tmp != '\n');
}
void solve(my_st& st, const unsigned short rows, const unsigned short cols,const unsigned short ctr,const unsigned short max)
{
    queen q(ctr / rows + 1, ctr % cols + 1);
    st.push(q);
    do
    {
        if(check(st))
            st.push(queen((st.top().row < rows)? st.top().row + 1: 1));
        else
            try_another(st,cols);
    }while(st.size() <= max);
    st.pop();
}
bool check(my_st& st)
{
    bool good = true;
    if(st.size() > 1)
    {
        my_st tmp_st;
        queen top_q = st.top();
        st.pop();
        while(!st.empty() && good)
        {
            queen tmp = st.top();
            unsigned short offset = top_q.row - tmp.row;
            if(conflict(top_q,tmp,offset))
                good = false;
            else
            {
                tmp_st.push(st.top());
                st.pop();
            }
        }
        while(!tmp_st.empty())
        {
            st.push(tmp_st.top());
            tmp_st.pop();
        }
        st.push(top_q);
    }
    return good;
}
bool conflict(const queen& q1, const queen& q2,const unsigned short offset)
{
    return q1.col == q2.col || q1.col + offset == q2.col || q1.col - offset == q2.col;
}
void try_another(my_st& st,const unsigned short cols)
{
    assert("THE BOARD CANNOT BE SOLVED" && st.size() != 0);
    queen tmp = st.top();
    st.pop();
    ++tmp.col;
    if(tmp.col > cols)
        return try_another(st,cols);
    st.push(tmp);
}
void display(my_st& st)
{
    my_st reverse;
    while(!st.empty())
    {
        reverse.push(st.top());
        st.pop();
    }
    while(!reverse.empty())
    {
        unsigned short row = reverse.top().row;
        unsigned short col = reverse.top().col;
        std::cout << '[' << row << ',' << col << ']';
        reverse.pop();
        if(!reverse.empty())
            std::cout << " -> ";
    }
    std::cout << std::endl;
}
