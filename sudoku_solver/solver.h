#ifndef SOLVER__H
#define SOLVER__H
#include <string>
#include <vector>
#include "cell.h"
#include "variable.h"
#include "sdk_board.h"
class solver
{
    public:
        solver();
        ~solver();
        void set_board(const std::string& config);
        char get_value(const size_t r, const size_t c)const;
        char get_value(const size_t idx)const;  
        bool solve();
        bool backtrack(sdk_board& brd);
        std::string fwd_check(const variable& var, sdk_board& brd);
        void clear();
    private:
        sdk_board board;
};
std::vector<size_t> get_rc(const variable& var);
#endif
