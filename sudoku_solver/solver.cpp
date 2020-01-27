#include "solver.h"
solver::solver()
{
}
solver::~solver()
{
}
void solver::set_board(const std::string& config)
{
    board.set(config);
}
char solver::get_value(const size_t r,const size_t c)const
{
    return board.get_value(r,c);
}
char solver::get_value(const size_t idx)const
{
    return board.get_value(idx);
}
bool solver::solve()
{
    return backtrack(board);
}
bool solver::backtrack(sdk_board& brd)
{
    if(brd.complete())
        return true;
    
    variable var = brd.MRV();
    
    std::vector<size_t> rc = get_rc(var);
    
    sdk_board brd_cpy = brd;
    std::string vals = fwd_check(var,brd_cpy);
    
    for(size_t i =0; i < vals.length(); ++i)
    {
        brd[rc[0]][rc[1]].val = vals[i];
        bool res = backtrack(brd);
        if(res)
            return true;
        else
            brd[rc[0]][rc[1]].val = '0';
    }
    return false;
}
std::string solver::fwd_check(const variable& var, sdk_board& brd)
{
    std::string valid_vals;
   
    std::vector<size_t> rc = get_rc(var);
    std::vector<size_t> base = get_base(rc[0],rc[1]);
    
    for(size_t i = 0 ; i < var.domain.length(); ++i)
    {
        brd[rc[0]][rc[1]].val = var.domain[i];
        bool valid = true;

        for(size_t i = 0; i < sdk_board::COL && valid; ++i)
            if(brd[rc[0]][i].val == '0')
                valid = brd.get_domain(rc[0],i).domain.length() != 0;
        for(size_t i = 0; i < sdk_board::ROW && valid; ++i)
            if(brd[i][rc[1]].val == '0')
                valid = brd.get_domain(i,rc[1]).domain.length() != 0;
        for(size_t y = 0; y < 3 && valid; ++y)
            for(size_t x =0; x < 3 && valid; ++x)
                if(brd[base[0] + y][base[1] + x].val == '0')
                    valid = brd.get_domain(base[0]+y,base[1]+x).domain.length() != 0; 
        
        if(valid)
            valid_vals += var.domain[i];
    }
    return valid_vals;
}
void solver::clear()
{
    board.clear();
}
std::vector<size_t> get_rc(const variable& var)
{
    std::vector<size_t> rc;
    rc.push_back(sdk_board::ROWS.find(var.c.loc[0]));
    rc.push_back(sdk_board::COLS.find(var.c.loc[1]));
    return rc;
}
