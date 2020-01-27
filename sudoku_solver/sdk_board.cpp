#include "sdk_board.h"
const std::string  sdk_board::ROWS = "ABCDEFGHI";
const std::string  sdk_board::COLS = "123456789";
const size_t sdk_board::ROW = 9;
const size_t sdk_board::COL = 9;
sdk_board::sdk_board()
{
}
sdk_board::sdk_board(const sdk_board& board_in)
{
    board = board_in.board;
}
std::vector<cell>& sdk_board::operator[](const size_t idx)
{
    assert(idx < board.size());
    return board[idx];
}
char sdk_board::get_value(const size_t r, const size_t c)const
{
    return board[r][c].val;
}
char sdk_board::get_value(const size_t idx)const
{
    size_t r = idx / ROW;
    size_t c = idx % COL;
    return board[r][c].val;
}

void sdk_board::set(const std::string& config)
{
    for(size_t i =0; i <ROW; ++i)
    { 
        std::vector<cell> row;
        for(size_t j =0; j <COL; ++j)
        {
            cell col;
            col.loc[0] = ROWS[i];
            col.loc[1] = COLS[j];
            col.val = config[i*ROW+j];
            row.push_back(col);
        }
        board.push_back(row);
    }
}
variable sdk_board::get_domain(const size_t row, const size_t col)const
{
    variable res(ROWS[row],COLS[col],get_value(row,col));
    
    std::vector<size_t> rc = get_base(row,col);
    size_t idx;
    size_t ctr = 0;
    
    while(ctr < COL && res.domain.length() > 0)
    {
        idx = res.domain.find(board[row][ctr].val);
        if(idx != std::string::npos)
            res.domain.erase(idx,1);
        
        idx = res.domain.find(board[ctr][col].val);
        if(idx != std::string::npos)
            res.domain.erase(idx,1);
        
        idx = res.domain.find(board[rc[0]+ctr/3][rc[1]+ctr%3].val);
        if(idx != std::string::npos)
            res.domain.erase(idx,1);
        ++ctr;
    }
    return res;
}
variable sdk_board::MRV()const
{
    variable minvar;
    for(size_t i = 0; i < ROW; ++i)
        for(size_t j = 0; j < COL; ++j)
            if(board[i][j].val == '0')
            {
                variable temp = get_domain(i,j);
                if(temp.domain.length() == 1)
                    return temp;
                else if(temp.domain.length() > 0 && temp.domain.length() < minvar.domain.length())
                    minvar = temp;
            }
    return minvar;
}
bool sdk_board::complete()const
{
    for(size_t i = 0; i < board.size(); ++i)
        for(auto it = board[i].begin(); it != board[i].end(); ++it)
            if((*it).val == '0')
                return false;
    return true;
}
void sdk_board::clear()
{
    board.clear();
}
std::vector<size_t> get_base(const size_t r, const size_t c)
{
    std::vector<size_t> rc;
    rc.push_back(r/3*3);
    rc.push_back(c/3*3);
    return rc;
}
