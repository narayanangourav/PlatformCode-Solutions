import java.io.*;
import java.util.*;

public class Solution {

    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        String s = scan.nextLine();
        if (s.trim().equals("")){
            System.out.println(0);
            return;
        }
        String[] strings = s.trim().split("[\\s!,?._'@]+");
        System.out.println(strings.length);
        for(String i: strings){
            System.out.println(i);
        }
        // Write your code here.
        scan.close();
    }
}
