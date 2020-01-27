#ifndef SDK_BOARD__H
#define SDK_BOARD__H
#include <vector>
#include <string>
#include <cassert>
#include "cell.h"
#include "variable.h"
class sdk_board
{
    public:
        typedef std::vector<std::vector<cell>> vect;
        static const size_t ROW;
        static const size_t COL;
        static const std::string ROWS;
        static const std::string COLS;
        sdk_board();
        sdk_board(const sdk_board& board_in);
        std::vector<cell>& operator[](const size_t idx);
        char get_value(const size_t r, const size_t c)const;
        char get_value(const size_t idx)const;
        void set(const std::string& config);
        variable get_domain(const size_t row, const size_t col)const;
        variable MRV()const;
        bool complete()const;
        void clear();
    private:
        vect board;
};
std::vector<size_t> get_base(const size_t r, const size_t c);
#endif
