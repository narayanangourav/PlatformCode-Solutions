# Java Substring Comparisons

<!-- synced-problem-statement -->

We define the following terms:

- [Lexicographical Order](https://en.wikipedia.org/wiki/Lexicographical_order), also known as *alphabetic* or *dictionary* order, orders characters as follows:		
	$$\texttt{A} \lt \texttt{B} \lt \ldots \lt \texttt{Y} \lt \texttt{Z} \lt \texttt{a} \lt \texttt{b} \lt \ldots \lt \texttt{y} \lt \texttt{z}$$ 
    
    For example, `ball < cat`, `dog < dorm`, `Happy < happy`, `Zoo < ball`.
- A [substring](https://en.wikipedia.org/wiki/Substring) of a string is a contiguous block of characters in the string. For example, the substrings of `abc` are `a`, `b`, `c`, `ab`, `bc`, and `abc`.

Given a string, $s$, and an integer, $k$, complete the function so that it finds the lexicographically *smallest* and *largest* substrings of length $k$.   

**Function Description**   

Complete the *getSmallestAndLargest* function in the editor below.   

*getSmallestAndLargest* has the following parameters:   

- *string s:* a string  
- *int k:* the length of the substrings to find   

**Returns**  

- *string:* the string '<smallest> + "\n" + <largest>' where <smallest> and <largest> are the two substrings

Source: https://www.hackerrank.com/challenges/java-string-compare/problem
