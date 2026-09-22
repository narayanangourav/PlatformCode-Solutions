import java.io.*;
import java.util.*;
import java.text.*;
import java.math.*;
import java.util.regex.*;

public class Solution {

    public static void main(String[] args) {
        /* Enter your code here. Read input from STDIN. Print output to STDOUT. Your class should be named Solution. */
        Scanner line=new Scanner(System.in);
        int counter = 1;
        while (line.hasNextLine()) {
            String a = line.nextLine();

            System.out.println(counter + " " + a);
            counter++;
        }
    }
}
