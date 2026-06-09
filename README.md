Some quick calculation

So if we have an $nxn$ word search, we need to search $n$ rows, $n$ columns, and about $n$ left diagonal and $n$ right diagonal (upperbound).

So we have to search $4n$ "lines".

Every line requires about $1 + 2 + \cdots + n \leq n^2$

So basically, we need to search $4 \times n \times n^2 = 4n^3$.
