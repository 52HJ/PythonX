from typing import List


class Solution:
    def getRow(self, rowIndex: int) -> List[int]:
        """

        1
        不使用错位相加，手动实现

        2
        错位相加，不使用 map 也可以使用 zip

        3
        错位相加的手动实现
        >>> Solution().getRow(4)
        [1, 4, 6, 4, 1]
        """
        row = [1]
        for _ in range(rowIndex):
            # 在最后添加 1
            row.append(1)
            # 从倒数 -2 位置到 1 位置
            for i in range(len(row) - 2, 0, -1):
                row[i] += row[i - 1]
        return row


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)
